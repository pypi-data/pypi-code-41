# Copyright 2019 The TensorFlow Probability Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""No U-Turn Sampler.

The implementation closely follows [1; Algorithm 3], with Multinomial sampling
on the tree instead of slice sampling.

Achieves batch execution across chains by precomputing the recursive tree
doubling data access patterns and then executes this "unrolled" data pattern via
a `tf.while_loop`.

#### References

[1]: Matthew D. Hoffman, Andrew Gelman. The No-U-Turn Sampler: Adaptively
     Setting Path Lengths in Hamiltonian Monte Carlo.
     In _Journal of Machine Learning Research_, 15(1):1593-1623, 2014.
     http://jmlr.org/papers/volume15/hoffman14a/hoffman14a.pdf
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import numpy as np

import tensorflow.compat.v2 as tf

from tensorflow_probability.python.distributions.seed_stream import SeedStream
from tensorflow_probability.python.internal import prefer_static
from tensorflow_probability.python.math.generic import log_add_exp
from tensorflow_probability.python.mcmc.internal import leapfrog_integrator as leapfrog_impl
from tensorflow_probability.python.mcmc.kernel import TransitionKernel

##############################################################
### BEGIN STATIC CONFIGURATION ###############################
##############################################################
TF_WHILE_PARALLEL_ITERATIONS = 10     # Default: 10

TREE_COUNT_DTYPE = tf.int32           # Default: tf.int32

# Whether to use slice sampling (original NUTS implementation) or multinomial
# sampling from the tree trajectory.
MULTINOMIAL_SAMPLE = True             # Default: True
##############################################################
### END STATIC CONFIGURATION #################################
##############################################################

__all__ = [
    'NoUTurnSampler',
]

NUTSKernelResults = collections.namedtuple('NUTSKernelResults', [
    'target_log_prob',
    'grads_target_log_prob',
    'momentum_state_memory',
    'step_size',
    'log_accept_ratio',
    'leapfrogs_taken',
    'is_accepted',
    'reach_max_depth',
    'has_divergence',
])

MomentumStateSwap = collections.namedtuple('MomentumStateSwap', [
    'momentum_swap',
    'state_swap',
])

OneStepMetaInfo = collections.namedtuple('OneStepMetaInfo', [
    'log_slice_sample',
    'init_energy',
    'write_instruction',
    'read_instruction',
])

TreeDoublingState = collections.namedtuple('TreeDoublingState', [
    'momentum',
    'state',
    'target',
    'target_grad_parts',
])

TreeDoublingStateCandidate = collections.namedtuple(
    'TreeDoublingStateCandidate', [
        'state',
        'target',
        'target_grad_parts',
        'weight',
    ])

TreeDoublingMetaState = collections.namedtuple(
    'TreeDoublingMetaState',
    [
        'candidate_state',  # A namedtuple of TreeDoublingStateCandidate
        'is_accepted',
        'energy_diff_sum',  # sum of the energy differences (H' - H0) within the
                            # single subtree
        'leapfrog_count',
        'continue_tree',
        'not_divergence',
    ])


