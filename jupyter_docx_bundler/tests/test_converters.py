import os

import pytest

from .. import converters


def test_preprocess(tmpdir, test_notebook):
    converters.preprocess(test_notebook)


def test_notebook_to_html(tmpdir, test_notebook):
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    preprocessed_notebook = converters.preprocess(test_notebook)
    converters.notebook_to_html(preprocessed_notebook, htmlfile)


def test_html_to_docx(tmpdir, test_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    preprocessed_notebook = converters.preprocess(test_notebook)
    converters.notebook_to_html(preprocessed_notebook, htmlfile)

    # convert notebook to DOCX
    docxfile = os.path.join(tmpdir, 'notebook.docx')
    converters.html_to_docx(htmlfile, docxfile, metadata=preprocessed_notebook['metadata'])


def test_html_to_docx_missing_path(tmpdir, test_notebook):
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    docxfile = os.path.join(tmpdir, 'notebook.docx')
    test_notebook = converters.preprocess(test_notebook)
    converters.notebook_to_html(test_notebook, htmlfile)
    with pytest.raises(FileNotFoundError):
        converters.html_to_docx('not/existing.html', docxfile)
    with pytest.raises(FileNotFoundError):
        converters.html_to_docx(htmlfile, 'not/existing.docx')


def test_notebookcontent_to_docxbytes(test_notebook):
    converters.notebookcontent_to_docxbytes(test_notebook, 'download-notebook')
