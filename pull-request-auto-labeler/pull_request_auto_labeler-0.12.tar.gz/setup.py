from setuptools import setup

with open('README.md', 'rb') as f:
    README = f.read().decode('utf-8')

setup(
    name='pull_request_auto_labeler',
    version='0.12',
    url='https://github.com/markddavidoff/pull_request_auto_labeler',
    author='Mark Davidoff',
    author_email='markddavidoff@gmail.com',
    description='Automatically label Github pull requests based on elements of the PR title. Expects Jira style ticket code(PROJ-100) in PR title',
    long_description=README,
    long_description_content_type="text/markdown",
    py_modules=['pull_request_auto_labeler'],
    license='MIT',
    install_requires=[
        'github3.py==1.2.0',
        'tqdm==4.33.0'
    ],
    entry_points='''
        [console_scripts]
        pull_request_auto_labeler=pull_request_auto_labeler:add_labels_for_project_names_from_pr_titles
    '''
)