class NoUTurnSampler(TransitionKernel):
  """Runs one step of the No U-Turn Sampler.

  The No U-Turn Sampler (NUTS) is an adaptive variant of the Hamiltonian Monte
  Carlo (HMC) method for MCMC.  NUTS adapts the distance traveled in response to
  the curvature of the target density.  Conceptually, one proposal consists of
  reversibly evolving a trajectory through the sample space, continuing until
  that trajectory turns back on itself (hence the name, 'No U-Turn').  This
  class implements one random NUTS step from a given
  `current_state`.  Mathematical details and derivations can be found in
  [Hoffman, Gelman (2011)][1].

  The `one_step` function can update multiple chains in parallel. It assumes
  that a prefix of leftmost dimensions of `current_state` index independent
  chain states (and are therefore updated independently).  The output of
  `target_log_prob_fn(*current_state)` should sum log-probabilities across all
  event dimensions.  Slices along the rightmost dimensions may have different
  target distributions; for example, `current_state[0][0, ...]` could have a
  different target distribution from `current_state[0][1, ...]`.  These
  semantics are governed by `target_log_prob_fn(*current_state)`. (The number of
  independent chains is `tf.size(target_log_prob_fn(*current_state))`.)

  #### References

  [1] Matthew D. Hoffman, Andrew Gelman.  The No-U-Turn Sampler: Adaptively
  Setting Path Lengths in Hamiltonian Monte Carlo.  2011.
  https://arxiv.org/pdf/1111.4246.pdf.
  """

  def __init__(self,
               target_log_prob_fn,
               step_size,
               max_tree_depth=10,
               max_energy_diff=1000.,
               unrolled_leapfrog_steps=1,
               seed=None,
               name=None):
    """Initializes this transition kernel.

    Args:
      target_log_prob_fn: Python callable which takes an argument like
        `current_state` (or `*current_state` if it's a list) and returns its
        (possibly unnormalized) log-density under the target distribution.
      step_size: `Tensor` or Python `list` of `Tensor`s representing the step
        size for the leapfrog integrator. Must broadcast with the shape of
        `current_state`. Larger step sizes lead to faster progress, but
        too-large step sizes make rejection exponentially more likely. When
        possible, it's often helpful to match per-variable step sizes to the
        standard deviations of the target distribution in each variable.
      max_tree_depth: Maximum depth of the tree implicitly built by NUTS. The
        maximum number of leapfrog steps is bounded by `2**max_tree_depth` i.e.
        the number of nodes in a binary tree `max_tree_depth` nodes deep. The
        default setting of 10 takes up to 1024 leapfrog steps.
      max_energy_diff: Scaler threshold of energy differences at each leapfrog,
        divergence samples are defined as leapfrog steps that exceed this
        threshold. Default to 1000.
      unrolled_leapfrog_steps: The number of leapfrogs to unroll per tree
        expansion step. Applies a direct linear multipler to the maximum
        trajectory length implied by max_tree_depth. Defaults to 1.
      seed: Python integer to seed the random number generator.
      name: Python `str` name prefixed to Ops created by this function.
        Default value: `None` (i.e., 'nuts_kernel').
    """
    with tf.name_scope(name or 'NoUTurnSampler') as name:
      # Process `max_tree_depth` argument.
      max_tree_depth = tf.get_static_value(max_tree_depth)
      if max_tree_depth is None or max_tree_depth < 1:
        raise ValueError(
            'max_tree_depth must be known statically and >= 1 but was '
            '{}'.format(max_tree_depth))
      self._max_tree_depth = max_tree_depth

      # Compute parameters derived from `max_tree_depth`.
      instruction_array = build_tree_uturn_instruction(
          max_tree_depth, init_memory=-1)
      [
          write_instruction_numpy,
          read_instruction_numpy
      ] = generate_efficient_write_read_instruction(instruction_array)

      # TensorArray version of the read/write instruction need to be created
      # within the function call to be compatible with XLA. Here we store the
      # numpy version of the instruction and convert it to TensorArray later.
      self._write_instruction = write_instruction_numpy
      self._read_instruction = read_instruction_numpy

      # Process all other arguments.
      self._target_log_prob_fn = target_log_prob_fn
      if not tf.nest.is_nested(step_size):
        step_size = [step_size]
      step_size = [
          tf.convert_to_tensor(s, dtype_hint=tf.float32) for s in step_size
      ]
      self._step_size = step_size

      self._parameters = dict(
          target_log_prob_fn=target_log_prob_fn,
          step_size=step_size,
          max_tree_depth=max_tree_depth,
          max_energy_diff=max_energy_diff,
          unrolled_leapfrog_steps=unrolled_leapfrog_steps,
          seed=seed,
          name=name,
      )
      self._seed_stream = SeedStream(seed, salt='nuts_one_step')
      self._unrolled_leapfrog_steps = unrolled_leapfrog_steps
      self._name = name
      self._max_energy_diff = max_energy_diff

  @property
  def target_log_prob_fn(self):
    return self._target_log_prob_fn

  @property
  def step_size(self):
    return self._step_size

  @property
  def max_tree_depth(self):
    return self._max_tree_depth

  @property
  def max_energy_diff(self):
    return self._max_energy_diff

  @property
  def unrolled_leapfrog_steps(self):
    return self._unrolled_leapfrog_steps

  @property
  def name(self):
    return self._name

  @property
  def write_instruction(self):
    return self._write_instruction

  @property
  def read_instruction(self):
    return self._read_instruction

  @property
  def parameters(self):
    return self._parameters

  @property
  def is_calibrated(self):
    return True

  def one_step(self, current_state, previous_kernel_results):
    with tf.name_scope(self.name + '.one_step'):
      unwrap_state_list = not tf.nest.is_nested(current_state)
      if unwrap_state_list:
        current_state = [current_state]

      current_target_log_prob = previous_kernel_results.target_log_prob
      [
          init_momentum,
          init_energy,
          log_slice_sample
      ] = self._start_trajectory_batched(current_state, current_target_log_prob)

      def _copy(v):
        return v * prefer_static.ones(
            prefer_static.pad(
                [2], paddings=[[0, prefer_static.rank(v)]], constant_values=1),
            dtype=v.dtype)

      initial_state = TreeDoublingState(
          momentum=init_momentum,
          state=current_state,
          target=current_target_log_prob,
          target_grad_parts=previous_kernel_results.grads_target_log_prob)
      initial_step_state = tf.nest.map_structure(_copy, initial_state)

      if MULTINOMIAL_SAMPLE:
        init_weight = tf.zeros_like(init_energy)
      else:
        init_weight = tf.ones_like(init_energy, dtype=TREE_COUNT_DTYPE)

      candidate_state = TreeDoublingStateCandidate(
          state=current_state,
          target=current_target_log_prob,
          target_grad_parts=previous_kernel_results.grads_target_log_prob,
          weight=init_weight)

      initial_step_metastate = TreeDoublingMetaState(
          candidate_state=candidate_state,
          is_accepted=tf.zeros_like(init_energy, dtype=tf.bool),
          energy_diff_sum=tf.zeros_like(init_energy),
          leapfrog_count=tf.zeros_like(init_energy, dtype=TREE_COUNT_DTYPE),
          continue_tree=tf.ones_like(init_energy, dtype=tf.bool),
          not_divergence=tf.ones_like(init_energy, dtype=tf.bool))

      # Convert the write/read instruction into TensorArray so that it is
      # compatible with XLA.
      write_instruction = tf.TensorArray(
          TREE_COUNT_DTYPE,
          size=2**(self.max_tree_depth - 1),
          clear_after_read=False).unstack(self._write_instruction)
      read_instruction = tf.TensorArray(
          tf.int32,
          size=2**(self.max_tree_depth-1),
          clear_after_read=False).unstack(self._read_instruction)

      current_step_meta_info = OneStepMetaInfo(
          log_slice_sample=log_slice_sample,
          init_energy=init_energy,
          write_instruction=write_instruction,
          read_instruction=read_instruction
          )

      _, _, new_step_metastate = tf.while_loop(
          cond=lambda iter_, state, metastate: (  # pylint: disable=g-long-lambda
              ((iter_ < self.max_tree_depth) &
               tf.reduce_any(metastate.continue_tree))),
          body=lambda iter_, state, metastate: self.loop_tree_doubling(  # pylint: disable=g-long-lambda
              previous_kernel_results.step_size,
              previous_kernel_results.momentum_state_memory,
              current_step_meta_info,
              iter_,
              state,
              metastate),
          loop_vars=(
              tf.zeros([], dtype=tf.int32, name='iter'),
              initial_step_state,
              initial_step_metastate),
          parallel_iterations=TF_WHILE_PARALLEL_ITERATIONS,
      )

      kernel_results = NUTSKernelResults(
          target_log_prob=new_step_metastate.candidate_state.target,
          grads_target_log_prob=(
              new_step_metastate.candidate_state.target_grad_parts),
          momentum_state_memory=previous_kernel_results.momentum_state_memory,
          step_size=previous_kernel_results.step_size,
          log_accept_ratio=tf.math.log(
              new_step_metastate.energy_diff_sum /
              tf.cast(new_step_metastate.leapfrog_count,
                      dtype=new_step_metastate.energy_diff_sum.dtype)),
          # TODO(junpenglao): return non-cumulated leapfrogs_taken once
          # benchmarking is done.
          leapfrogs_taken=(
              previous_kernel_results.leapfrogs_taken +
              new_step_metastate.leapfrog_count * self.unrolled_leapfrog_steps
          ),
          is_accepted=new_step_metastate.is_accepted,
          reach_max_depth=new_step_metastate.continue_tree,
          has_divergence=~new_step_metastate.not_divergence,
      )

      result_state = new_step_metastate.candidate_state.state
      if unwrap_state_list:
        result_state = result_state[0]

      return result_state, kernel_results

  def bootstrap_results(self, init_state):
    """Creates initial `previous_kernel_results` using a supplied `state`."""
    with tf.name_scope(self.name + '.bootstrap_results'):
      if not tf.nest.is_nested(init_state):
        init_state = [init_state]
      # Padding the step_size so it is compatable with the states
      step_size = self.step_size
      if len(step_size) == 1:
        step_size = step_size * len(init_state)
      if len(step_size) != len(init_state):
        raise ValueError('Expected either one step size or {} (size of '
                         '`init_state`), but found {}'.format(
                             len(init_state), len(step_size)))

      dummy_momentum = [tf.ones_like(state) for state in init_state]

      def _init(shape_and_dtype):
        """Allocate TensorArray for storing state and momentum."""
        return [  # pylint: disable=g-complex-comprehension
            tf.zeros(
                tf.TensorShape([self.max_tree_depth + 1]).concatenate(s),
                dtype=d) for (s, d) in shape_and_dtype
        ]

      get_shapes_and_dtypes = lambda x: [(x_.shape, x_.dtype) for x_ in x]
      momentum_state_memory = MomentumStateSwap(
          momentum_swap=_init(get_shapes_and_dtypes(dummy_momentum)),
          state_swap=_init(get_shapes_and_dtypes(init_state)))
      [
          _,
          _,
          current_target_log_prob,
          current_grads_log_prob,
      ] = leapfrog_impl.process_args(self.target_log_prob_fn, dummy_momentum,
                                     init_state)

      return NUTSKernelResults(
          target_log_prob=current_target_log_prob,
          grads_target_log_prob=current_grads_log_prob,
          momentum_state_memory=momentum_state_memory,
          step_size=step_size,
          log_accept_ratio=tf.zeros_like(current_target_log_prob,
                                         name='log_accept_ratio'),
          leapfrogs_taken=tf.zeros_like(current_target_log_prob,
                                        dtype=TREE_COUNT_DTYPE,
                                        name='leapfrogs_taken'),
          is_accepted=tf.zeros_like(current_target_log_prob,
                                    dtype=tf.bool,
                                    name='is_accepted'),
          reach_max_depth=tf.zeros_like(current_target_log_prob,
                                        dtype=tf.bool,
                                        name='reach_max_depth'),
          has_divergence=tf.zeros_like(current_target_log_prob,
                                       dtype=tf.bool,
                                       name='has_divergence'),
      )

  def _start_trajectory_batched(self, state, target_log_prob):
    """Computations needed to start a trajectory."""
    with tf.name_scope('start_trajectory_batched'):
      seed_stream = SeedStream(
          self._seed_stream, salt='start_trajectory_batched')
      momentum = [
          tf.random.normal(  # pylint: disable=g-complex-comprehension
              shape=prefer_static.shape(x),
              dtype=x.dtype,
              seed=seed_stream()) for x in state
      ]
      init_energy = compute_hamiltonian(target_log_prob, momentum)

      if MULTINOMIAL_SAMPLE:
        return momentum, init_energy, None

      # Draw a slice variable u ~ Uniform(0, p(initial state, initial
      # momentum)) and compute log u. For numerical stability, we perform this
      # in log space where log u = log (u' * p(...)) = log u' + log
      # p(...) and u' ~ Uniform(0, 1).
      log_slice_sample = tf.math.log1p(-tf.random.uniform(
          shape=prefer_static.shape(init_energy),
          dtype=init_energy.dtype,
          seed=seed_stream()))
      return momentum, init_energy, log_slice_sample

  def loop_tree_doubling(self, step_size, momentum_state_memory,
                         current_step_meta_info, iter_, initial_step_state,
                         initial_step_metastate):
    """Main loop for tree doubling."""
    with tf.name_scope('loop_tree_doubling'):
      batch_shape = prefer_static.shape(current_step_meta_info.init_energy)
      direction = tf.cast(
          tf.random.uniform(
              shape=batch_shape,
              minval=0,
              maxval=2,
              dtype=tf.int32,
              seed=self._seed_stream()),
          dtype=tf.bool)

      tree_start_states = tf.nest.map_structure(
          lambda v: tf.where(  # pylint: disable=g-long-lambda
              _rightmost_expand_to_rank(direction, prefer_static.rank(v[1])),
              v[1], v[0]),
          initial_step_state)

      directions_expanded = [
          _rightmost_expand_to_rank(
              direction, prefer_static.rank(state))
          for state in tree_start_states.state
      ]

      integrator = leapfrog_impl.SimpleLeapfrogIntegrator(
          self.target_log_prob_fn,
          step_sizes=[
              tf.where(d, ss, -ss)
              for d, ss in zip(directions_expanded, step_size)
          ],
          num_steps=self.unrolled_leapfrog_steps)

      [
          candidate_tree_state,
          tree_final_states,
          final_not_divergence,
          continue_tree_final,
          energy_diff_tree_sum,
          leapfrogs_taken,
      ] = self._build_sub_tree(
          directions_expanded,
          integrator,
          current_step_meta_info,
          # num_steps_at_this_depth = 2**iter_ = 1 << iter_
          tf.bitwise.left_shift(1, iter_),
          tree_start_states,
          initial_step_metastate.continue_tree,
          initial_step_metastate.not_divergence,
          momentum_state_memory)

      last_candidate_state = initial_step_metastate.candidate_state
      tree_weight = candidate_tree_state.weight
      if MULTINOMIAL_SAMPLE:
        weight_sum = log_add_exp(tree_weight, last_candidate_state.weight)
        log_accept_thresh = tree_weight - last_candidate_state.weight
      else:
        weight_sum = tree_weight + last_candidate_state.weight
        log_accept_thresh = tf.math.log(
            tf.cast(tree_weight, tf.float32) /
            tf.cast(last_candidate_state.weight, tf.float32))
      log_accept_thresh = tf.where(
          tf.math.is_nan(log_accept_thresh),
          tf.zeros([], log_accept_thresh.dtype),
          log_accept_thresh)
      u = tf.math.log1p(-tf.random.uniform(
          shape=batch_shape,
          dtype=log_accept_thresh.dtype,
          seed=self._seed_stream()))
      is_sample_accepted = u <= log_accept_thresh

      choose_new_state = is_sample_accepted & continue_tree_final

      new_candidate_state = TreeDoublingStateCandidate(
          state=[
              tf.where(  # pylint: disable=g-complex-comprehension
                  _rightmost_expand_to_rank(
                      choose_new_state, prefer_static.rank(s0)), s0, s1)
              for s0, s1 in zip(candidate_tree_state.state,
                                last_candidate_state.state)
          ],
          target=tf.where(
              _rightmost_expand_to_rank(
                  choose_new_state,
                  prefer_static.rank(candidate_tree_state.target)),
              candidate_tree_state.target, last_candidate_state.target),
          target_grad_parts=[
              tf.where(  # pylint: disable=g-complex-comprehension
                  _rightmost_expand_to_rank(
                      choose_new_state, prefer_static.rank(grad0)),
                  grad0, grad1)
              for grad0, grad1 in zip(candidate_tree_state.target_grad_parts,
                                      last_candidate_state.target_grad_parts)
          ],
          weight=weight_sum)

      # Update left right information of the trajectory, and check trajectory
      # level U turn
      tree_otherend_states = tf.nest.map_structure(
          lambda v: tf.where(  # pylint: disable=g-long-lambda
              _rightmost_expand_to_rank(direction, prefer_static.rank(v[1])),
              v[0], v[1]), initial_step_state)

      new_step_state = tf.nest.pack_sequence_as(initial_step_state, [
          tf.stack([  # pylint: disable=g-complex-comprehension
              tf.where(
                  _rightmost_expand_to_rank(direction, prefer_static.rank(l)),
                  r, l),
              tf.where(
                  _rightmost_expand_to_rank(direction, prefer_static.rank(l)),
                  l, r),
          ], axis=0)
          for l, r in zip(tf.nest.flatten(tree_final_states),
                          tf.nest.flatten(tree_otherend_states))
      ])
      no_u_turns_trajectory = has_not_u_turn(
          [s[0] for s in new_step_state.state],
          [m[0] for m in new_step_state.momentum],
          [s[1] for s in new_step_state.state],
          [m[1] for m in new_step_state.momentum],
          log_prob_rank=len(batch_shape))

      new_step_metastate = TreeDoublingMetaState(
          candidate_state=new_candidate_state,
          is_accepted=choose_new_state | initial_step_metastate.is_accepted,
          energy_diff_sum=(
              energy_diff_tree_sum + initial_step_metastate.energy_diff_sum),
          continue_tree=continue_tree_final & no_u_turns_trajectory,
          not_divergence=final_not_divergence,
          leapfrog_count=(initial_step_metastate.leapfrog_count +
                          leapfrogs_taken))

      return iter_ + 1, new_step_state, new_step_metastate

  def _build_sub_tree(self,
                      directions,
                      integrator,
                      current_step_meta_info,
                      nsteps,
                      initial_state,
                      continue_tree,
                      not_divergence,
                      momentum_state_memory,
                      name=None):
    with tf.name_scope('build_sub_tree'):
      batch_shape = prefer_static.shape(current_step_meta_info.init_energy)
      # We never want to select the inital state
      if MULTINOMIAL_SAMPLE:
        init_weight = tf.fill(
            batch_shape,
            tf.constant(-np.inf,
                        dtype=current_step_meta_info.init_energy.dtype))
      else:
        init_weight = tf.zeros(batch_shape, dtype=TREE_COUNT_DTYPE)
      initial_state_candidate = TreeDoublingStateCandidate(
          state=initial_state.state,
          target=initial_state.target,
          target_grad_parts=initial_state.target_grad_parts,
          weight=init_weight)
      energy_diff_sum = tf.zeros_like(current_step_meta_info.init_energy,
                                      name='energy_diff_sum')
      [
          _,
          energy_diff_tree_sum,
          leapfrogs_taken,
          final_state,
          candidate_tree_state,
          final_continue_tree,
          final_not_divergence,
          momentum_state_memory,
      ] = tf.while_loop(
          cond=lambda iter_, energy_diff_sum, leapfrogs_taken, state, state_c,  # pylint: disable=g-long-lambda
                      continue_tree, not_divergence, momentum_state_memory: (
                          (iter_ < nsteps) & tf.reduce_any(continue_tree)),
          body=lambda iter_, energy_diff_sum, leapfrogs_taken, state, state_c,  # pylint: disable=g-long-lambda
                      continue_tree, not_divergence, momentum_state_memory: (
                          self._loop_build_sub_tree(
                              directions, integrator, current_step_meta_info,
                              iter_, energy_diff_sum, leapfrogs_taken, state,
                              state_c, continue_tree, not_divergence,
                              momentum_state_memory)),
          loop_vars=(
              tf.zeros([], dtype=tf.int32, name='iter'),
              energy_diff_sum,
              tf.zeros(batch_shape, dtype=TREE_COUNT_DTYPE),
              initial_state,
              initial_state_candidate,
              continue_tree,
              not_divergence,
              momentum_state_memory,
          ),
          parallel_iterations=TF_WHILE_PARALLEL_ITERATIONS,
      )

    return (
        candidate_tree_state,
        final_state,
        final_not_divergence,
        final_continue_tree,
        energy_diff_tree_sum,
        leapfrogs_taken,
    )

  def _loop_build_sub_tree(self,
                           directions,
                           integrator,
                           current_step_meta_info,
                           iter_,
                           energy_diff_sum_previous,
                           leapfrogs_taken,
                           prev_tree_state,
                           candidate_tree_state,
                           continue_tree_previous,
                           not_divergent_previous,
                           momentum_state_memory):
    """Base case in tree doubling."""
    with tf.name_scope('loop_build_sub_tree'):
      # Take one leapfrog step in the direction v and check divergence
      [
          next_momentum_parts,
          next_state_parts,
          next_target,
          next_target_grad_parts
      ] = integrator(prev_tree_state.momentum,
                     prev_tree_state.state,
                     prev_tree_state.target,
                     prev_tree_state.target_grad_parts)

      next_tree_state = TreeDoublingState(
          momentum=next_momentum_parts,
          state=next_state_parts,
          target=next_target,
          target_grad_parts=next_target_grad_parts)
      # If the tree have not yet terminated previously, we count this leapfrog.
      leapfrogs_taken = tf.where(
          continue_tree_previous, leapfrogs_taken + 1, leapfrogs_taken)

      write_instruction = current_step_meta_info.write_instruction
      read_instruction = current_step_meta_info.read_instruction
      init_energy = current_step_meta_info.init_energy

      # Save state and momentum at odd step, check U turn at even step.
      # Note that here we also write to a Placeholder at even step
      write_index = tf.where(
          tf.equal(iter_ % 2, 0),
          write_instruction.gather([iter_ // 2]),
          self.max_tree_depth)

      momentum_state_memory = MomentumStateSwap(
          momentum_swap=[
              tf.tensor_scatter_nd_update(old, [write_index], [new])
              for old, new in zip(momentum_state_memory.momentum_swap,
                                  next_momentum_parts)
          ],
          state_swap=[
              tf.tensor_scatter_nd_update(old, [write_index], [new])
              for old, new in zip(momentum_state_memory.state_swap,
                                  next_state_parts)
          ])
      batch_shape = prefer_static.shape(next_target)
      has_not_u_turn_at_even_step = tf.ones(batch_shape, dtype=tf.bool)

      read_index = read_instruction.gather([iter_ // 2])[0]
      no_u_turns_within_tree = tf.cond(
          tf.equal(iter_ % 2, 0),
          lambda: has_not_u_turn_at_even_step,
          lambda: has_not_u_turn_at_odd_step(  # pylint: disable=g-long-lambda
              read_index, directions, momentum_state_memory,
              next_momentum_parts, next_state_parts,
              has_not_u_turn_at_even_step,
              log_prob_rank=prefer_static.rank(next_target)))

      energy = compute_hamiltonian(next_target, next_momentum_parts)
      energy = tf.where(tf.math.is_nan(energy),
                        tf.constant(-np.inf, dtype=energy.dtype),
                        energy)
      energy_diff = energy - init_energy

      if MULTINOMIAL_SAMPLE:
        not_divergent = -energy_diff < self.max_energy_diff
        weight_sum = log_add_exp(candidate_tree_state.weight, energy_diff)
        log_accept_thresh = energy_diff - weight_sum
      else:
        log_slice_sample = current_step_meta_info.log_slice_sample
        not_divergent = log_slice_sample - energy_diff < self.max_energy_diff
        # Uniform sampling on the trajectory within the subtree across valid
        # samples.
        is_valid = log_slice_sample <= energy_diff
        weight_sum = tf.where(is_valid,
                              candidate_tree_state.weight + 1,
                              candidate_tree_state.weight)
        log_accept_thresh = tf.where(
            is_valid,
            -tf.math.log(tf.cast(weight_sum, dtype=tf.float32)),
            tf.constant(-np.inf, dtype=tf.float32))
      u = tf.math.log1p(-tf.random.uniform(
          shape=batch_shape,
          dtype=log_accept_thresh.dtype,
          seed=self._seed_stream()))
      is_sample_accepted = u <= log_accept_thresh

      next_candidate_tree_state = TreeDoublingStateCandidate(
          state=[
              tf.where(  # pylint: disable=g-complex-comprehension
                  _rightmost_expand_to_rank(is_sample_accepted,
                                            prefer_static.rank(s0)),
                  s0, s1)
              for s0, s1 in zip(next_state_parts, candidate_tree_state.state)
          ],
          target=tf.where(
              _rightmost_expand_to_rank(is_sample_accepted,
                                        prefer_static.rank(next_target)),
              next_target, candidate_tree_state.target),
          target_grad_parts=[
              tf.where(  # pylint: disable=g-complex-comprehension
                  _rightmost_expand_to_rank(is_sample_accepted,
                                            prefer_static.rank(grad0)),
                  grad0, grad1)
              for grad0, grad1 in zip(next_target_grad_parts,
                                      candidate_tree_state.target_grad_parts)
          ],
          weight=weight_sum)

      continue_tree = not_divergent & continue_tree_previous
      continue_tree_next = no_u_turns_within_tree & continue_tree

      not_divergent_tokeep = tf.where(continue_tree_previous,
                                      not_divergent,
                                      tf.ones(batch_shape, dtype=tf.bool))

      # min(1., exp(energy_diff)).
      exp_energy_diff = tf.clip_by_value(tf.exp(energy_diff), 0., 1.)
      energy_diff_sum = tf.where(continue_tree,
                                 energy_diff_sum_previous + exp_energy_diff,
                                 energy_diff_sum_previous)

      return (
          iter_ + 1,
          energy_diff_sum,
          leapfrogs_taken,
          next_tree_state,
          next_candidate_tree_state,
          continue_tree_next,
          not_divergent_previous & not_divergent_tokeep,
          momentum_state_memory,
      )


def has_not_u_turn_at_odd_step(read_indexes, direction, momentum_state_memory,
                               momentum_right, state_right,
                               no_u_turns_within_tree, log_prob_rank):
  """Check u turn for early stopping."""

  def _get_left_state_and_check_u_turn(left_current_index, no_u_turns_last):
    """Check U turn on a single index."""
    momentum_left = [
        tf.gather(x, left_current_index, axis=0)
        for x in momentum_state_memory.momentum_swap
    ]
    state_left = [
        tf.gather(x, left_current_index, axis=0)
        for x in momentum_state_memory.state_swap
    ]

    no_u_turns_current = has_not_u_turn(
        state_left,
        [tf.where(d, m, -m) for d, m in zip(direction, momentum_left)],
        state_right,
        [tf.where(d, m, -m) for d, m in zip(direction, momentum_right)],
        log_prob_rank)
    return left_current_index + 1, no_u_turns_current & no_u_turns_last

  _, no_u_turns_within_tree = tf.while_loop(
      cond=lambda i, no_u_turn: i < tf.gather(read_indexes, 1),
      body=_get_left_state_and_check_u_turn,
      loop_vars=(tf.gather(read_indexes, 0), no_u_turns_within_tree),
      parallel_iterations=TF_WHILE_PARALLEL_ITERATIONS)
  return no_u_turns_within_tree


def has_not_u_turn(state_left,
                   momentum_left,
                   state_right,
                   momentum_right,
                   log_prob_rank):
  """If two given states and momentum do not exhibit a U-turn pattern."""
  with tf.name_scope('has_not_u_turn'):
    batch_dot_product_left = sum([
        tf.reduce_sum(  # pylint: disable=g-complex-comprehension
            (s1 - s2) * m,
            axis=tf.range(log_prob_rank, prefer_static.rank(m)))
        for s1, s2, m in zip(state_right, state_left, momentum_left)
    ])
    batch_dot_product_right = sum([
        tf.reduce_sum(  # pylint: disable=g-complex-comprehension
            (s1 - s2) * m,
            axis=tf.range(log_prob_rank, prefer_static.rank(m)))
        for s1, s2, m in zip(state_right, state_left, momentum_right)
    ])
    return (batch_dot_product_left >= 0) & (batch_dot_product_right >= 0)


def _rightmost_expand_to_rank(tensor, new_rank):
  """Expands `tensor`'s rank by `new_rank - tensor.rank` rightmost dims."""
  return tf.reshape(
      tensor,
      shape=prefer_static.pad(
          prefer_static.shape(tensor),
          paddings=[[0, max(0, new_rank - prefer_static.rank(tensor))]],
          constant_values=1))


def build_tree_uturn_instruction(max_depth, init_memory=0):
  """Run build tree and output the u turn checking input instruction."""

  def _buildtree(address, depth):
    if depth == 0:
      address += 1
      return address, address
    else:
      address_left, address_right = _buildtree(address, depth - 1)
      _, address_right = _buildtree(address_right, depth - 1)
      instruction.append((address_left, address_right))
      return address_left, address_right

  instruction = []
  _, _ = _buildtree(init_memory, max_depth)
  return np.array(instruction, dtype=np.int32)


def generate_efficient_write_read_instruction(instruction_array):
  """Statically generate a memory efficient write/read instruction."""
  nsteps_within_tree = np.max(instruction_array) + 1
  instruction_mat = np.zeros((nsteps_within_tree, nsteps_within_tree))
  for previous_step, current_step in instruction_array:
    instruction_mat[previous_step, current_step] = 1
  instruction_mat_cumsum = np.cumsum(instruction_mat, axis=1)
  max_to_retain = instruction_mat_cumsum[:, -1][..., np.newaxis]

  # Generate a sparse matrix that represents the memory footprint:
  #   -1 : no need to save to memory (these are odd steps)
  #    1 : needed for check u turn (either already in memory or will be saved)
  #    0 : still in memory but not needed for check u turn
  instruction_mat2 = np.zeros(instruction_mat.shape)
  instruction_mat2[instruction_mat == 0] = -1
  instruction_mat2[(instruction_mat_cumsum < max_to_retain)
                   & (instruction_mat_cumsum > 0)] = 0
  instruction_mat2[instruction_mat == 1] = 1
  np.fill_diagonal(instruction_mat2, (max_to_retain > 0) - 1)
  # plt.imshow(instruction_mat2, interpolation='None')

  # Note that we only write at even step. Oberserved that this is actually
  # squence A000120 (https://oeis.org/A000120)
  write_instruction = np.sum(
      instruction_mat2 > -1, axis=0)[range(0, nsteps_within_tree, 2)] - 1
  # Note that we only read at odd step.
  read_instruction = []
  for i in range(nsteps_within_tree):
    temp_instruction = instruction_mat2[:, i]
    if np.sum(temp_instruction == 1) > 0:
      r = np.where(temp_instruction[temp_instruction >= 0] == 1)[0][0]
      read_instruction.append([r, r + np.sum(temp_instruction == 1)])
  return write_instruction, np.asarray(read_instruction)


def compute_hamiltonian(target_log_prob, momentum_parts):
  """Compute the Hamiltonian of the current system."""
  independent_chain_ndims = prefer_static.rank(target_log_prob)
  momentum_sq_parts = (
      tf.cast(  # pylint: disable=g-complex-comprehension
          tf.reduce_sum(
              tf.square(m),
              axis=prefer_static.range(independent_chain_ndims,
                                       prefer_static.rank(m))),
          dtype=target_log_prob.dtype) for m in momentum_parts)
  # TODO(jvdillon): Verify no broadcasting happening.
  return target_log_prob - 0.5 * sum(momentum_sq_parts)
