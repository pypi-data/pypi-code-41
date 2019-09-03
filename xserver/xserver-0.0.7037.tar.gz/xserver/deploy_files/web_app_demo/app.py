#coding: utf8
from __future__ import absolute_import
from flask import Flask


app = Flask(__name__)


@app.route('/')
def homepage():
    return 'hello world, xserver demo.'
