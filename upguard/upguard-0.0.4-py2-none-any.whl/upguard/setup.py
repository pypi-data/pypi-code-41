import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name='upguard',
  version='0.0.3',
  scripts=['__init__.py', 'BaseObject.py', 'Account.py', 'ConnectionManager.py', 'ConnectionManagerGroup.py', 'Environment.py', 'Event.py', 'EventAction.py', 'Incident.py', 'MediumType.py', 'Node.py', 'NodeGroup.py', 'NodeType.py', 'OperatingSystem.py', 'OperatingSystemFamily.py', 'ScheduledJob.py', 'SystemMetric.py', 'User.py'],
  author='UpGuard',
  author_email='support@upguard.com',
  description='UpGuard SDK for Python',
  long_description=long_description,
  long_description_content_type="text/markdown",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 2",
    "License :: Other/Proprietary License",
    "Operating System :: OS Independent",
  ],
)

