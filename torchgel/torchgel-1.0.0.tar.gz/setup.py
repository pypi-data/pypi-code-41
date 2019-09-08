# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['gel']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.10,<2.0', 'tqdm>=4.0,<5.0']

extras_require = \
{'test': ['scipy', 'cvxpy>=1.0,<2.0', 'cvxopt']}

setup_kwargs = {
    'name': 'torchgel',
    'version': '1.0.0',
    'description': 'PyTorch implementation of group elastic net',
    'long_description': "# torch-gel\n\nThis package provides PyTorch implementations to solve the group elastic net\nproblem. Let _A<sub>j</sub>_ (_j = 1 … p_) be feature matrices of sizes _m ×\nn<sub>j</sub>_ (_m_ is the number of samples, and _n<sub>j</sub>_ is the number\nof features in the _j_<sup>th</sup> group), and let _y_ be an _m × 1_ vector of\nthe responses. Group elastic net finds coefficients _β<sub>j</sub>_, and a bias\n_β<sub>0</sub>_ that solve the optimization problem\n\n> min _<sub>β<sub>0</sub>, …, β<sub>p</sub></sub>_\n>     _½ ║y - β<sub>0</sub> - ∑ A<sub>j</sub> β<sub>j</sub>║<sup>2</sup>_\n>     + _m ∑ √n<sub>j</sub> (λ<sub>1</sub>║β<sub>j</sub>║_\n>                           _+ λ<sub>2</sub>║β<sub>j</sub>║<sup>2</sup>)._\n\nHere _λ<sub>1</sub>_ and _λ<sub>2</sub>_ are scalar coefficients that control\nthe amount of 2-norm and squared 2-norm regularization. This 2-norm\nregularization encourages sparsity at the group level; entire _β<sub>j</sub>_\nmight become 0. The squared 2-norm regularization is in similar spirit to\nelastic net, and addresses some of the issues of lasso. Note that group elastic\nnet includes as special cases group lasso (_λ<sub>2</sub> = 0_), ridge\nregression (_λ<sub>1</sub> = 0_), elastic net (each _n<sub>j</sub> = 1_), and\nlasso (each _n<sub>j</sub> = 1_ and _λ<sub>2</sub> = 0_). The optimization\nproblem is convex, and can be solved efficiently. This package provides two\nimplementations; one based on proximal gradient descent, and one based on\ncoordinate descent.\n\n## Installation\nInstall with `pip`\n\n```bash\npip install torchgel\n```\n\n`tqdm` (for progress bars), and numpy are pulled in as dependencies. PyTorch\n(`v1.0+`) is also needed, and needs to be installed manually. Refer to the\n[PyTorch website](<http://pytorch.org>) for instructions.\n\n## Usage\n[`examples/main.ipynb`](examples/main.ipynb) is a Jupyter notebook that walks\nthrough using the package for a typical use-case. A more formal description of\nthe functions follows; and for details about the algorithms, refer to the\ndocstrings of files in the `gel` directory.\n\n### Solving Single Instances\nThe modules `gel.gelfista` and `gel.gelcd` provide implementations based on\nproximal gradient descent and coordinate descent respectively. Both have similar\ninterfaces, and expose two main public functions: `make_A` and `gel_solve`. The\nfeature matrices should be stored in a list (say `As`) as PyTorch tensor\nmatrices, and the responses should be stored in a PyTorch vector (say `y`).\nAdditionally, the sizes of the groups (_n<sub>j</sub>_) should be stored in a\nvector (say `ns`). First use the `make_A` function to convert the feature\nmatrices into a suitable format:\n\n```python\nA = make_A(As, ns)\n```\n\nThen pass `A`, `y` and other required arguments to `gel_solve`. The general\ninterface is::\n\n```python\nb_0, B = gel_solve(A, y, l_1, l_2, ns, **kwargs)\n```\n\n`l_1` and `l_2` are floats representing _λ<sub>1</sub>_ and _λ<sub>2</sub>_\nrespectively. The method returns a float `b_0` representing the bias and a\nPyTorch matrix `B` holding the other coefficients. `B` has size _p ×_\nmax<sub>_j_</sub> _n<sub>j</sub>_ with suitable zero padding. The following\nsections cover additional details for the specific implementations.\n\n#### Proximal Gradient Descent (FISTA)\nThe `gel.gelfista` module contains a proximal gradient descent implementation.\nIt's usage is just as described in the template above. Refer to the docstring\nfor `gel.gelfista.gel_solve` for details about the other arguments.\n\n#### Coordinate Descent\nThe `gel.gelcd` module contains a coordinate descent implementation. Its usage\nis a bit more involved than the FISTA implementation. Coordinate descent\niteratively solves single blocks (each corresponding to a single\n_β<sub>j</sub>_). There are multiple solvers provided to solve the individual\nblocks. These are the `gel.gelcd.block_solve_*` functions. Refer to their\ndocstrings for details about their arguments. `gel.gelcd.gel_solve` requires\npassing a block solve function and its arguments (as a dictionary). Refer to\nits docstring for further details.\n\n### Solution Paths\n`gel.gelpaths` provides a wrapper function `gel_paths` to solve the group\nelastic net problem for multiple values of the regularization coefficients. It\nimplements a two-stage process. For a given _λ<sub>1</sub>_ and _λ<sub>2</sub>_,\nfirst the group elastic net problem is solved and the feature blocks with\nnon-zero coefficients is extracted (the support). Then ridge regression models\nare learned for each of several provided regularization values. The final model\nis summarized using an arbitrary provided summary function, and the summary for\neach combination of the regularization values is returned as a dictionary. The\ndocstring contains more details. `gel.ridgepaths` contains another useful function,\n`ridge_paths` which can efficiently solve ridge regression for multiple\nregularization values.\n\n## Citation\nIf you find this code useful in your research, please cite\n\n```\n@misc{koushik2017torchgel,\n  author = {Koushik, Jayanth},\n  title = {torch-gel},\n  year = {2017},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/jayanthkoushik/torch-gel}},\n}\n```\n",
    'author': 'Jayanth Koushik',
    'author_email': 'jnkoushik@gmail.com',
    'url': 'https://github.com/jayanthkoushik/torch-gel',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
