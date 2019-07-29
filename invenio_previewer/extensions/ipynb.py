# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Jupyter Notebook previewer."""

from __future__ import absolute_import, unicode_literals

from uuid import uuid4
import nbformat
from flask import make_response, render_template
from nbconvert import HTMLExporter

from ..utils import sanitize_html


def render(file):
    """Generate the result HTML."""
    with file.open() as fp:
        content = fp.read()

    notebook = nbformat.reads(content.decode('utf-8'), as_version=4)

    html_exporter = HTMLExporter()
    html_exporter.template_file = 'basic'
    (body, resources) = html_exporter.from_notebook_node(notebook)
    return body, resources


def can_preview(file):
    """Determine if file can be previewed."""
    return file.is_local() and file.has_extensions('.ipynb')


def preview(file):
    """Render the IPython Notebook."""
    body, resources = render(file)
    default_jupyter_nb_style = resources['inlining']['css'][1]
    nonce = str(uuid4())
    resp = make_response(render_template(
        'invenio_previewer/ipynb.html',
        file=file,
        content=body,
        inline_style=default_jupyter_nb_style,
        nonce=nonce
    ))
    csp_header = "script-src cdn.mathjax.org 'nonce-{}';".format(nonce)
    resp.headers['Content-Security-Policy'] = csp_header
    resp.headers['X-Webkit-CSP'] = csp_header
    # IE10 doesn't have proper CSP support, so we need to be more strict
    resp.headers['X-Content-Security-Policy'] = "sandbox allow-same-origin;"
    return resp
