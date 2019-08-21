# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['torchtrainer', 'torchtrainer.callbacks', 'torchtrainer.metrics']

package_data = \
{'': ['*']}

install_requires = \
['torch>=1.2,<2.0',
 'torchvision>=0.4.0,<0.5.0',
 'tqdm>=4.33,<5.0',
 'visdom>=0.1.8,<0.2.0']

setup_kwargs = {
    'name': 'torchtrainer',
    'version': '0.3.8',
    'description': 'Focus on building and optimizing pytorch models not on training loops',
    'long_description': "# torchtrainer\n\n\nPyTorch model training made simpler without loosing control. Focus on optimizing your model! Concepts are heavily inspired by the awesome project [torchsample](https://github.com/ncullen93/torchsample) and [Keras](https://github.com/keras-team/keras).\nFurther, besides applying Epoch Callbacks it also allows to call Callbacks every time after a specific number of batches passed (iterations) for long epoch durations.\n\n[![Build Status](https://travis-ci.com/VictorKuenstler/torchtrainer.svg?branch=master)](https://travis-ci.com/VictorKuenstler/torchtrainer)\n[![codecov](https://codecov.io/gh/VictorKuenstler/torchtrainer/branch/master/graph/badge.svg)](https://codecov.io/gh/VictorKuenstler/torchtrainer)\n\n## Features\n\n* `Torchtrainer`\n* Logging utilities\n* Metrics\n* Visdom Visualization\n* Learning Rate Scheduler\n* Checkpointing\n* Flexible for muliple data inputs\n* Setup validation after every ... batches\n\n## Usage\n\n### Installation\n\n```bash\npip install torchtrainer\n```\n\n\n### Example\n\n```python\nfrom torch import nn\nfrom torch.optim import SGD\nfrom torchtrainer import TorchTrainer\nfrom torchtrainer.callbacks import VisdomLinePlotter, ProgressBar, VisdomEpoch, Checkpoint, CSVLogger, \\\n    EarlyStoppingEpoch, ReduceLROnPlateauCallback\nfrom torchtrainer.metrics import BinaryAccuracy\n\n\nmetrics = [BinaryAccuracy()]\n\ntrain_loader = ...\nval_loader = ...\n\nmodel = ...\nloss = nn.BCELoss()\noptimizer = SGD(model.parameters(), lr=0.001, momentum=0.9)\n\n# Setup Visdom Environment for your modl\nplotter = VisdomLinePlotter(env_name=f'Model {11}')\n\n\n# Setup the callbacks of your choice\n\ncallbacks = [\n    ProgressBar(log_every=10),\n    VisdomEpoch(plotter, on_iteration_every=10),\n    VisdomEpoch(plotter, on_iteration_every=10, monitor='binary_acc'),\n    CSVLogger('test.csv'),\n    Checkpoint('./model'),\n    EarlyStoppingEpoch(min_delta=0.1, monitor='val_running_loss', patience=10),\n    ReduceLROnPlateauCallback(factor=0.1, threshold=0.1, patience=2, verbose=True)\n]\n\ntrainer = TorchTrainer(model)\n\n# function to transform batch into inputs to your model and y_true values\n# if your model accepts multiple inputs, just put all inputs into a tuple (input1, input2), y_true\ndef transform_fn(batch):\n    inputs, y_true = batch\n    return inputs, y_true.float()\n\n# prepare your trainer for training\ntrainer.prepare(optimizer,\n                loss,\n                train_loader,\n                val_loader,\n                transform_fn=transform_fn,\n                callbacks=callbacks,\n                metrics=metrics)\n\n# train your model\nresult = trainer.train(epochs=10, batch_size=10)\n\n``` \n\n\n### Callbacks\n\n#### Logger\n\n* `CSVLogger`\n* `CSVLoggerIteration`\n* `ProgressBar`\n\n#### Visualization and Logging\n\n* `VisdomEpoch`\n\n#### Optimizers\n\n* `ReduceLROnPlateauCallback`\n* `StepLRCallback`\n\n#### Regularization\n\n* `EarlyStoppingEpoch`\n* `EarlyStoppingIteration`\n\n#### Checkpointing\n\n* `Checkpoint`\n* `CheckpointIteration`\n\n### Metrics\n\nCurrently only `BinaryAccuracy` is implemented. To implement other Metrics use the abstract base metric class `torchtrainer.metrics.metric.Metric`. \n\n## TODO\n\n- more tests\n- metrics\n\n\n## \n\n",
    'author': 'Victor Künstler',
    'author_email': 'victor.kuenstler@outlook.com',
    'url': 'https://github.com/VictorKuenstler/torchtrainer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
