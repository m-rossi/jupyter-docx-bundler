import os
import re

import matplotlib.pyplot as plt
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat
import numpy as np
import pandas as pd
import pytest
from pytest_lazyfixture import lazy_fixture
import requests

from ..converters import encode_image_base64


def _random_matplotlib_image(path):
    fig, ax = plt.subplots(1, 1)
    ax.plot(np.random.randn(100))
    fig.savefig(path)
    plt.close(fig)

    return path


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
    image_count = 0

    # imports
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            '# Imports',
        )
    )
    nb.cells.append(
        nbformat.v4.new_code_cell(
            '\n'.join([
                'import matplotlib.pyplot as plt',
                'import numpy as np',
                '%matplotlib inline',
            ])
        )
    )

    # single matplotlib image inline output
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            '# single matplotlib image inline output',
        )
    )
    for _ in range(request.param):
        nb.cells.append(
            nbformat.v4.new_code_cell(
                '\n'.join([
                    'plt.figure(dpi=100)',
                    'plt.plot(np.random.randn(100))',
                    'plt.show()',
                ])
            )
        )
    image_count += request.param

    # mulitple matplotlib image inline output
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            '# mulitple matplotlib image inline output',
        )
    )
    nb.cells.append(
        nbformat.v4.new_code_cell(
            '\n'.join([
                f'for ii in range({request.param}):',
                '    plt.figure()',
                '    plt.plot(np.random.randn(100))',
                '    plt.show()',
            ])
        )
    )
    image_count += request.param

    nb['metadata'].update({
        'path': f'{tmpdir}',
        'image_count': image_count,
    })

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture(params=[
    'png',
    'jpg',
    'jpeg',
    'tiff',
])
def markdown_images_notebook(tmpdir, request):
    nb = nbformat.v4.new_notebook()
    image_count = 0

    # add image as path
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            '# Linked image',
        )
    )
    filename = _random_matplotlib_image(tmpdir / f'path.{request.param}')
    nb.cells.append(
        nbformat.v4.new_markdown_cell('\n'.join([
            'line1',
            f'![{filename}]({filename})',
            'line3',
        ]))
    )
    image_count += 1

    # add image as path with extra title
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            '# Linked image with extra title'
        )
    )
    filename = _random_matplotlib_image(tmpdir / f'path_extra-title.{request.param}')
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            '\n'.join([
                'line1',
                f'![title]({filename} "extra-title")',
                'line3',
            ])
        )
    )
    image_count += 1

    # add image as attachment
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            '# Image as attachment'
        )
    )
    filename = _random_matplotlib_image(tmpdir / f'attachment.{request.param}')
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            '\n'.join([
                'line1',
                f'![{filename}](attachment:{filename})',
                'line3',
            ])
        )
    )
    nb.cells[-1]['attachments'] = encode_image_base64(os.path.join(tmpdir, filename))
    image_count += 1

    nb['metadata'].update({
        'path': f'{tmpdir}',
        'image_count': image_count,
    })

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture
def metadata_notebook(tmpdir):
    nb = nbformat.v4.new_notebook()

    nb['metadata'].update(
        {
            'title': 'title',
            'authors': [{'name': 'author1'}, {'name': 'author2'}],
            'subtitle': 'subtitle',
            'date': '2019-05-11',
            'path': f'{tmpdir}',
        }
    )

    nb.cells.append(nbformat.v4.new_markdown_cell('Hello World!'))

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture
def remove_input_notebook(tmpdir):
    nb = nbformat.v4.new_notebook()

    tags = nbformat.notebooknode.NotebookNode({
        'tags': ['nbconvert-remove-input'],
    })

    # Create cell with visible output
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            source='# Visible Output',
        )
    )
    nb.cells.append(
        nbformat.v4.new_code_cell(
            source='print("Hide my input!")',
            metadata=tags,
        )
    )

    nb['metadata'].update({'path': f'{tmpdir}'})

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture
def remove_cell_notebook(tmpdir):
    nb = nbformat.v4.new_notebook()

    tags = nbformat.notebooknode.NotebookNode({
        'tags': ['nbconvert-remove-cell'],
    })

    # Create cell with visible output
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            source='# Removed Cell',
        )
    )
    nb.cells.append(
        nbformat.v4.new_code_cell(
            source='print("Hide me!")',
            metadata=tags,
        )
    )

    nb['metadata'].update({'path': f'{tmpdir}'})

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture(params=[
    {'ncells': 10, 'exclude_input': True},
    {'ncells': 10, 'exclude_input': False},
    {'ncells': 10, 'exclude_input': "True"},
])
def remove_all_inputs_notebook(tmpdir, request):
    nb = nbformat.v4.new_notebook()

    for ii in range(request.param['ncells']):
        nb.cells.append(
            nbformat.v4.new_code_cell(
                source='print("Hide my input!")',
            )
        )

    nb['metadata'].update({
        'path': f'{tmpdir}',
        'ncells': request.param['ncells'],
        'jupyter-docx-bundler': {
            'exclude_input': request.param['exclude_input'],
        }
    })

    ep = ExecutePreprocessor()
    while request.param['ncells'] != sum([len(c.outputs) for c in nb.cells]):
        ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture(params=[{'ncells': 10}])
