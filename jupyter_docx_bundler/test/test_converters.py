import os

import pytest

from .. import converters


def test_notebook_to_html_exportpath(download_notebook):
    with pytest.raises(FileNotFoundError):
        converters.notebook_to_html(download_notebook, 'not/existing.html')


def test_html_to_docx(tmpdir, download_notebook):
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    docxfile = os.path.join(tmpdir, 'notebook.docx')
    download_notebook = converters.preprocess(download_notebook)
    converters.notebook_to_html(download_notebook, htmlfile)
    with pytest.raises(FileNotFoundError):
        converters.html_to_docx('not/existing.html', docxfile)
    with pytest.raises(FileNotFoundError):
        converters.html_to_docx(htmlfile, 'not/existing.docx')


def test_notebook_to_html_download(tmpdir, download_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    download_notebook = converters.preprocess(download_notebook)
    converters.notebook_to_html(download_notebook, htmlfile)


def test_notebook_to_html_matplotlib(tmpdir, matplotlib_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    matplotlib_notebook = converters.preprocess(matplotlib_notebook)
    converters.notebook_to_html(matplotlib_notebook, htmlfile)


def test_notebook_to_html_embedded_images(tmpdir, embedded_images_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    embedded_images_notebook = converters.preprocess(embedded_images_notebook)
    converters.notebook_to_html(embedded_images_notebook, htmlfile)


def test_html_to_docx_download(tmpdir, download_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    download_notebook = converters.preprocess(download_notebook)
    converters.notebook_to_html(download_notebook, htmlfile)

    # convert notebook to DOCX
    docxfile = os.path.join(tmpdir, 'notebook.docx')
    converters.html_to_docx(htmlfile, docxfile, metadata=download_notebook['metadata'])


def test_html_to_docx_matplotlib(tmpdir, matplotlib_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    matplotlib_notebook = converters.preprocess(matplotlib_notebook)
    converters.notebook_to_html(matplotlib_notebook, htmlfile)

    # convert notebook to DOCX
    docxfile = os.path.join(tmpdir, 'notebook.docx')
    converters.html_to_docx(htmlfile, docxfile, metadata=matplotlib_notebook['metadata'])


def test_html_to_docx_embedded_images(tmpdir, embedded_images_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    embedded_images_notebook = converters.preprocess(embedded_images_notebook)
    converters.notebook_to_html(embedded_images_notebook, htmlfile)

    # convert notebook to DOCX
    docxfile = os.path.join(tmpdir, 'notebook.docx')
    converters.html_to_docx(htmlfile, docxfile, metadata=embedded_images_notebook['metadata'])


def test_notebookcontent_to_docxbytes_download(download_notebook):
    converters.notebookcontent_to_docxbytes(download_notebook, 'download-notebook')


def test_notebookcontent_to_docxbytes_matplotlib(matplotlib_notebook):
    converters.notebookcontent_to_docxbytes(matplotlib_notebook, 'matplotlib-notebook')


def test_notebookcontent_to_docxbytes(embedded_images_notebook):
    converters.notebookcontent_to_docxbytes(embedded_images_notebook, 'embedded-images-notebook')


def test_html_to_docx_authors(tmpdir, authors_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    download_notebook = converters.preprocess(authors_notebook)
    converters.notebook_to_html(download_notebook, htmlfile)

    # convert notebook to DOCX
    docxfile = os.path.join(tmpdir, 'notebook.docx')
    converters.html_to_docx(htmlfile, docxfile, metadata=download_notebook['metadata'])
