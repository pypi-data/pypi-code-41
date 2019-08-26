from ipykernel.kernelapp import IPKernelApp
from .kernel import ATSKernel
IPKernelApp.launch_instance(kernel_class=ATSKernel)
