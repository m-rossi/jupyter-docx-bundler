import os
import re

import matplotlib.pyplot as plt
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat
import numpy as np
import pytest
from pytest_lazyfixture import lazy_fixture
import requests

from ..converters import encode_image_base64


@pytest.fixture(
    params=[
        'https://nbviewer.jupyter.org/github/unpingco/Python-for-Signal-Processing/blob/master/Mor'
        'e_Fourier_Transform.ipynb',
        'https://nbviewer.jupyter.org/github/CamDavidsonPilon/Probabilistic-Programming-and-Bayesi'
        'an-Methods-for-Hackers/blob/master/Chapter1_Introduction/Ch1_Introduction_PyMC3.ipynb',
        'https://nbviewer.jupyter.org/github/waltherg/notebooks/blob/master/2013-12-03-Crank_Nicol'
        'son.ipynb',
    ]
)
def download_notebook(tmpdir, request):
    notebook_url = request.param

    # check extension of file
    filename = os.path.basename(notebook_url)
    if not notebook_url.endswith('.ipynb'):
        raise ValueError(f'{filename} is not a Jupyter notebook.')

    # redirect notebook if notebook is located on nbviewer.jupyter.org
    if 'nbviewer' in notebook_url:
        r = requests.get(notebook_url)
        link = re.findall(
            '(?<=<a href=").+(?=" title="Download Notebook" ' 'download>)',
            r.content.decode('utf8'),
        )
        if len(link) > 0:
            notebook_url = link[0]

    # download notebook
    r = requests.get(notebook_url)

    nb = nbformat.reads(r.content.decode('utf8'), 4)
    nb['metadata'].update({'path': f'{tmpdir}'})

    return nb


@pytest.fixture(params=[10])
def matplotlib_notebook(tmpdir, request):
    nb = nbformat.v4.new_notebook()

    nb.cells.append(
        nbformat.v4.new_code_cell(
            '\n'.join([
                'import matplotlib.pyplot as plt',
                '%matplotlib inline',
            ])
        )
    )

    for _ in range(request.param):
        nb.cells.append(
            nbformat.v4.new_code_cell(
                '\n'.join([
                    'plt.figure(dpi=100)',
                    'plt.plot(range(100))',
                    'plt.show()',
                ])
            )
        )

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    nb['metadata'].update({'path': f'{tmpdir}'})

    return nb


@pytest.fixture(params=['png'])
def images_notebook(tmpdir, request):
    nb = nbformat.v4.new_notebook()

    filename = 'matplotlib.' + request.param

    plt.figure()
    plt.plot(np.linspace(0, 1), np.power(np.linspace(0, 1), 2))
    plt.savefig(os.path.join(tmpdir, filename))

    # add image as path
    nb.cells.append(
        nbformat.v4.new_markdown_cell('\n'.join([
            'line1',
            f'![{filename}]({filename})',
            'line3',
        ]))
    )

    # add image as path with extra title
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            '\n'.join([
                'line1',
                f'![title]({filename} "extra-title")',
                'line3',
            ])
        )
    )

    # add image as attachment
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            '\n'.join([
                'line1',
                f'![{filename}](attachment:{filename})',
                'line3',
            ])
        )
    )
    nb.cells[-1]['attachments'] = {filename: encode_image_base64(os.path.join(tmpdir, filename))}

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    nb['metadata'].update({'path': f'{tmpdir}'})

    return nb


@pytest.fixture(params=[True, False])
def metadata_notebook(tmpdir, request):
    nb = nbformat.v4.new_notebook()

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    nb['metadata'].update(
        {
            'authors': [{'name': 'author1'}, {'name': 'author2'}],
            'subtitle': 'subtitle',
            'date': '2019-05-11',
            'path': f'{tmpdir}',
        }
    )
    if request.param:
        nb['metadata']['title'] = 'title'

    return nb


@pytest.fixture(
    params=[
        lazy_fixture('download_notebook'),
        lazy_fixture('matplotlib_notebook'),
        lazy_fixture('images_notebook'),
        lazy_fixture('metadata_notebook'),
    ],
    ids=[
        'download',
        'matplotlib',
        'embedded-images',
        'metadata',
    ],
)
def test_notebook(request):
    return request.param
