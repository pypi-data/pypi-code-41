# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['vbuild']

package_data = \
{'': ['*']}

install_requires = \
['pscript>=0.7.0,<0.8.0']

setup_kwargs = {
    'name': 'vbuild',
    'version': '0.8.1',
    'description': "A simple module to extract html/script/style from a vuejs '.vue' file (can minimize/es2015 compliant js) ... just py2 or py3, NO nodejs !",
    'long_description': '# vbuild\n\n"Compile" your [VueJS](https://vuejs.org/) components (*.vue) to standalone html/js/css ... python only, **no need of nodejs**. And you can use [python components](https://github.com/manatlan/vbuild/blob/master/doc/PyComponent.md) with **vbuild**, in your vue/sfc files !!!\n\nIt\'s just an utility to [generate](https://github.com/manatlan/vbuild/blob/master/doc/generate.md) HTML(template), SCRIPT and STYLE from a [VUE/SFC component]((https://fr.vuejs.org/v2/guide/single-file-components.html)) (*.vue). It won\'t replace webpack/nodejs/vue-cli, it fills the _"Sometimes you have to work with the tools you have, not the ones you want."_ gap.\n\n[DEMO](https://manatlan.alwaysdata.net/vbuild/)\n\n[Available on pypi](https://pypi.org/project/vbuild/)\n\n[Changelog](https://github.com/manatlan/vbuild/blob/master/changelog.md)\n\n## Features\n\n * **NO node-js stack**, only pure python (py2 or py3 compliant)\n * Ability to use [python components](https://github.com/manatlan/vbuild/blob/master/doc/PyComponent.md)\n * Components can be styled with [SASS or LESS ccs-pre-processors](https://github.com/manatlan/vbuild/blob/master/doc/CssPreProcess.md) !\n * Provide a [JS-minifier (ES5 compliant JS, via closure)](https://github.com/manatlan/vbuild/blob/master/doc/minimize.md)\n * Ability to [post process stuff](https://github.com/manatlan/vbuild/blob/master/doc/PostProcess.md), with your own processors\n * Respect [VueJs specs](https://vue-loader.vuejs.org/spec.html) (at least one template tag, many style (scoped or not) tags)\n * `templates` are converted to a `<script type="text/x-template" id="XXX"></script>` (not converted to JS)\n * Unittested (coverage 100%)\n * no import/from ! \n \n\n```python\nimport vbuild\n\nc=vbuild.render("mycompo.vue")\n#c=vbuild.render("vues/*.vue")\n#c=vbuild.render( "c1.vue", "c2.vue" )\n#c=vbuild.render( "c1.vue", "vues/*.vue" )\n\nprint( c.html )\nprint( c.script )\nprint( c.style )\n\n#or \n\nprint( c ) # all stuff in html tags\n\n```\n\n## Main Goal\n\nIts main purpose is to let you use components (.vue files) in your vuejs app, without a full nodejs stack. It\'s up to you to create your generator, to extract the things, and create your "index.html" file. It\'s a 4 lines of python code; example:\n\n```python\nimport vbuild\nbuf=readYourTemplate("index.tpl") # should contains a tag "<!-- HERE -->" that would be substituted\nbuf=buf.replace("<!-- HERE -->",str( vbuild.render( "vues/*.vue" ) ) )\nwriteYourTemplate("index.html",buf)\n```\n\n([a real example](https://github.com/manatlan/wuy/tree/master/examples/vueapp) of rendering vue/sfc components, using **vbuild** and the marvelous [wuy](https://github.com/manatlan/wuy))\n\n\n## Vue/sfc component compatibility\n\nAll classical JS vue/sfc components are compatibles. But now, you can use [python component](https://github.com/manatlan/vbuild/blob/master/doc/PyComponent.md) too. \n\nHere is, side by side, the same component (in js, and in python):\n\n<image src="https://raw.githubusercontent.com/manatlan/vbuild/master/doc/vs.png"/>\n\n## To use the full features of vbuild\n\nIf you want to use the full features, you\'ll need to install the optionnal\'s libs.\n\n```\nsudo pip install pyscss lesscpy closure\n```\n\nAll theses libs works with py2 and/or py3, and you could use the [css-pre-processors SASS and LESS](https://github.com/manatlan/vbuild/blob/master/doc/CssPreProcess.md), and [closure to minify js](https://github.com/manatlan/vbuild/blob/master/doc/minimize.md).\n\n## TODO\n\n * more utilities\n * more rock solid version\n * and docs !\n * add pyscss lesscpy closure to pip setup.py (optionnal\'s modules)\n * see the [TODO list for python components too](https://github.com/manatlan/vbuild/blob/master/doc/PyComponent.md)\n\n',
    'author': 'manatlan',
    'author_email': 'manatlan@gmail.com',
    'url': 'https://github.com/manatlan/vbuild',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
}


setup(**setup_kwargs)
