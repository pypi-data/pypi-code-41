import logging
import os
import re
import sys

from tqdm import tqdm
from github3 import login

try:
    GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']
    ORGANIZATION = os.environ['ORGANIZATION']
    # PROJECT-100, [project2-900], etc
    LABEL_EXTRACTING_REGEX = os.environ[r'\s*[\[]*([a-zA-Z0-9]{2,})[-|\s][0-9]+']
except KeyError as error:
    sys.stderr.write('Please set the environment variable {0}'.format(error))
    sys.exit(1)

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def get_issues_that_are_prs(repository):
    # GitHub's REST API v3 considers every pull request an issue, but not every issue is a pull request.
    # For this reason, "Issues" endpoints may return both issues and pull requests in the response.
    # You can identify pull requests by the pull_request key.
    # In order to access labels we have to treat pull requests as issues
    issues_that_are_prs = []
    for issue in repository.issues(state='open', sort='created'):
        if issue.pull_request_urls:
            issues_that_are_prs.append(issue)
    return issues_that_are_prs


RE_TICKET_CODE = re.compile(LABEL_EXTRACTING_REGEX)

MISSING_PROJECT_NAME_LABEL = 'NO JIRA TICKET'


def get_ticket_codes_from_issue(issue):
    # PROJECT-100, project2-900, etc
    return RE_TICKET_CODE.findall(issue.title)


def get_project_names(issue):
    # PROJECT1, PROJECT2
    ticket_codes = get_ticket_codes_from_issue(issue)
    return [code.split('-')[0].upper() for code in ticket_codes]


def add_labels_for_project_names_from_pr_titles(show_progress_bar=True):
    client = login(token=GITHUB_API_TOKEN)
    organization = client.organization(ORGANIZATION)
    repos_iterator = organization.repositories()
    log = logger.info
    if show_progress_bar:
        log = tqdm.write
        repos_iterator = tqdm(list(repos_iterator), desc=f'Repos in {ORGANIZATION}')
    log(f"Getting all repos in {ORGANIZATION}...")
    for repository in repos_iterator:
        issues_that_are_prs = get_issues_that_are_prs(repository)
        if show_progress_bar:
            issues_that_are_prs = tqdm(issues_that_are_prs, desc=f'PRs in   {repository.full_name}')

        log(f"Getting all PRs in {repository.full_name}...")
        for issue in issues_that_are_prs:
            project_names = get_project_names(issue)
            if project_names:
                log(f'Updating PR {issue.id}-{issue.title} with labels {project_names}')
                issue.add_labels(*project_names)
            elif MISSING_PROJECT_NAME_LABEL:
                log(f'Updating PR {issue.id}-{issue.title} with label {MISSING_PROJECT_NAME_LABEL}')
                issue.add_labels(MISSING_PROJECT_NAME_LABEL)


def lambda_handler(event, context):
    add_labels_for_project_names_from_pr_titles(show_progress_bar=False)
    response = {
        "statusCode": 200,
        "body": "OK"
    }

    return response


if __name__ == '__main__':
    add_labels_for_project_names_from_pr_titles()
