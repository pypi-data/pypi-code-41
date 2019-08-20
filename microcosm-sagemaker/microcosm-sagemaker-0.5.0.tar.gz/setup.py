#!/usr/bin/env python
from setuptools import find_packages, setup


project = "microcosm-sagemaker"
version = "0.5.0"

setup(
    name=project,
    version=version,
    description="Opinionated machine learning organization and configuration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/microcosm-sagemaker",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6",
    keywords="microcosm",
    install_requires=[
        "boto3>=1.9.90",
        "click>=7.0",
        "microcosm>=2.12.0",
        "microcosm_flask[metrics,spooky]>=1.28.0",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
        "console_scripts": [
            "train = microcosm_sagemaker.commands.train:main",
            "evaluate = microcosm_sagemaker.commands.evaluate:main",
            "runserver = microcosm_sagemaker.commands.runserver:main",
        ],
        "microcosm.factories": [
            "active_bundle = microcosm_sagemaker.factories:configure_active_bundle",
            "active_evaluation = microcosm_sagemaker.factories:configure_active_evaluation",
            (
                "bundle_and_dependencies_loader = "
                "microcosm_sagemaker.bundle_traversal:BundleAndDependenciesLoader"
            ),
            (
                "bundle_and_dependencies_trainer = "
                "microcosm_sagemaker.bundle_traversal:BundleAndDependenciesTrainer"
            ),
            (
                "load_active_bundle_and_dependencies = "
                "microcosm_sagemaker.factories:load_active_bundle_and_dependencies"
            ),
            "ping_convention = microcosm_sagemaker.conventions.ping:configure_ping",
            "sagemaker_health_convention = microcosm_sagemaker.conventions.health:configure_health",
            "random = microcosm_sagemaker.random:Random",
            "sagemaker = microcosm_sagemaker.factories:configure_sagemaker",
            "sagemaker_metrics = microcosm_sagemaker.metrics.store:SageMakerMetrics",
            (
                "single_threaded_bundle_orchestrator = "
                "microcosm_sagemaker.bundle_orchestrator:SingleThreadedBundleOrchestrator"
            ),
            "training_initializers = microcosm_sagemaker.training_initializer_registry:TrainingInitializerRegistry",
        ],
    },
    extras_require={
        "test": [
            "PyHamcrest>=1.9.0",
            "coverage>=4.0.3",
            "parameterized>=0.7.0",
        ],
        "profiling": "pyinstrument>=3.0",
    },
)
