import base64
import os
import platform
import re

import matplotlib.pyplot as plt
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat
import numpy as np
import pytest
import requests

from .. import converters


def encode_image_base64(filepath):
    """Encode an image as a base64 string

    Parameters
    ----------
    filepath : str
        Filepath of the image file

    Returns
    -------
    dict
        Dictionary with identifier as key and base64-encoded data as value.

    """
    key = 'image/' + os.path.splitext(filepath)[1][1:]
    with open(filepath, 'rb') as image:
        data = base64.b64encode(image.read()).decode('utf8')

    return {key: data}


@pytest.fixture(params=['https://nbviewer.jupyter.org/github/unpingco/Python-f'
                        'or-Signal-Processing/blob/master/More_Fourier_Transfo'
                        'rm.ipynb',
                        'https://nbviewer.jupyter.org/github/CamDavidsonPilon/'
                        'Probabilistic-Programming-and-Bayesian-Methods-for-Ha'
                        'ckers/blob/master/Chapter1_Introduction/Ch1_Introduct'
                        'ion_PyMC3.ipynb',
                        'https://nbviewer.jupyter.org/github/waltherg/notebook'
                        's/blob/master/2013-12-03-Crank_Nicolson.ipynb'])
def download_notebook(request):
    notebook_url = request.param

    # check extension of file
    filename = os.path.basename(notebook_url)
    if not notebook_url.endswith('.ipynb'):
        raise ValueError(f'{filename} is not a Jupyter notebook.')

    # redirect notebook if notebook is located on nbviewer.jupyter.org
    if 'nbviewer' in notebook_url:
        r = requests.get(notebook_url)
        link = re.findall('(?<=<a href=").+(?=" title="Download Notebook" '
                          'download>)', r.content.decode('utf8'))
        if len(link) > 0:
            notebook_url = link[0]

    # download notebook
    r = requests.get(notebook_url)
    return nbformat.reads(r.content.decode('utf8'), 4)


@pytest.fixture(params=[100, 1000])
def matplotlib_notebook(tmpdir, request):
    nb = nbformat.v4.new_notebook()

    nb.cells.append(nbformat.v4.new_code_cell('\n'.join(
        ['import numpy as np',
         'import matplotlib.pyplot as plt',
         '% matplotlib inline'])))

    for _ in range(request.param):
        nb.cells.append(nbformat.v4.new_code_cell('\n'.join(
            ['plt.figure(dpi=100)',
             'plt.plot(np.linspace(0, 1), np.power(np.linspace(0, 1), 2))',
             'plt.show()'])))

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture(params=['png', 'jpg', 'jpeg'])
def embedded_images_notebook(tmpdir, request):
    nb = nbformat.v4.new_notebook()

    filename = 'matplotlib.' + request.param

    plt.figure()
    plt.plot(np.linspace(0, 1), np.power(np.linspace(0, 1), 2))
    if platform.system() == 'Windows' and request.param is not 'png':
        pytest.skip('Image export only works for png on Windows.')
    plt.savefig(os.path.join(tmpdir, filename))

    nb.cells.append(nbformat.v4.new_markdown_cell('\n'.join(
        ['line1',
         '![' + filename + '](attachment:' + filename + ')',
         'line3'])))

    nb.cells[-1]['attachments'] = \
        {filename: encode_image_base64(os.path.join(tmpdir, filename))}

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


def test_notebook_to_html_download(tmpdir, download_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    converters.notebook_to_html(download_notebook, htmlfile)


def test_notebook_to_html_matplotlib(tmpdir, matplotlib_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    converters.notebook_to_html(matplotlib_notebook, htmlfile)


def test_notebook_to_html_embedded_images(tmpdir, embedded_images_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    converters.notebook_to_html(embedded_images_notebook, htmlfile)


def test_html_to_docx_download(tmpdir, download_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    converters.notebook_to_html(download_notebook, htmlfile)

    # convert notebook to DOCX
    docxfile = os.path.join(tmpdir, 'notebook.docx')
    converters.html_to_docx(htmlfile, docxfile)


def test_html_to_docx_matplotlib(tmpdir, matplotlib_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    converters.notebook_to_html(matplotlib_notebook, htmlfile)

    # convert notebook to DOCX
    docxfile = os.path.join(tmpdir, 'notebook.docx')
    converters.html_to_docx(htmlfile, docxfile)


def test_html_to_docx_embedded_images(tmpdir, embedded_images_notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    converters.notebook_to_html(embedded_images_notebook, htmlfile)

    # convert notebook to DOCX
    docxfile = os.path.join(tmpdir, 'notebook.docx')
    converters.html_to_docx(htmlfile, docxfile)
