#!/usr/bin/env python

import os
import time
import tarfile
import threading
# import writeInputs

import radical.entk  as re
import radical.utils as ru


RMQ_PORT = int(os.environ.get('RMQ_PORT', 32769))
SANDER   = '/home/scm177/mantel/AMBER/amber14/bin/sander'
SANDER   = 'sleep 3; echo'


# ------------------------------------------------------------------------------
#
class Exchange(re.AppManager):
    '''
    A ReplicaExchange class owns a number of replicas and signs responsible for
    their exchange algorthm.  G
    '''

    def __init__(self, size, max_wait, min_cycles, min_temp, max_temp,
                 timesteps, basename, executable, cores):

        self._size       = size
        self._max_wait   = max_wait
        self._min_cycles = min_cycles
        self._min_temp   = min_temp
        self._max_temp   = max_temp
        self._timesteps  = timesteps
        self._basename   = basename
        self._executable = executable
        self._cores      = cores

        self._log = ru.Logger('radical.repex.exc')

        # inintialize the entk app manager
        re.AppManager.__init__(self, autoterminate=False, port=RMQ_PORT) 
        self.resource_desc = {"resource" : 'local.localhost',
                              "walltime" : 30,
                              "cpus"     : 4}                                

        # this is ugly
        self._sbox      = '$Pipeline_untarPipe_Stage_untarStg_Task_untarTsk'
        self._cnt       = 0  # count exchanges

        self._replicas  = list()  # list of all participating replicas
        self._waitlist  = list()  # replicas waiting for an exchange
        self._exchanges = dict()  # currently active exchanges

        self._waitlist_lock = threading.Lock()
        self._exchange_lock = threading.Lock()

        # create the required number of replicas
        for i in range(self._size):

            replica = Replica(check_ex  = self._check_exchange,
                              after_ex  = self._after_exchange,
                              rid       = i,
                              sbox      = self._sbox,
                              cores     = self._cores, 
                              exe       = self._executable)

            self._replicas.append(replica)


    # --------------------------------------------------------------------------
    #
    def overview(self):
        '''
        print a visual aide to show current state of all replicas.  Following
        codes are used:

          + running MD
          - suspended
          * running EX
          = done
          _ failed
        '''

        out = ''
        for r in self._replicas:
            if   r.state == re.states.SUSPENDED: out += '-'
            elif r.state == re.states.DONE     : out += '='
            elif r.state == re.states.FAILED   : out += '_'
            else:
                c = r.current_stage
                if c == 0                      : out += '.'
                else:
                    s = r.stages[c - 1]
                    t = list(s.tasks)[0]
                    if   'extsk' in t.name   : out += '*'
                    elif 'mdtsk' in t.name   : out += '+'
                    else                     : out += '?'

        return out


    # --------------------------------------------------------------------------
    #
    def setup(self):

      # self._log.debug('=== data staging')
      #
      # # prepare input for all replicas
      # writeInputs.writeInputs(max_temp=self._max_temp,
      #                         min_temp=self._min_temp,
      #                         replicas=self._size,
      #                         timesteps=self._timesteps,
      #                         basename=self._basename)
      #
      # # and tar it up
      # tar = tarfile.open("input_files.tar", "w")
      # for name in [self._basename + ".prmtop",
      #              self._basename + ".inpcrd",
      #              self._basename + ".mdin"]:
      #     tar.add(name)
      #
      # for replica in self._replicas:
      #     tar.add  ('mdin-%s-0' % replica.rid)
      #     os.remove('mdin-%s-0' % replica.rid)
      #
      # tar.close()

        # create a single pipeline with one stage to transfer the tarball
        task = re.Task()
        task.name              = 'untarTsk'
      # task.executable        = 'python'
        task.executable        = 'echo'
      # task.upload_input_data = ['untar_input_files.py', 'input_files.tar']
        task.arguments         = ['untar_input_files.py', 'input_files.tar']
        task.cpu_reqs          = 1
        task.post_exec         = []

        stage = re.Stage()
        stage.name = 'untarStg'
        stage.add_tasks(task)

        setup = re.Pipeline()
        setup.name = 'untarPipe'
        setup.add_stages(stage)

        # run the setup pipeline
        self.workflow = set([setup]) 
        self.run() 


    # --------------------------------------------------------------------------
    #
    def execute(self):
        '''
        First stage data, then start the actual repex workload
        '''

        self.setup()

        # run the replica pipelines
        self._log.debug('exc repex')
        self.workflow = set(self._replicas)
        self.run() 


    # --------------------------------------------------------------------------
    #
    def terminate(self):

        self._log.debug('exc term')

        self.resource_terminate()


    # --------------------------------------------------------------------------
    #
    def _select_exchanges(self):
        '''
        For now we only follow a very simple approach where we check if we have
        more than `self._max_wait` replicas, If so, then those will form an
        exchange list
        '''

        ret = list()  # list of exchange sets

        with self._waitlist_lock:

            print 'x: %d >= %d' % (len(self._waitlist), self._max_wait)

            while len(self._waitlist) >= self._max_wait:

                # extract sufficient number of replicas into new exchange # list
                ret.append(self._waitlist[:self._max_wait])
                self._waitlist = self._waitlist[self._max_wait:]

                print 'X: %d >= %d' % (len(self._waitlist), self._max_wait)


        print 'S: %s' % [len(s) for s in ret]

        return ret


    # --------------------------------------------------------------------------
    #
    def _check_exchange(self, replica):
        '''
        A replica finished an MD step.  At this point this routine is triggered
        to check if the replica can participate in an exchange step.  For that
        decision to be made, the replica is suspended and added to the list of
        waiting replicas (`self._waitlist`).

        One of two things will then happen:

          (a) the exchange algorithms determines there are not enough suitable
              replicas available for an exchange - this routine will leave the
              replica suspended and simply return; or

          (b) the exhange algorithm *does* find a suitable set of exchange

              partners - this routine will then initiate such an exchange over
              the set of eligible replicas, but leave all other waiting replicas
              suspended until they too become eligible.

        In the second case the algorithm will thus select a list of replicas to
        perform an exchange.  Out of that set, the first replica will be
        unsuspended (resumed) and an exchange task will be added to its work
        pipeline.  Only after that exchange has been completed will all aother
        replicas in that exchange set be resumed (in the routine
        `self._after_exchange`).

        As not all suspended replicas may be eligible for an exchange at any
        point in time, but may become eligible soon after a specific set of
        replicas entered some exchange, it can happen that multiple exchange
        steps are concurrently active.  The Exchange class will keep track of
        those exchanging subsets in `self._exchanges`, a dictionary of replica
        lists, where the key is the pipeline ID of the replica pipeline
        performing the exchange step.  The `_after_exchange` method will resume
        replicas only for it's own exchange step, and will then clean out the
        `self._exchanges` entry.

        What specific subset out of the set of suspended replicas is eligible
        for an exchange is at the core of the exchange algorithm, and will be
        decided in a pluggable subroutine (see documentation of
        '`self._select_exchanges()`).
        '''

        print '++++++++++++++++'
        self._log.debug('=== EX %s check exchange', replica.uid)

        # suspend this replica

        print '1: ', self.overview()

        # ...and add it to waitlist
        with self._waitlist_lock:
            self._waitlist.append(replica)

        # determine if one (or more) subset(s) of replicas exist which are
        # eligible for an exchange
        exchange_sets = self._select_exchanges()

        if not exchange_sets:
            # no, nothing suitable found here.  We are done.
            self._log.debug('=== EX %s susp', replica.uid)
            replica.suspend()
            return



        # ok, so the selection algorithm did find some sets (at least one) which
        # can be used for exchange.  We select the first replica of each set and
        # task it to perform the exchange step
        for exchange_set in exchange_sets:

            assert(len(exchange_set) > 1)       # we need more than one replica
       ##   exchange_replica = exchange_set[0]  # first replica runs exchange
            exchange_replica = replica

            self._log.debug('=== EX %s exchange', exchange_replica.uid)

            task = re.Task()
            task.name       = 'extsk'
         ## task.executable = 'python'
            task.executable = 'echo'
            task.arguments  = ['t_ex_gibbs.py', len(self._waitlist)]

         ## for replica in self._waitlist:
         ##     rid   = replica.rid
         ##     cycle = replica.cycle
         ##     task.link_input_data.append('%s/mdinfo-%s-%s' 
         ##                                % (self._sbox, rid, cycle))
            stage = re.Stage()
            stage.add_tasks(task)
            stage.post_exec = replica._after_exchange

            exchange_replica.add_stages(stage)

            # the exchange step is ready to run: we keep track of the step in
            # `self._exchanges` and unsuspend the replica to do the deed
            with self._exchange_lock:
                assert(exchange_replica.uid not in self._exchanges)
                self._exchanges[exchange_replica.uid] = exchange_set
                self._log.debug('=== EX %s exchange run', exchange_replica.uid)
              # print '--- unsuspend   %s' % exchange_replica.uid
              # exchange_replica.resume()
              # print '--- unsuspended %s' % exchange_replica.uid

        print '2: ', self.overview()
        return replica.uid


    # --------------------------------------------------------------------------
    #
    def _after_exchange(self, exchange_replica):
        '''
        This is triggered after the exchange stage from above.  Resume all
        suspended replicas patrticipating in the current exchange step, and
        also add a new MD stage for those which did not reach end of cycles.
        '''

        print '3: ', self.overview()
        self._log.debug('=== EX %s after exchange' % exchange_replica.uid)

        # get list of replica which were part of the completed exchange
        with self._exchange_lock:
            assert(exchange_replica.uid in self._exchanges)
            exchange_set = self._exchanges[exchange_replica.uid]
            del(self._exchanges[exchange_replica.uid])

        resumed = list()
        for replica in exchange_set:

            if replica.cycle <= self._min_cycles:

                # more work to do for this replica
                replica.add_md_stage()

                # resume the replica (but skip the exchange_replica since it is
                # still active after the exchange step.
                if replica.rid != exchange_replica.rid:
                    self._log.debug('=== EX %s resume', replica.uid)
                  # replica.resume()
                    resumed.append(replica.uid)

        # increase exchange counter
        self._cnt += 1
        print '4: ', self.overview()

        return resumed


