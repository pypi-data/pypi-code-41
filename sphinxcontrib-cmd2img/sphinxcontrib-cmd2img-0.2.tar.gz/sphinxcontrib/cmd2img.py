# -*- coding: utf-8 -*-
"""
    sphinxcontrib.cmd2img
    ~~~~~~~~~~~~~~~~~~~~~

    Allow cmd2img commands be rendered as nice looking images
    

    See the README file for details.

    :author: Vadim Gubergrits <vadim.gubergrits@gmail.com>
    :license: BSD, see LICENSE for details

    Inspired by ``sphinxcontrib-aafig`` by Leandro Lucarella.
"""

import re, os
import posixpath
from os import path
import copy
from subprocess import Popen, PIPE
import shlex
import imghdr
try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.errors import SphinxError
from sphinx.util import ensuredir, relative_uri

OWN_OPTION_SPEC = dict( { 'caption': str,
    'show_source': str,
    'watermark': str,
    'gravity': str,
    'location': str,
    'fill': str,
    'pointsize': str,
    'font': str})

class Cmd2imgError(SphinxError):
    category = 'cmd2img error'

class Cmd2figDirective(directives.images.Figure):
    """
    Directive that builds figure object.
    """
    has_content = True
    required_arguments = 0
    option_spec = directives.images.Figure.option_spec.copy()
    option_spec.update(OWN_OPTION_SPEC)
  
    def run(self):
        self.arguments = ['']
        total_options = self.options.copy()

        cmd = self.content[0]
        text = '\n'.join(self.content[1:])
        own_options = dict([(k,v) for k,v in self.options.items() 
                                  if k in OWN_OPTION_SPEC])

        # Remove the own options from self-options which will be as figure
        # options.
        for x in own_options.keys():
            self.options.pop(x)

        # don't parse the centent as legend, it's not legend.
        self.content = None

        (node,) = directives.images.Figure.run(self)
        if isinstance(node, nodes.system_message):
            return [node]

        node.cmd2img = dict(cmd=cmd,text=text,options=own_options,suffix="cmd2img",
                directive="cmd2fig", total_options=total_options)
        return [node]

class Cmd2imgDirective(directives.images.Image):
    """
    Directive that builds image object.
    """
    has_content = True
    required_arguments = 0
    option_spec = directives.images.Image.option_spec.copy()
    option_spec.update(OWN_OPTION_SPEC)
  
    def run(self):
        self.arguments = ['']
        #print ("%s start!self.options: %s" %(self.__class__.__name__, self.options))
        total_options = self.options.copy()

        # Parse the cmd/options/text
        cmd = self.content[0]
        own_options = dict([(k,v) for k,v in self.options.items() 
                                  if k in OWN_OPTION_SPEC])
        text = '\n'.join(self.content[1:])

        # Remove the own defined options from self-options, which will be as
        # figure options.
        for x in own_options.keys():
            self.options.pop(x)

        (node,) = directives.images.Image.run(self)
        if isinstance(node, nodes.system_message):
            return [node]

        node.cmd2img = dict(cmd=cmd,text=text,options=own_options,suffix="cmd2img",
                directive="cmd2img", total_options=total_options)
        return [node]

