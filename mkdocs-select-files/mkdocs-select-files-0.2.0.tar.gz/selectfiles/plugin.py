import re
import logging
from mkdocs.plugins import BasePlugin
import mkdocs.structure

logger = logging.getLogger("mkdocs.plugin.select-files")

class SelectFiles(BasePlugin):

    config_scheme = (
        ('select', mkdocs.config.config_options.Type(mkdocs.utils.string_types, default='(\d+)')),
        ('where', mkdocs.config.config_options.Type(mkdocs.utils.string_types, default='lambda x: int(x) >= 0')),
    )

    def on_files(self, files, **kwargs):
        logger.debug("Filtering files")
        
        try:
            select = re.compile(self.config["select"])
        except Exception as e:
            logger.error("Error parsing select regular expression : %s", e)
            return files
        
        try:
            where = eval(self.config["where"])
        except Exception as e:
            logger.error("Error evaluating where expression : %s", e)
            return files

        def ok(path):
            m = select.search(path)
            if m:
                args = m.groups()
                if where(*args):
                    logger.debug("MATCH : %s", path)
                    return True
                else:
                    logger.debug("DROP : %s", path)
                    return False
            else:
                logger.debug("PASS : %s", f.src_path)
                return True

        res = []
        for f in files:
            try:
                t = ok(f.src_path)
            except Exception as e:
                logger.error("Error evaluating regular expression : %s", e)
                t = True

            if t:
                res.append(f)

        return mkdocs.structure.files.Files(res)