# ------------------------------------------------------------------------------
#
class Replica(re.Pipeline):
    '''
    A `Replica` is an EnTK pipeline which consists of MD stages which are
    subject to an exchange algorithm
    The initial setup is for one MD stage - Exchange and more
    MD stages get added depending on runtime conditions.
    '''

    # --------------------------------------------------------------------------
    #
    def __init__(self, check_ex, after_ex, rid, sbox, cores, exe):

        self._check_ex  = check_ex   # is called when checking for exchange
        self._after_ex  = after_ex   # is called when exchange is done
        self._rid       = rid
        self._sbox      = sbox
        self._cores     = cores
        self._exe       = exe
        self._cycle     = 0  # initial cycle

        self._log = ru.Logger('radical.repex.rep')

        # entk pipeline initialization
        re.Pipeline.__init__(self)
        self.name = 'p_%s' % self.rid

        # add an initial md stage
        self.add_md_stage()


    @property
    def rid(self):   return self._rid

    @property
    def cycle(self): return self._cycle


    # --------------------------------------------------------------------------
    #
    def add_md_stage(self):


        rid   = self._rid
        cycle = self._cycle
        sbox  = self._sbox
        cores = self._cores
        exe   = self._exe

        self._log.debug('=== %s add md (cycle %s)', rid, cycle)

        task = re.Task()
        task.name            = 'mdtsk-%s-%s'               % (      rid, cycle)
     ## task.link_input_data = ['%s/inpcrd > inpcrd-%s-%s' % (sbox, rid, cycle),
     ##                          '%s/prmtop'               % (sbox),
     ##                          '%s/mdin-%s-%s > mdin'    % (sbox, rid, cycle)]
        task.arguments       = ['-O', 
                                '-i',   'mdin', 
                                '-p',   'prmtop', 
                                '-c',   'inpcrd-%s-%s'     % (      rid, cycle), 
                                '-o',   'out',
                                '-x',   'mdcrd',
                                '-r',   '%s/inpcrd-%s-%s'  % (sbox, rid, cycle),
                                '-inf', '%s/mdinfo-%s-%s'  % (sbox, rid, cycle)]
        task.executable      = exe
        task.cpu_reqs        = {'processes' : cores}
        task.pre_exec        = ['echo $SHARED']

        stage = re.Stage()
        stage.add_tasks(task)
        stage.post_exec = self._after_md

        self.add_stages(stage)


    # --------------------------------------------------------------------------
    #
    def _after_md(self):
        '''
        after an md cycle, record its completion and check for exchange
        '''

        self._log.debug('=== %s after md', self.rid)

        self._cycle += 1
        self._check_ex(self)


    # --------------------------------------------------------------------------
    #
    def _after_exchange(self):
        '''
        after an ex cycle, trigger replica resumption
        '''
        print 'after exchange'
        self._log.debug('=== %s after ex', self.rid)
        self._after_ex(self)


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':


    exchange = Exchange(size       = 2,
                        max_wait   = 2,
                        min_cycles = 2, 
                        min_temp   = 100,
                        max_temp   = 200,
                        timesteps  = 500,
                        basename   = 'ace-ala', 
                        executable = SANDER, 
                        cores      = 1)

    exchange.execute()       # run replicas and exchanges
    exchange.terminate()     # done


# ------------------------------------------------------------------------------