# http://epydoc.sourceforge.net/docutils/
def render_cmd2img_images(app, doctree):

    for fig in doctree.traverse(nodes.figure):
        if not hasattr(fig, 'cmd2img'):
            continue

        cmd = fig.cmd2img['cmd']
        text = fig.cmd2img['text']
        options = fig.cmd2img['options']

        try:
            #relfn, outfn, relinfile = cmd_2_image(app, fig.cmd2img)
            out = cmd_2_image(app, fig.cmd2img)
            caption_node = nodes.caption("", options.get("caption", cmd))
            fig += caption_node
            fig['ids'] = "cmd2fig"
            #img = fig.children[fig.first_child_matching_class(nodes.image)]
            for img in fig.traverse(condition=nodes.image):
                img['uri'] = out["outrelfn"]
                if out["outreference"]:
                    reference_node = nodes.reference(refuri=out["outreference"])
                    reference_node += img
                    fig.replace(img, reference_node)
                #img['candidates']={'*': out["outfullfn"]}

            #if options.get("show_source", False):
            #    # rendere as a text
            #    fig["align"] = "left"
            #    fig.insert(0, nodes.literal_block("", "%s\n%s" %(cmd, text), align = "left"))
            #print("rending figure: %s" %(fig))
        except Cmd2imgError as err:
            #app.builder.warn('cmd2img error: ')
            print(err)
            fig.replace_self(nodes.literal_block("", "%s\n%s" %(cmd, text)))
            continue

    for img in doctree.traverse(nodes.image):
        if not hasattr(img, 'cmd2img'):
            continue

        text = img.cmd2img['text']
        options = img.cmd2img['options']
        cmd = img.cmd2img['cmd']
        try:
            #relfn, outfn, relinfile = cmd_2_image(app, img.cmd2img)
            out = cmd_2_image(app, img.cmd2img)
            img['uri'] = out["outrelfn"]
            if out["outreference"]:
                reference_node = nodes.reference(refuri=out["outreference"])
                img.replace_self(reference_node)
                reference_node.append(img) 
            #if options.get("show_source", False):
            #    img.insert(0, nodes.literal_block("", "%s\n%s" %(cmd, text)))
        except Cmd2imgError as err:
            #app.builder.warn('cmd2img error: ')
            print(err)
            img.replace_self(nodes.literal_block("", "%s\n%s" %(cmd, text)))
            continue

