#!/usr/bin/env python3

import sys
import os
import datetime
import subprocess


sys.path.append(os.path.abspath('.'))

def get_version():
    return '#{sha1}, {date:%Y-%m-%d}'.format(
        sha1=subprocess.Popen('git log -1 --format="%h"', stdout=subprocess.PIPE, shell=True).stdout.read().decode().replace('\n', ''),
        date=datetime.date.today(),
    )


project = 'Astronaut Training Program'
author = 'Matt Harasymczuk'

extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.imgmath',
]

language = 'en'
copyright = '2012-{date:%Y}, Matt Harasymczuk <matt@astromatt.space>'.format(date=datetime.date.today())
master_doc = 'index'
today_fmt = '%Y-%m-%d'
source_suffix = ['.rst']

version = get_version()
release = get_version()

html_theme = 'sphinx_rtd_theme'
html_sidebars = {'sidebar': ['localtoc.html', 'sourcelink.html', 'searchbox.html']}
html_show_sphinx = False
htmlhelp_basename = project


latex_elements = {}
latex_documents = [
  (master_doc, 'Astronaut-Training-Program.tex', 'Astronaut Training Program', 'Matt Harasymczuk', 'manual'),
]

texinfo_documents = [
  (master_doc, 'Astronaut-Training-Program', 'Astronaut Training Program', author, 'Astronaut Training Program', '', 'Miscellaneous'),
]

