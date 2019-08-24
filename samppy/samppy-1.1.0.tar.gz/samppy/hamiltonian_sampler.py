"""Implementation of Hamiltonian Markov-Chain sampling.

Main Classes:
HamiltonianSampler: standard isotropic sampler
HamiltonianBoundedSampler: subclass allowing bounds on all vector elements.
(more general constraints to a manifold are not implemented.)

A HamiltonianSampler object
can generate samples of any continuous-valued random vector, defined only by
an un-normalized LOG-LIKELIHOOD function, and the GRADIENT of that function.

The sample can store sample vectors either as rows (VECTOR_AXIS == 1)
or as columns (VECTOR_AXIS == 0) in a 2D array.
VECTOR_AXIS is a module-global variable that can be re-assigned by user,
at any time BEFORE a sampler instance is initialized.

Assume a random vector X has probability density p(x),
       but p(x) can be calculated only up to some unknown scale factor.

Define functions neg_log_likelihood and GradNegLL, such that
LL = neg_log_likelihood(x, *args, **kwargs) is a scalar or row vector, with
LL(n) == - log p( x[n, :] ) + constant, (if VECTOR_AXIS==1) and
G = grad_neg_log_likelihood(x, *args, **kwargs) is an array with with gradient vectors, as
G[n, i] == d neg_log_likelihood / d x_i, evaluated at x[n, :].

(NOTE: if VECTOR_AXIS == 0, the arrays are transposed,
and function NegLL and GradNegLL must account for the chosen storage method.)

NegLL and GradNegLL must accept the first argument x as an array with one or many vectors.
If these functions are defined using optional additional arguments,
the arguments saved in properties args and kwargs are used at every call to method sample().

Therefore, if those arguments have changed between calls to the sample method,
the properties args and kwargs must first be explicitly assigned to the new values.

**** Usage Example:

def neg_log_likelihood(x, a, b):
    ......
def grad_neg_log_likelihood(x, a, b):
    ......

# construct a sampler instance h:

h = HamiltonianSampler(neg_log_likelihood, grad_neg_log_likelihood, x0,
    args=(a,),
    kwargs=dict(b=0.),
    epsilon=0.1,
    n_leap_frog_steps=10)

x = h.sample(min_steps=10, max_steps=100)
# Sample row vectors x[n, :] are now (nearly) independent samples,
# drawn from the density function p(x) propto exp(-neg_log_likelihood(x)).
# x.shape == x0.shape

# h.args = (a_new,) # if the argument value has changed.
x = h.sample(n_samples=100, min_steps=1, max_steps=10)
# x.shape[VECTOR_AXIS] == X0.shape[VECTOR_AXIS]
# x.shape[1 - VECTOR_AXIS] = n_samples

# OR:
x = h.safe_sample(n_samples=100, min_steps=5)
# automatically checking and adjusting h.epsilon for good accept_rate

# The sample or safe_sample method can be called repeatedly, to get new batches of samples,
# nearly independent of the previous batch.

**** Settings:

The parameters epsilon and n_leapfrog_steps are CRITICAL!
epsilon should be roughly equal to the smallest dimension of p(x) effective support,
and epsilon * n_leapfrog_steps should correspond to the largest dimension.

It is recommended for the caller to check accept_rate after each sample call,
and adjust epsilon in case it is too small.
Anyway, the sampler raises an AcceptanceError,
if accept_rate falls below property min_accept_rate.

If the distribution has different scales for each coordinate,
epsilon may also be given as a vector,
with different algorithm step sizes for each dimension.

The sample method uses an ad-hoc check that the Markov Chain is reasonably
close to its stationary distribution,
and performs only as many Hamiltonian leapfrog trajectories as necessary,
within the limits (min_steps, max_steps).

All sample vectors in x are processed in parallel,
as different independent 'particles' in Hamiltonian motion.

Method safe_sample checks accept_rate and adjusts epsilon automatically,
BUT samples before and after a change of epsilon
are not guaranteed to be drawn from the same desired distribution.
Samples should then only be used from the same batch
resulting from a single safe_sample call,
preferably with large min_step parameter.
This adaptive approach may be useful especially when the sampler is used iteratively,
with several subsequent calls to safe_sample,
such that the probability of epsilon adjustments decreases toward zero
in later iterations.

Reference:
R M Neal (2011): MCMC using Hamiltonian dynamics. Ch. 5 in
Brooks et al. (eds) Handbook of Markov Chain Monte Carlo.
Chapman and Hall / CRC Press.

*** Version History:

New in version 1.1.0:
2019-08-23, HamiltonianSampler uses numpy.random.Generator as internal property.
    This requires Numpy v. 1.17.
    HamiltonianSampler allows initial seed for reproducible behavior.
    HamiltonianSample.safe_sample can adapt epsilon both up and down,
    until min_accept_rate < accept_rate < max_accept_rate.
    Some other minor fixes.

Version 1.0.0, 2018-09-13, first published version

2017-04-29, allow both args and kwargs for potential-energy and gradient functions
2017-05-25, use logging
2017-06-16, minor update to allow instance to be saved as property of other class
2017-11-05, HamiltonianBoundedSampler use get/set methods for bounds property
2017-12-14, allow either ROW of COLUMN storage of random vectors.
2018-09-13, fix bug init_batch in HamiltonianBoundedSampler
"""
import numpy as np

