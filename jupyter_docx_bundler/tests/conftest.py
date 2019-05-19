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
    # TODO Remove when matplotlib 3.04 or 3.1 is released
    if platform.system() == 'Darwin':
        pytest.skip('matplotlib is currently broken on Mac OS X, see https://github.com/matplotlib'
                    '/matplotlib/issues/13096')
    nb = nbformat.v4.new_notebook()

    nb.cells.append(nbformat.v4.new_code_cell('\n'.join(
        ['import matplotlib.pyplot as plt',
         '%matplotlib inline'])))

    for _ in range(request.param):
        nb.cells.append(nbformat.v4.new_code_cell('\n'.join(
            ['plt.figure(dpi=100)',
             'plt.plot(range(100))',
             'plt.show()'])))

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture(params=['png', 'jpg', 'jpeg'])
def embedded_images_notebook(tmpdir, request):
    # TODO Remove when matplotlib 3.04 or 3.1 is released
    if platform.system() == 'Darwin':
        pytest.skip('matplotlib is currently broken on Mac OS X, see https://github.com/matplotlib'
                    '/matplotlib/issues/13096')
    nb = nbformat.v4.new_notebook()

    filename = 'matplotlib.' + request.param

    plt.figure()
    plt.plot(np.linspace(0, 1), np.power(np.linspace(0, 1), 2))
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


@pytest.fixture()
def metadata_notebook(tmpdir):
    nb = nbformat.v4.new_notebook()

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    nb['metadata'].update({
        "authors": [
            {"name": "author1"},
            {"name": "author2"}
        ],
        "subtitle": 'subtitle',
        "date": '2019-05-11',
    })

    return nb


@pytest.fixture(params=[
    pytest.lazy_fixture('download_notebook'),
    pytest.lazy_fixture('matplotlib_notebook'),
    pytest.lazy_fixture('embedded_images_notebook'),
    pytest.lazy_fixture('metadata_notebook')
], ids=[
    'download',
    'matplotlib',
    'embedded-images',
    'metadata',
])
def test_notebook(request):
    return request.param
