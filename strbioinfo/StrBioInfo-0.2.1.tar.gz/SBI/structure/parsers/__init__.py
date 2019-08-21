# -*-
#
# @author: jaumebonet
# @email:  jaume.bonet@gmail.com
# @url:    jaumebonet.github.io
#
# @date:   2016-02-16 09:57:33
#
# @last modified by:   jaumebonet
# @last modified time: 2016-02-16 10:51:09
#
# -*-
"""
.. module:: parsers
   :platform: Unix, MacOs
   :synopsis: Objects to read and write from and to mmJSON

.. moduleauthor:: Jaume Bonet <jaume.bonet@gmail.com>

Based on the `mmJSON definition <http://pdbj.org/help/mmjson>`_, any format will
be transformed to and from **mmJSON**. This will be, then, the format that the
:py:class:`structure.PDB <SBI.structure.PDB>` class will be able to read from.

As it is clear by the name, the **mmJSON** is a plain dictionary object.

"""