import logging
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)  # *** for TEST

# VECTOR_AXIS = 0
# random vectors are stored as COLUMNS in 2D arrays
VECTOR_AXIS = 1
# default: random vectors are stored as ROWS in 2D arrays


# --------------------------------------- problems:
class AcceptanceError(RuntimeError):
    """Signal too few accepted trajectories
    """


class ArgumentError(RuntimeError):
    """Signal error in input arguments
    """


# -------------------------------------------------
class HamiltonianSampler:
    """Standard Hamiltonian sampler with isotropic kinetic-energy function,
    and no bounds for sample vector elements.

    The interface is similar to scipy.optimize.minimize.
    The sampler can use the same objective functions as scipy minimize.
    """

    def __init__(self, fun, jac, x,
                 args=(),
                 kwargs=None,
                 epsilon=0.1,
                 n_leapfrog_steps=10,
                 min_accept_rate=0.8,
                 max_accept_rate=0.95,
                 seed=None
                 ):
        """
        :param fun: potential energy function = negative log pdf of sampled distribution,
            except for an arbitrary additive log-normalization constant.
            Will be called as fun(x, *args, **kwargs), with
            x = 2D array of tentative sample vectors.
            Must return 1D array of potential-energy values
            fun(x).shape == (sampler.n_samples,)
                == (x.shape[1],) if VECTOR_AXIS == 0, else == (x.shape[0],)
        :param jac: gradient of fun
            Will be called as jac(x, *args, **kwargs), with
            x = 2D array of tentative sample column vectors.
            jac(x).shape == x.shape
        :param x: 2D array with starting values for all desired sample vectors.
            x[i, n] = i-th element of n-th sample vector if VECTOR_AXIS == 0, OR
            x[n, i] = i-th element of n-th sample vector if VECTOR_AXIS == 11
        :param args: (optional) tuple with positional arguments for fun and jac.
        :param kwargs: (optional) dict with keyword arguments for fun and jac. 
        :param epsilon: (optional) scalar Hamiltonian leapfrog step size
            MUST be carefully selected to match the scale of the sampled distribution.
            Should be roughly equal to the standard deviation of the distribution
            in the spatial direction where the deviation is SMALLEST.
            epsilon may also be a single vector,
            with epsilon.shape == (sampler.len_vector,) if VECTOR_AXIS == 1,
                OR epsilon.shape == (sampler.len_vector, 1) if vector_axis == 0.
            (Neal, 2011, eqs. 4.14 - 4.16)
            May be adjusted externally, based on observed accept_rate,
            but then older samples with different epsilon should be discarded.
        :param n_leapfrog_steps: (optional) number of steps in each Hamilton trajectory
        :param min_accept_rate: (optional) limit to raise AcceptanceError in method sample
        :param max_accept_rate: (optional) upper limit used in method safe_sample
        :param seed: (optional) integer seed for internal random number generator
            Setting the seed gives reproducible sampling behavior.
        """
        self._fun = fun
        self._jac = jac
        self.args = tuple(args)
        if kwargs is None:
            kwargs = dict()
        self.kwargs = dict(kwargs)

        # trajectory parameters:
        self.epsilon = epsilon
        self.n_leapfrog_steps = n_leapfrog_steps

        # initial state for sampler:
        self.x = np.asarray(x)
        self.U = None  # self.potential(self.x)
        # = 1D array with U[n] = potential energy for n-th particle
        # to be updated by each call to self.sample
        self.mean_U_old = 0.
        # updated by one_sample_step, to allow check for unstable trend
        self.n_accepted = 0
        # = total number of accepted trajectories so far
        self.n_trajectories = 0
        # total number of trajectories tried so far
        self.min_accept_rate = min_accept_rate
        # = limit to raise AcceptanceError
        self.max_accept_rate = max_accept_rate
        # = limit for increasing self.epsilon in safe_sample
        self._rng = np.random.default_rng(seed)
        # = random number generator, state preserved even when used in multi-processing

    @property
    def accept_rate(self):
        return self.n_accepted / self.n_trajectories

    @property
    def n_samples(self):
        return self.x.shape[1-VECTOR_AXIS]

    @property
    def len_sample_vector(self):
        return self.x.shape[VECTOR_AXIS]

    @property
    def n_steps(self):
        return self.n_trajectories / self.n_samples

    def potential(self, x):
        """call external potential-energy function
        """
        return self._fun(x, *self.args, **self.kwargs)

    def grad_potential(self, x):
        """call external gradient function
        """
        return self._jac(x, *self.args, **self.kwargs)

    def safe_sample(self, n_samples=None,
                    min_steps=5, max_steps=100):
        """Run a series of trajectories to generate a new sample batch.
        Check that min_accept_rate < accept_rate < max_accept_rate
        and adjust epsilon until accept_rate is OK.
        :param n_samples: (optional) desired number of samples
            if None, start only from self.x
        :param min_steps: (optional) min number of Hamiltonian trajectories
        :param max_steps: (optional) max number of Hamiltonian trajectories
        :return: x = 2D array with new sample vectors, stored according to VECTOR_AXIS

        Result: saved internal state for next sample call
        """
        epsilon_start = 0. + self.epsilon  # must copy
        while self.epsilon > epsilon_start / 10.:
            try:
                self.sample(n_samples, min_steps, max_steps)
                if self.accept_rate > self.max_accept_rate:
                    self.epsilon *= 1.3  # *** ad-hoc adjustment
                    logger.debug(f'High accept_rate; increased epsilon = {self.epsilon}')
                return self.x  # OK result
            except AcceptanceError as e:
                logger.debug(e)
                self.epsilon *= (0.7 + 0.2 * self._rng.random())
        # Giving up: no success even with much reduced epsilon:
        msg = f'Low accept_rate= {self.accept_rate:.1%}. epsilon = {self.epsilon}'
        raise AcceptanceError(msg)  # again!

    def sample(self, n_samples=None,
               min_steps=1, max_steps=100):
        """Run a series of trajectories to generate a new sample batch.
        :param n_samples: (optional) desired number of samples
            if None, start only from self.x
        :param min_steps: (optional) min number of Hamiltonian trajectories
        :param max_steps: (optional) max number of Hamiltonian trajectories
        :return: x = 2D array with new sample vectors, stored according to VECTOR_AXIS

        The actual number of trajectories will range between min_steps and max_steps.
        New trajectories are included until the sample distribution
        seems to have reached a reasonably stationary state.

        Result: saved internal state for next sample call
        """
        if n_samples is not None and n_samples != self.n_samples:
            self.init_batch(n_samples)
        self.U = self.potential(self.x)
        # must initialize self.U here in case self.potential or args or kwargs have changed
        self.n_accepted = 0
        self.n_trajectories = 0
        # count acceptance rate for each call of sample()
        min_steps = max(1, min_steps)
        self.one_sample_step()
        done_steps = 1
        while (done_steps < min_steps
               or (done_steps < max_steps and self.unstable())
               ):
            self.one_sample_step()
            done_steps += 1
        if self.accept_rate < self.min_accept_rate:
            msg = f'Low accept_rate = {self.accept_rate:.1%}. epsilon = {self.epsilon}'
            raise AcceptanceError(msg)
        return self.x

    # --------------------------------- internal functions:

    def init_batch(self, n_samples):
        """Re-sample initial state to desired batch size
        i.e., such that self.n_samples == n_samples
        """
        i = self._rng.integers(0, self.n_samples, size=n_samples)
        self.x = self.x[:,i] if VECTOR_AXIS == 0 else self.x[i, :]
        self.x += self.epsilon * self._rng.standard_normal(size=self.x.shape)

    def one_sample_step(self):
        """Run one Hamilton trajectory,
        and check acceptance for detailed balance
        Starting from self.x, with potential energy self.U

        Result: updated self.x, self.U, self.n_accepted, self.n_trajectories
        """
        self.mean_U_old = np.mean(self.U)
        # save to be used to check trend stability later.
        x0 = self.x
        p0 = self.random_momentum(x0)
        h0 = self.U + self.kinetic_energy(p0)
        # = Hamiltonians at starting points
        (x, p) = self.trajectory(x0, p0,
                                 self.random_epsilon,
                                 self.random_leapfrog_steps)
        # p = -p # not needed because kinetic_energy is symmetric
        u1 = self.potential(x)
        h1 = u1 + self.kinetic_energy(p)
        accept = self._rng.random(size=len(h1)) < np.exp(h0 - h1)
        if VECTOR_AXIS == 0:
            self.x[:, accept] = x[:, accept]
        else:
            self.x[accept, :] = x[accept, :]
        self.U[accept] = u1[accept]
        self.n_accepted += np.sum(accept)
        self.n_trajectories += self.n_samples

    def trajectory(self, x, p, dt, leap_steps):
        """Run one leapfrog trajectory with all particles in parallel in the sample batch.
        :param x: 2D array with start position vectors
        :param p: 2D array with start momentum vectors
        :param dt: scalar leapfrog step size
            OR 2D array with shape broadcast-compatible with x
        :param leap_steps: integer number of leapfrog steps
        :return: tuple (x, p); updated copy versions of x and p
        """
        # self.Q.append(x[:, 0].copy()) # for TEST display only
        p = p - 0.5 * dt * self.grad_potential(x)
        x = x + dt * p
        # do not assign in place, because we must work on a copy
        # self.Q.append(x[:, 0].copy())
        for _ in range(1, leap_steps):
            p -= dt * self.grad_potential(x)
            x += dt * p
            # self.Q.append(x[:, 0].copy())
        p -= 0.5 * dt * self.grad_potential(x)
        return x, p

    def unstable(self):
        """Ad-hoc check for stability of sampling Markov Chain.
        :return: boolean = True, if trend is large in relation to variance across sample batch,
            with 'large' defined as > 1.5 * expected St.Dev
        NOTE: needs self.n_samples >> 1 for variance estimate
        """
        if self.accept_rate < self.min_accept_rate:
            return True
        abs_d = np.abs(self.mean_U_old - np.mean(self.U)) / self.accept_rate
        # scaled up to compensate for zero diff for rejected trajectories
        std_d = np.sqrt(np.var(self.U) * 2. / self.n_samples)
        # = expected std.dev of abs_d, estimated from new batch of samples
        return abs_d > 1.5 * std_d

    @property
    def random_epsilon(self):
        """Slightly random variations on epsilon.
        Ref: Neal (2011) recommended +- 20% randomization
        :return: scalar epsilon
        """
        r_range = 0.2
        # = random range of relative epsilon variations
        r = self._rng.random() * 2 * r_range - r_range
        return self.epsilon * (1 + r)

    @property
    def random_leapfrog_steps(self):
        """ Slightly random variations around nominal self.n_leapfrog_steps
        Ref: Neal (2011)
        :return: scalar integer
        """
        r_range = 0.2
        # = random range of relative variations
        r = self._rng.random() * 2 * r_range - r_range
        return int(self.n_leapfrog_steps * (1 + r))

    def random_momentum(self, x):
        """Generate random momentum vectors corresponding to x
        Returns: p = 2D array with standard Gaussian momentum vectors
            p.shape == self.x.shape
        """
        return self._rng.standard_normal(size=x.shape)

    @staticmethod
    def kinetic_energy(p):
        """Kinetic energy for momentum p
        Input: p = 2D array with momentum column vectors
        Returns: Kinetic = 1D array with kinetic energy
            Kinetic[n] = kinetic energy of n-th sample of p
        """
        return np.sum(p**2, axis=VECTOR_AXIS) / 2


