from notebook.utils import url_path_join as ujoin
from notebook.log import log_request
from tornado.web import RequestHandler
from civis_jupyter_notebooks.git_utils import CivisGit, CivisGitError


class UncommittedChangesHandler(RequestHandler):
    def _log(self):
        log_func(self)

    def get(self):
        response = dict()
        civis_git = CivisGit()

        if not civis_git.is_git_enabled():
            self.set_status(404, 'Not a git enabled notebook')
        else:
            has_changes = False
            try:
                has_changes = civis_git.has_uncommitted_changes()
            except CivisGitError:
                pass

            response['dirty'] = has_changes
            self.set_status(200)
        self.finish(response)


def log_func(handler):
    if handler.get_status() != 404:
        log_request(handler)


def load_jupyter_server_extension(nbapp):
    nbapp.log.info('Uncommitted Changes Ext. Loaded')

    webapp = nbapp.web_app
    base_url = webapp.settings['base_url']
    webapp.add_handlers(".*$", [
        (ujoin(base_url, r"/git/uncommitted_changes"), UncommittedChangesHandler),
    ])
