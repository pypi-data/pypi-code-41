"""
This is a Handler Module with all the individual handlers for LSSTQuery
"""
import json
import nbformat
import os

import nbreport.templating as templ

from .templatemap import TEMPLATEMAP

from nbreport.repo import ReportRepo
from notebook.utils import url_path_join as ujoin
from notebook.base.handlers import APIHandler
from tempfile import TemporaryDirectory
from urllib.parse import urlparse


class LSSTQuery_handler(APIHandler):
    """
    LSSTQuery Parent Handler.
    """
    @property
    def lsstquery(self):
        return self.settings['lsstquery']

    def post(self):
        """
        POST a queryID and get back a prepopulated notebook.
        """
        post_data = json.loads(self.request.body.decode('utf-8'))
        # Do The Deed
        query_id = post_data["query_id"]
        query_type = post_data["query_type"]
        self.log.debug("Query_Type: {}".format(query_type))
        self.log.debug("Query_ID: {}".format(query_id))
        result = self._substitute_query(query_type, query_id)
        self.finish(json.dumps(result))

    def _substitute_query(self, query_type, query_id):
        top = os.environ.get("JUPYTERHUB_SERVICE_PREFIX")
        root = os.environ.get("HOME")
        fname = self._get_filename(query_type, query_id)
        fpath = "notebooks/queries/" + fname
        os.makedirs(root + "/notebooks/queries", exist_ok=True)
        filename = root + "/" + fpath
        retval = {
            "status": 404,
            "filename": filename,
            "path": fpath,
            "url": top + "/tree/" + fpath,
            "body": None
        }
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                nb = f.read().decode("utf-8")
        else:
            # We need to create the file from template
            try:
                nb = self._render_from_template(query_type, query_id)
                nbformat.write(nb, filename)
            except ValueError as exc:
                self.log.error("Render error: {}".format(exc))
        if nb:
            retval["status"] = 200
            retval["body"] = nb
        return retval

    def _render_from_template(self, query_type, query_id):
        template_map = TEMPLATEMAP.get(query_type)
        if not template_map:
            raise ValueError(
                "No template for query type '{}'!".format(query_type))
        template_url = template_map.get("url")
        branch = template_map.get("branch") or "master"
        subdir = template_map.get("subdir")
        if not template_url:
            raise ValueError(
                "No template URL for query type '{}'!".format(query_type))
        repo = None
        nb = None
        extra_context = self._get_extra_context(query_type, query_id)
        purl = urlparse(template_url)
        if not purl.netloc:
            # If there is no netloc, assume that the repository is already
            #  checked out to the given location
            repo = ReportRepo(purl.path)
            nb = self._render_notebook(repo, extra_context)
        else:
            with TemporaryDirectory() as td:
                repo = ReportRepo.git_clone(template_url,
                                            checkout=branch,
                                            subdir=subdir,
                                            clone_base_dir=td)
                nb = self._render_notebook(repo, extra_context)
        return nb

    def _render_notebook(self, repo, extra_context):
        context = templ.load_template_environment(
            repo.context_path,
            extra_context=extra_context
        )
        nb = repo.open_notebook()
        rendered_notebook = templ.render_notebook(nb, *context)
        return rendered_notebook

    def _get_filename(self, query_type, query_id):
        self.log.debug("Query Type: {} | Query ID: {}".format(query_id,
                                                              query_type))
        qn = query_id
        ul = urlparse(query_id)
        self.log.debug("Parsed Query ID: {}".format(ul))
        if ul.netloc:
            qn = ul.path
        qn = qn.split('/')[-1]
        if not qn:
            qn = "q"
        fname = "query-" + query_type + "-" + qn + ".ipynb"
        self.log.debug("Fname: {}".format(fname))
        return fname

    def _get_extra_context(self, query_type, query_id):
        context = {}
        if query_type == "api":
            context = {"query_url": query_id}
        elif query_type == "squash":
            context = {"ci_id": query_id}
        else:
            pass
        return context


def setup_handlers(web_app):
    """
    Function used to setup all the handlers used.
    """
    # add the baseurl to our paths
    host_pattern = '.*$'
    base_url = web_app.settings['base_url']
    handlers = [(ujoin(base_url, r'/lsstquery'), LSSTQuery_handler)]
    web_app.add_handlers(host_pattern, handlers)