# -----------------------------------------------------------------------
class HamiltonianBoundedSampler(HamiltonianSampler):
    """Hamiltonian sampler with isotropic momentum function,
    with lower and/or upper coordinate bounds for each vector element
    """
    def __init__(self, fun, jac, x,
                 bounds=None,
                 **kwargs):
        """
        :param fun: potential energy function = negative log pdf
        :param jac: gradient of fun
        :param x: 2D array with starting values for all desired sample vectors.
            x[i, n] = i-th element of n-th sample vector if VECTOR_AXIS=0, OR
            x[n, i] = i-th element of n-th sample vector if VECTOR_AXIS=1
        :param bounds: sequence of pairs (x_min, x_max)
            with low and high bounds for each sample vector element.
            Either x_min or x_max may be None.
            x_min may be -inf; x_max may be +inf
            len(bounds) == sample vector length == self.len_sample_vector
        :param kwargs: any other keyword arguments for superclass constructor.
        """
        super().__init__(fun, jac, x, **kwargs)
        if bounds is None:
            bounds = [(-np.inf, np.inf) for _ in range(x.shape[VECTOR_AXIS])]
        # assert len(bounds) == x.shape[VECTOR_AXIS], 'bounds must match vector length'
        if len(bounds) != x.shape[VECTOR_AXIS]:
            raise ArgumentError('bounds must match vector length')
        # *** or allow single bound pair?
        self._bounds = [self.check_bound(*b) for b in bounds]
        x_elements = self.x if VECTOR_AXIS == 0 else self.x.T
        for (x_i, (l_i, h_i)) in zip(x_elements, self.bounds):
            np.maximum(x_i, l_i, out=x_i)
            np.minimum(x_i, h_i, out=x_i)
            # just clip data to bounds, storing results in place

    @property
    def bounds(self):
        return self._bounds

    @bounds.setter
    def bounds(self, b):
        """Check and adjust, in case user explicitly assigns new bounds.
        :param b: list of tuples (l_i, h_i) with (low, high) bounds
            l_i == None is recoded as l_i = -inf
            h_i == None is recoded as h_i = +inf
        """
        if len(bounds) != self.x.shape[VECTOR_AXIS]:
            raise ArgumentError('bounds must match vector length')
        self._bounds = [self.check_bound(*b_i) for b_i in b]

    def init_batch(self, n_samples):
        """Re-sample initial state to desired batch size of particles
        i.e., such that self.n_samples == n_samples
        and make sure all generated samples are within bounds.
        Arne Leijon, 2018-09-13
        """
        super().init_batch(n_samples)
        (self.x, _) = self.keep_within_bounds(self.x, np.zeros_like(self.x))

    def trajectory(self, x, p, dt, leap_steps):
        """Run one leapfrog trajectory for each particle,
        :param x: 2D array with start position vectors
        :param p: 2D array wth start momentum vectors
        :param dt: scalar leapfrog step size
            OR 2D array with shape broadcast-compatible with x
        :param leap_steps: integer number of leapfrog steps
        :return: tuple (x, p); updated copy versions of x and p
        """
        p = p - 0.5 * dt * self.grad_potential(x)
        x = x + dt * p
        # do not assign in place, because we must make copy
        (x, p) = self.keep_within_bounds(x, p)
        for _ in range(1, leap_steps):
            p -= dt * self.grad_potential(x)
            x += dt * p
            (x, p) = self.keep_within_bounds(x, p)
        p -= 0.5 * dt * self.grad_potential(x)
        return x, p

    def keep_within_bounds(self, x, p):
        """Reflect particle trajectories at coordinate bounds,
        to make sure that all low_i <= x_i <= high_i.
        :param x: 2D array with start position vectors
        :param p: 2D array wth start momentum vectors
        :return: tuple (x, p); updated copy versions of x and p

        Ref: Neal (2011) Fig 8
        """
        (x_work, p_work) = (x.T, p.T) if VECTOR_AXIS == 1 else (x, p)
        for (x_i, p_i, (l_i, h_i)) in zip(x_work, p_work, self.bounds):
            outside_h = x_i > h_i
            outside_l = x_i < l_i
            while np.any(outside_l) or np.any(outside_h):
                x_i[outside_h] -= 2*(x_i[outside_h] - h_i)
                p_i[outside_h] *= -1
                x_i[outside_l] -= 2*(x_i[outside_l] - l_i)
                p_i[outside_l] *= -1
                outside_h = x_i > h_i
                outside_l = x_i < l_i
        return (x_work.T, p_work.T) if VECTOR_AXIS == 1 else (x_work, p_work)

    @staticmethod
    def check_bound(low, high):
        """Ensure that bounds (low, high) are ordered as b.low < b.high,
        (otherwise the bound reflection algorithm will never terminate).
        Any bound == None is replaced by -inf or +inf
        :param low: scalar real
        :param high: scalar real
        :return: tuple (low, high) with checked bounds in correct order
        """
        if low is None:
            low = -np.inf
        if high is None:
            high = np.inf
        if low > high:
            (low, high) = (high, low)
        if np.isclose(low, high):  # low == high:
            raise ArgumentError('All (low, high) bounds must be separated')
        return low, high