def math_with_space_notebook(tmpdir, request):
    nb = nbformat.v4.new_notebook()

    for ii in range(request.param['ncells']):
        nb.cells.append(
            nbformat.v4.new_markdown_cell(
                source=r'Inline formular $ y = m \cdot x + b $',
            )
        )

    for ii in range(request.param['ncells']):
        nb.cells.append(
            nbformat.v4.new_markdown_cell(
                source=r'$$ y = m \cdot x + b $$',
            )
        )

    nb['metadata'].update({
        'path': f'{tmpdir}',
        'ncells': request.param['ncells'] * 2,
    })

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture(params=[{'ncells': 10}])
def math_without_space_notebook(tmpdir, request):
    nb = nbformat.v4.new_notebook()

    for ii in range(request.param['ncells']):
        nb.cells.append(
            nbformat.v4.new_markdown_cell(
                source=r'Inline formular $y = m \cdot x + b$',
            )
        )

    for ii in range(request.param['ncells']):
        nb.cells.append(
            nbformat.v4.new_markdown_cell(
                source=r'$$y = m \cdot x + b$$',
            )
        )

    nb['metadata'].update({
        'path': f'{tmpdir}',
        'ncells': request.param['ncells'] * 2,
    })

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture(
    params=[
        'normal',
        'named-index',
        'multicolumn',
        'multirow',
        'multirow-multicolumn',
    ],
)
def pandas_html_table_notebook(tmpdir, request):
    nb = nbformat.v4.new_notebook()

    nb.cells.append(
        nbformat.v4.new_code_cell(
            source='\n'.join([
                'import numpy as np',
                'import pandas as pd',
            ])
        )
    )

    if request.param == 'named-index':
        index = pd.Index(np.arange(6), name="index")
        df = pd.DataFrame(
            np.random.randn(6, 4),
            index=index,
            columns=("A", "B", "C", "D"),
        )
        nb.cells.append(
            nbformat.v4.new_code_cell(
                source='\n'.join([
                    'index = pd.Index(np.arange(6), name="myindex")',
                    'pd.DataFrame(',
                    '    np.random.randn(6, 4),',
                    '    index=index,',
                    '    columns=("A", "B", "C", "D"),',
                    ')',
                ])
            )
        )
    elif request.param == 'multicolumn':
        df = pd.DataFrame(np.random.randn(6, 4), columns=[list("1122"), list("ABCD")])
        nb.cells.append(
            nbformat.v4.new_code_cell(
                source='pd.DataFrame(np.random.randn(6, 4), columns=[list("1122"), list("ABCD")])',
            )
        )
    elif request.param == 'multirow':
        arrays = [
            ["A", "B", "C"],
            [1, 2],
        ]
        index = pd.MultiIndex.from_product(arrays, names=["first", "second"])
        df = pd.DataFrame(np.random.randn(6, 4), index=index)
        nb.cells.append(
            nbformat.v4.new_code_cell(
                source='\n'.join([
                    'arrays = [',
                    '    ["A", "B", "C"],',
                    '    [1, 2],',
                    ']',
                    'index = pd.MultiIndex.from_product(arrays, names=["first", "second"])',
                    'pd.DataFrame(np.random.randn(6, 4), index=index)',
                ])
            )
        )
    elif request.param == 'multirow-multicolumn':
        arrays = [
            ["A", "B", "C"],
            [1, 2],
        ]
        index = pd.MultiIndex.from_product(arrays, names=["first", "second"])
        df = pd.DataFrame(
            np.random.randn(6, 4),
            index=index,
            columns=[list("1122"), list("ABCD")],
        )
        nb.cells.append(
            nbformat.v4.new_code_cell(
                source='\n'.join([
                    'arrays = [',
                    '    ["A", "B", "C"],',
                    '    [1, 2],',
                    ']',
                    'index = pd.MultiIndex.from_product(arrays, names=["first", "second"])',
                    'pd.DataFrame(',
                    '    np.random.randn(6, 4),',
                    '    index=index,',
                    '    columns=[list("1122"), list("ABCD")],',
                    ')',
                ])
            )
        )
    else:
        df = pd.DataFrame(np.random.randn(6, 4), columns=("A", "B", "C", "D"))
        nb.cells.append(
            nbformat.v4.new_code_cell(
                source='pd.DataFrame(np.random.randn(6, 4), columns=("A", "B", "C", "D"))',
            )
        )

    nb['metadata'].update({
        'path': f'{tmpdir}',
        'table': df.to_json(),
        'named-index': True if request.param == 'named-index' else False,
    })

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    nb.cells[-1].outputs[0]['data']['text/plain'] = df.__repr__()
    nb.cells[-1].outputs[0]['data']['text/html'] = df._repr_html_()

    return nb