def cmd_2_image (app, cmd2img):
    """Render cmd2img code into a PNG output file."""
    #print("app.builder.format: %s" %(app.builder.format))
    #print("app.builder.env.docname: %s" %(app.builder.env.docname))
    #print("app.builder.imagedir: %s" %(app.builder.imagedir))

    cmd = cmd2img['cmd']
    text = cmd2img['text']
    options = cmd2img['options']
    #print(cmd2img)
    format = app.builder.format

    out = dict(outrelfn=None,outfullfn=None,outreference=None)
    #out["outdir"] = app.builder.outdir

    cmd_args = shlex.split(cmd)
    #print("cmd_args: %s" %(cmd_args))
    rel_imgpath = relative_uri(app.builder.env.docname, app.builder.imagedir)
    hashkey = cmd + str(options) + text
    hashkey = sha(hashkey.encode('utf-8')).hexdigest()
    infname = '%s-%s.%s' % (cmd_args[0], hashkey, cmd2img['suffix'])
    infullfn = path.join(app.builder.outdir, app.builder.imagedir, infname)
    ensuredir(path.join(app.builder.outdir, app.builder.imagedir))

    # 1) prepare the input file and output file
    if text:
        # With body: wring the script to file and chdir to _image directory.
        outfname = '%s-%s.%s' % (cmd_args[0], hashkey, "png")
        out["outrelfn"] = posixpath.join(rel_imgpath, outfname)
        out["outfullfn"] = path.join(app.builder.outdir, app.builder.imagedir, outfname)
        out["outreference"] = posixpath.join(rel_imgpath, infname)

        if cmd_args[0] == "gnuplot":
            cmd_args.append(infullfn)
        elif cmd_args[0] == "ditaa":
            cmd_args.extend([infname, outfname])
        else:
            cmd_args.extend([infullfn, "-o", out["outfullfn"]])

        if not path.isfile(infullfn):
            with open(infullfn, 'wb') as f:
                if cmd_args[0] == "gnuplot":
                    # Gnuplot: the outfile is in the script insteading in the cmd line.
                    text = "set output '%s'\nset terminal pngcairo\n" %((out["outfullfn"])) + text
                f.write(text.encode('utf-8'))
    else:
        # shell command, not caculate the out file but not need the in file.
        t = os.path.splitext(cmd_args[-1])
        outfname = "%s-%s%s" %(t[0], hashkey, t[1])
        out["outrelfn"] = posixpath.join(rel_imgpath, outfname)
        out["outfullfn"] = path.join(app.builder.outdir, app.builder.imagedir, outfname)

        cmd_args[-1] = out["outfullfn"]
        if text or options.get("show_source", False) :
            # write the infile if it need to show the source.
            if not path.isfile(infullfn):
                with open(infullfn, 'wb') as f:
                    f.write(cmd.encode('utf-8'))


    # 2) generate the output file
    if not path.isfile(out["outfullfn"]):
        currpath = os.getcwd()
        if cmd_args[0] == "ditaa":
            # Ditaa don't support absolute dir, change the dir. others might have input files
            os.chdir(path.join(app.builder.outdir, app.builder.imagedir))
        else:
            os.chdir(path.join(currpath, os.path.dirname(app.builder.env.docname)))

        try:
            print(' '.join(cmd_args))
            #print(cmd_args)
            p = Popen(cmd_args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
            os.chdir(currpath)
            stdout, stderr = (p.stdout.read().decode("utf-8"), p.stderr.read().decode("utf-8"))
            if stderr:
                raise Cmd2imgError('"%s" exited with error: [1;31m%s[0m' % (cmd, stderr))
        except OSError as err:
            os.chdir(currpath)
            raise Cmd2imgError('"%s" exited with error: [1;31m%s[0m' %(cmd, err))

    # 3) Check if it's need to generate the outreference file
    if options.get("watermark", None):
        # Add watermark onto the image:
        if text or options.get("show_source", False):
            out["outreference"] = posixpath.join(rel_imgpath, infname)
        else:
            out["outreference"] = out["outrelfn"]

        if not path.isfile(out["outreference"]):
            t = os.path.splitext(outfname)
            outfname = "%s-watermark%s" %(t[0], t[1])
            outrelfn = posixpath.join(rel_imgpath, outfname)
            outfullfn = path.join(app.builder.outdir, app.builder.imagedir, outfname)
            c = ['convert', out["outfullfn"],
                    #'-resize', "600x400",
                    '-gravity', options.get("gravity", 'northeast'),
                    '-fill', options.get("fill", 'black'),
                    '-pointsize', options.get("pointsize", '23'),
                    '-draw', '%s' %(options["watermark"]),
                    outfullfn]
            try:
                p = Popen(c, stdout=PIPE, stdin=PIPE, stderr=PIPE)
                stdout, stderr = (p.stdout.read().decode("utf-8"), p.stderr.read().decode("utf-8"))
                if stderr:
                    raise Cmd2imgError('convert exited with error: [1;31m%s[0m' % (stderr))
                out["outrelfn"] = outrelfn
                out["outfullfn"] = outfullfn
            except OSError as err:
                print('%s exited with error: [1;31m%s[0m' %(c, err))
    elif text or options.get("show_source", False):
        # Input file could be rendered as a link
        out["outreference"] = posixpath.join(rel_imgpath, infname)

    # 4) latex pdf don't support gif image, convert it to jpg
    if format == "latex" and imghdr.what(out["outfullfn"]) == "gif":
    #if format == "latex" and os.path.splitext(out["outrelfn"])[1] == ".gif":
        original = out["outfullfn"]
        out["outrelfn"] = os.path.splitext(out["outrelfn"])[0] + ".jpg"
        out["outfullfn"] = os.path.splitext(out["outfullfn"])[0] + ".jpg"
        c = ['convert', "%s[0]" %(original), out["outfullfn"]]
        try:
            p = Popen(c, stdout=PIPE, stdin=PIPE, stderr=PIPE)
            print('latex gif to jpg: %s ' %(out["outrelfn"]))
            stdout, stderr = (p.stdout.read().decode("utf-8"), p.stderr.read().decode("utf-8"))
            if stderr:
                raise Cmd2imgError('"%s" exited with error: [1;31m%s[0m' % (cmd, stderr))
        except OSError as err:
            print('%s exited with error: [1;31m%s[0m' %(c, err))

    #print(out)
    return out

def setup(app):
    app.add_directive('cmd2fig', Cmd2figDirective)
    app.add_directive('cmd2img', Cmd2imgDirective)
    app.connect('doctree-read', render_cmd2img_images)
    app.add_config_value('cmd2img', 'cmd2img', 'html')
    app.add_config_value('cmd2img_args', [], 'html')
    app.add_config_value('cmd2img_log_enable', True, 'html')

#https://blog.csdn.net/wangchaoqi1985/article/details/80461850