# ------------------------------------------------------ TEST:
if __name__ == '__main__':
    from scipy.stats import norm

    VECTOR_AXIS = 1
    import matplotlib.pyplot as plt
    
    # print('logger: ', logger)
    # logger.warning('*** Test logging ***')
    print(f'*** Testing HamiltonianSampler with 2-dim Gaussian; VECTOR_AXIS={VECTOR_AXIS} ***\n')
    print('NOTE: some settings can cause periodic trajectories!')
    print('turn off epsilon and leapfrog randomization to see this problem more often')
    print('TEST: sigma = np.array([10., 3.]); epsilon=3.; n_leapfrog_steps=9, or 12, or ...\n')
    # fixed single starting point, no epsilon randomization
    sigma = np.array([10., 3.])
    hamilton_scale = np.min(sigma)
    hamilton_steps = max(10, int(np.max(sigma) / hamilton_scale))
    # prec = 1. / (sigma**2).reshape((-1,1))

    # = column principal vectors:
    P = np.array([[1., 1.],
                  [1., -1.]]) / np.sqrt(2.)
    # P = np.eye(2)
    # = principal-vector matrix

    def NegLL(x, sigma):
        if VECTOR_AXIS == 0:
            z = np.dot(P.T, x) / sigma.reshape((-1,1))
        else:
            z = np.dot(P.T, x.T) / sigma.reshape((-1,1))
        # projection on Principal axes
        return np.sum(z**2, axis=0) / 2.

    def Grad_NegLL(x, sigma):
        if VECTOR_AXIS == 0:
            z = np.dot(P.T, x)
            return np.dot(P / sigma**2, z)
        else:
            z = np.dot(x, P)
            return np.dot(z / sigma**2, P.T)

    def sample(n_samples):
        x = np.dot(sigma * P, norm.rvs(size=(2, n_samples)))
        if VECTOR_AXIS == 0:
            return x
        else:
            return x.T

    def plot_samples(ax, x):
        b = 2 * np.max(sigma)
        if VECTOR_AXIS == 0:
            ax.plot(x[0,:], x[1,:], '.b')
        else:
            ax.plot(x[:,0], x[:,1], '.b')
        ax.set_xlim([-b, b])
        ax.set_ylim([-b,b])

    def plot_sample_state(ax, h):
        """plot state of sampler h
        """
        plot_samples(ax, h.x)

    scipy_x = sample(1000)
    print('scipy_x.mean = ', np.mean(scipy_x, axis=1-VECTOR_AXIS))
    print('scipy_x.std = ', np.std(scipy_x, axis=1-VECTOR_AXIS))
    print('scipy_x mean LL = ', - np.mean(NegLL(scipy_x, sigma)) )

    # --------------------------------------- check gradient:
    # from scipy.optimize import check_grad, approx_fprime
    #
    # def test(x):
    #     if VECTOR_AXIS == 0:
    #         return NegLL(x.reshape((-1, 1)), sigma)[0]
    #     else:
    #         return NegLL(x.reshape((1, -1)), sigma)[0]
    #
    # def grad_test(x):
    #     if VECTOR_AXIS == 0:
    #         xt = x.reshape((-1,1))
    #         return Grad_NegLL(xt, sigma).reshape((-1,))
    #     else:
    #         return Grad_NegLL(x, sigma)
    #
    # test_x = scipy_x[:,0]
    # test_x = np.array([-5., +5.])
    # err = check_grad(test, grad_test, test_x)
    # print('\nGradient test:')
    # print('test_x =', test_x)
    # print('test =', test(test_x))
    # print('grad_test =', grad_test(test_x))
    # print('approx_grad = ', approx_fprime(test_x, test, epsilon=1e-6))
    # print('check_grad err = ', err)
    # print()
    # # --------------------------------------------------

    x0 = np.zeros((2, 2000))
    if VECTOR_AXIS == 1:
        x0 = x0.T
    h = HamiltonianSampler(NegLL, Grad_NegLL, x0,
                           kwargs=dict(sigma=sigma),
                           min_accept_rate=0.9,
                           epsilon=hamilton_scale,
                           n_leapfrog_steps=12)
    ham_x = h.sample(min_steps=1, n_samples=1000)
    # print('h.trajectory:', np.array(h.Q))
    print()
    print('ham_x.mean = ', np.mean(ham_x, axis=1-VECTOR_AXIS))
    print('ham_x.std = ', np.std(ham_x, axis=1-VECTOR_AXIS))
    print('ham_x mean LL = ', - np.mean(NegLL(ham_x, sigma)))
    print('ham.accept_rate= ', h.accept_rate)
    print('ham.n_steps= ', h.n_steps)

    f1, ax1 = plt.subplots()
    plot_samples(ax1, scipy_x)
    ax1.set_title('Scipy Gaussian Samples')
    f1.show()

    f2,ax2 = plt.subplots()
    plot_sample_state(ax2, h)
    ax2.set_title('Hamiltonian Samples')

    plt.show()

    # ------------------------------------------------------------------------
    print('\n*** Testing HamiltonianSampler reproducible with seed ***')
    h = HamiltonianSampler(NegLL, Grad_NegLL, x0,
                           kwargs=dict(sigma=sigma),
                           min_accept_rate=0.9,
                           epsilon=hamilton_scale,
                           n_leapfrog_steps=12,
                           seed=12345)
    ham_x = h.sample(min_steps=1, n_samples=5)
    print('ham_x = ', ham_x)
    h = HamiltonianSampler(NegLL, Grad_NegLL, x0,
                           kwargs=dict(sigma=sigma),
                           min_accept_rate=0.9,
                           epsilon=hamilton_scale,
                           n_leapfrog_steps=12,
                           seed=12345)
    ham_x = h.sample(min_steps=1, n_samples=5)
    print('ham_x should be same = ', ham_x)

    # ------------------------------------------------------------------------
    print('\n*** Testing HamiltonianBoundedSampler ***')
    bounds = [(-3., +5.), (None, 10.)]
    x0 = np.zeros((2,1000)) # + np.array([2., -2.]).reshape((-1,1))
    if VECTOR_AXIS == 1:
        x0 = x0.T
    h = HamiltonianBoundedSampler(NegLL, Grad_NegLL, x0,
                                  args=(sigma,),
                                  bounds=bounds,
                                  min_accept_rate=0.7,
                                  epsilon=hamilton_scale,
                                  n_leapfrog_steps=12) #hamilton_steps)
    ham_x = h.sample(min_steps=1)
    # print('h.trajectory:', np.array(h.Q))
    print()
    print('ham_x.mean = ', np.mean(ham_x, axis=1-VECTOR_AXIS))
    print('ham_x.std = ', np.std(ham_x, axis=1-VECTOR_AXIS))
    print('ham_x mean LL = ', - np.mean(NegLL(ham_x, sigma)))
    print('ham.accept_rate= ', h.accept_rate)
    print('ham.n_steps= ', h.n_steps)

    fb1, ax1 = plt.subplots()
    plot_samples(ax1, scipy_x)
    ax1.set_title('Scipy Unbounded Gaussian Samples')
    fb1.show()

    fb2,ax2 = plt.subplots()
    plot_sample_state(ax2, h)
    ax2.set_title('Hamiltonian Bounded Samples')
    plt.show()

