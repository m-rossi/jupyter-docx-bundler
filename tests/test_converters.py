from jupyter_docx_bundler import converters
import nbformat
import os
import pytest
import re
import requests


@pytest.fixture(params=['https://nbviewer.jupyter.org/github/unpingco/Python-f'
                        'or-Signal-Processing/blob/master/More_Fourier_Transfo'
                        'rm.ipynb',
                        'https://nbviewer.jupyter.org/github/CamDavidsonPilon/'
                        'Probabilistic-Programming-and-Bayesian-Methods-for-Ha'
                        'ckers/blob/master/Chapter1_Introduction/Ch1_Introduct'
                        'ion_PyMC3.ipynb',
                        'https://nbviewer.jupyter.org/github/waltherg/notebook'
                        's/blob/master/2013-12-03-Crank_Nicolson.ipynb'],
                scope='module')
def download_notebook(request):
    notebook_url = request.param

    # check extension of file
    filename = os.path.basename(notebook_url)
    if not notebook_url.endswith('.ipynb'):
        raise ValueError('{} is not a Jupyter notebook.'.format(filename))

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


@pytest.fixture(params=[pytest.lazy_fixture('download_notebook')])
def notebook(request):
    return request.param


def test_notebook_to_html(tmpdir, notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    converters.notebook_to_html(notebook, htmlfile)


def test_html_to_docx(tmpdir, notebook):
    # convert notebook to HTML
    htmlfile = os.path.join(tmpdir, 'notebook.html')
    converters.notebook_to_html(notebook, htmlfile)

    # convert notebook to DOCX
    docxfile = os.path.join(tmpdir, 'notebook.docx')
    converters.html_to_docx(htmlfile, docxfile)
