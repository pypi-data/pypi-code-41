import chainermn
from chainermn import scatter_dataset as scatter

from .base import DefaultFinetuner

class MPIFinetuner(DefaultFinetuner):

	@property
	def mpi(self):
		return self.comm is not None

	@property
	def mpi_main_process(self):
		return not self.mpi or self.comm.rank == 0

	def gpu_config(self, opts, comm=None):
		super(MPIFinetuner, self).gpu_config(opts)

		self.comm = comm
		if self.mpi:
			self.device = opts.gpu[self.comm.rank]

			# self.device += self.comm.intra_rank

	def scatter_datasets(self):
		if self.mpi:
			self.train_data = scatter(self.train_data, self.comm)
			self.val_data = scatter(self.val_data, self.comm)

	def init_datasets(self, *args, **kwargs):

		if not self.mpi_main_process:
			self.train_data, self.val_data = None, None
			return

		super(MPIFinetuner, self).init_datasets(*args, **kwargs)

		self.scatter_datasets()

	def init_optimizer(self, opts):
		super(MPIFinetuner, self).init_optimizer(opts)

		if self.mpi:
			self.opt = chainermn.create_multi_node_optimizer(self.opt, self.comm)

	def init_evaluator(self):
		super(MPIFinetuner, self).init_evaluator()

		if self.mpi:
			self.evaluator = chainermn.create_multi_node_evaluator(
				self.evaluator, self.comm)

	def run(self, opts, ex):
		super(MPIFinetuner, self).run(opts, ex, no_observe=not self.mpi_main_process)
