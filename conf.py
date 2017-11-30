#!/usr/bin/env python3
import datetime
import subprocess

project = 'Astronaut Training Program'
project_slug = 'astronaut-training-program'
description = 'Astronaut Training Program'
author = 'Matt Harasymczuk'
copyright = '2014-{year}, Matt Harasymczuk <matt@astronaut.center>'.format(year=datetime.date.today().year)

extensions = [
    # 'sphinx.ext.autodoc',
    # 'sphinx.ext.doctest',
    # 'sphinx.ext.githubpages',
    'sphinx.ext.todo',
    # 'sphinx.ext.coverage',
    # 'sphinx.ext.imgmath',
    # 'sphinx.ext.viewcode',
]

language = 'en'
master_doc = 'index'
today_fmt = '%Y-%m-%d'
source_suffix = ['.rst']
imgmath_image_format = 'svg'
exclude = ['README.rst']

todo_emit_warnings = True
todo_include_todos = False

numfig = True
numfig_format = {
    'section': 'Sect. %s',
    'figure': 'Fig. %s',
    'table': 'Tab. %s',
    'code-block': 'List. %s',
}

def get_version():
    shell = subprocess.Popen('git log -1 --format="%h"', stdout=subprocess.PIPE, shell=True)
    return '{sha1}, {date:%Y-%m-%d}'.format(
        sha1=shell.stdout.read().decode().replace('\n', ''),
        date=datetime.date.today(),
    )

version = get_version()
release = get_version()


highlight_language = 'python3'
pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
html_show_sphinx = False
htmlhelp_basename = project


htmlhelp_basename = project_slug
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '10pt',
    'figure_align': 'htbp',

    # Fix for: LaTeX Backend Fails with Citations In Figure Captions
    'preamble': r'''
        \usepackage{etoolbox}
        \AtBeginEnvironment{figure}{\renewcommand{\phantomsection}{}}
    '''
}

latex_documents = [
    (master_doc, 'document.tex', project, author, 'manual'),
]

man_pages = [
    (master_doc, project_slug, project, [author], 1)
]

texinfo_documents = [
    (master_doc, project_slug, project, author, project_slug, description, 'Miscellaneous'),
]