@pytest.fixture
def math_in_output(tmpdir):
    nb = nbformat.v4.new_notebook()

    nb.cells.append(
        nbformat.v4.new_code_cell(
            source='\n'.join([
                'from IPython.display import display',
                'import sympy as sp',
            ]),
        )
    )
    nb.cells.append(
        nbformat.v4.new_code_cell(
            source='sp.var("a, b")'
        )
    )

    nb.cells.append(
        nbformat.v4.new_code_cell(
            source='display(a/b**3)'
        )
    )

    nb['metadata'].update({
        'path': f'{tmpdir}',
        'ncells': 1,
    })

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture(
    params=[
        'Markdown',
        'LaTeX',
        'Math',
        'Code',
    ]
)
def ipython_output_notebook(tmpdir, request):
    nb = nbformat.v4.new_notebook()

    nb.cells.append(
        nbformat.v4.new_code_cell(
            source='from IPython import display',
            metadata=nbformat.notebooknode.NotebookNode({
                'tags': [
                    'nbconvert-remove-input',
                ],
            }),
        ),
    )
    if request.param == 'Markdown':
        nb.cells.append(
            nbformat.v4.new_code_cell(
                source='display.Markdown("# Heading")',
                metadata=nbformat.notebooknode.NotebookNode({
                    'tags': [
                        'nbconvert-remove-input',
                    ],
                }),
            )
        )
        expected_pattern = '# Heading'
    elif request.param == 'LaTeX':
        nb.cells.append(
            nbformat.v4.new_code_cell(
                source='display.Latex("$a + b$")',
                metadata=nbformat.notebooknode.NotebookNode({
                    'tags': [
                        'nbconvert-remove-input',
                    ],
                }),
            )
        )
        expected_pattern = r'\$a \+ b\$'
    elif request.param == 'Math':
        nb.cells.append(
            nbformat.v4.new_code_cell(
                source='display.Math("a + b")',
                metadata=nbformat.notebooknode.NotebookNode({
                    'tags': [
                        'nbconvert-remove-input',
                    ],
                }),
            )
        )
        expected_pattern = r'\$a \+ b\$'
    elif request.param == 'Code':
        nb.cells.append(
            nbformat.v4.new_code_cell(
                source='display.Code("import this")',
                metadata=nbformat.notebooknode.NotebookNode({
                    'tags': [
                        'nbconvert-remove-input',
                    ],
                }),
            )
        )
        expected_pattern = r'[\w`]*import this[\w`]*'

    nb['metadata'].update({
        'path': f'{tmpdir}',
        'expected_pattern': expected_pattern,
    })

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture(params=[10])
def plotly_notebook(tmpdir, request):
    nb = nbformat.v4.new_notebook()
    image_count = 0

    # imports
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            '# Imports',
        )
    )
    nb.cells.append(
        nbformat.v4.new_code_cell(
            '\n'.join([
                'import numpy as np',
                'import plotly.express as px',
            ])
        )
    )

    # single plotly image per cell
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            '# single plotly image per cell',
        )
    )
    for _ in range(request.param):
        nb.cells.append(
            nbformat.v4.new_code_cell(
                '\n'.join([
                    'fig = px.line(x=np.arange(100), y=np.random.randn(100))',
                    'fig.show()',
                ])
            )
        )
    image_count += request.param

    # update metadata
    nb['metadata'].update({
        'path': f'{tmpdir}',
        'image_count': image_count,
    })

    ep = ExecutePreprocessor()
    ep.preprocess(nb, {'metadata': {'path': tmpdir}})

    return nb


@pytest.fixture(
    params=[
        lazy_fixture('math_with_space_notebook'),
        lazy_fixture('math_without_space_notebook'),
        lazy_fixture('math_in_output'),
    ],
    ids=[
        'with_space',
        'without_space',
        'math_in_output',
    ]
)
def math_notebook(request):
    return request.param


@pytest.fixture(
    params=[
        lazy_fixture('download_notebook'),
        lazy_fixture('images_notebook'),
        lazy_fixture('metadata_notebook'),
        lazy_fixture('pandas_html_table_notebook'),
        lazy_fixture('math_notebook'),
    ],
    ids=[
        'download',
        'images',
        'metadata',
        'html-table',
        'math',
    ],
)
def test_notebook(request):
    return request.param


@pytest.fixture(
    params=[
        lazy_fixture('matplotlib_notebook'),
        lazy_fixture('markdown_images_notebook'),
        lazy_fixture('plotly_notebook'),
    ],
    ids=[
        'matplotlib',
        'images',
        'plotly',
    ]
)
def images_notebook(request):
    return request.param
