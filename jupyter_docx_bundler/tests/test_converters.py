from pathlib import Path
import re

import numpy as np
import pandas as pd
import pypandoc

from .. import converters


def test_notebookcontent_to_docxbytes(test_notebook):
    converters.notebookcontent_to_docxbytes(
        test_notebook, 'test-notebook', test_notebook['metadata']['path'],
    )


def test_image_conversion(tmpdir, images_notebook):
    # convert notebook to docx
    docxbytes = converters.notebookcontent_to_docxbytes(
        images_notebook, 'test-notebook', images_notebook['metadata']['path'],
    )

    # write to file on disk
    filename = tmpdir / 'images-notebook.docx'
    with open(filename, 'wb') as file:
        file.write(docxbytes)

    # convert to markdown and extract media
    pypandoc.convert_file(
        f'{filename}',
        'markdown',
        'docx',
        extra_args=['--extract-media', f'{tmpdir}'],
        outputfile=f'{tmpdir / "images-notebook.md"}',
    )

    # compare number of extracted media with generated media
    media = list(Path(tmpdir / 'media').glob('*.*'))
    assert images_notebook['metadata']['image_count'] == len(media),\
        'Number of generated images does not match in docx-document.'


def test_remove_input(tmpdir, remove_input_notebook):
    # convert notebook to docx
    docxbytes = converters.notebookcontent_to_docxbytes(
        remove_input_notebook, 'test-notebook', remove_input_notebook['metadata']['path'],
    )

    # write to file on disk
    filename = tmpdir / 'images-notebook.docx'
    outfilename = tmpdir / 'remove-input-notebook.md'
    with open(filename, 'wb') as file:
        file.write(docxbytes)

    # convert to markdown and read text
    pypandoc.convert_file(
        f'{filename}',
        'markdown',
        'docx',
        outputfile=f'{outfilename}',
    )
    with open(outfilename, 'r') as file:
        lines = file.readlines()

    # Check for the occurence of code
    assert len(re.findall('jupyter.*docx.*bundler.*remove.*input', ''.join(lines))) == 0, \
        'Keyword not removed'
    assert len(re.findall('print(.*Hide my input!.*)', ''.join(lines))) == 0, 'Input not hided.'


def test_remove_cell(tmpdir, remove_cell_notebook):
    # convert notebook to docx
    docxbytes = converters.notebookcontent_to_docxbytes(
        remove_cell_notebook, 'test-notebook', remove_cell_notebook['metadata']['path'],
    )

    # write to file on disk
    filename = tmpdir / 'images-notebook.docx'
    outfilename = tmpdir / 'remove-cell-notebook.md'
    with open(filename, 'wb') as file:
        file.write(docxbytes)

    # convert to markdown and read text
    pypandoc.convert_file(
        f'{filename}',
        'markdown',
        'docx',
        outputfile=f'{outfilename}',
    )
    with open(outfilename, 'r') as file:
        lines = file.readlines()

    # Check for the occurence of code
    assert len(re.findall('Hide me!', ''.join(lines))) == 0, 'Cell not hided.'


def test_remove_all_inputs(tmpdir, remove_all_inputs_notebook):
    # convert notebook to docx
    docxbytes = converters.notebookcontent_to_docxbytes(
        remove_all_inputs_notebook,
        'test-notebook',
        remove_all_inputs_notebook['metadata']['path'],
    )

    # write to file on disk
    filename = tmpdir / 'test-notebook.docx'
    outfilename = tmpdir / 'test-cell-notebook.md'
    with open(filename, 'wb') as file:
        file.write(docxbytes)

    # convert to markdown and read text
    pypandoc.convert_file(
        f'{filename}',
        'markdown',
        'docx',
        outputfile=f'{outfilename}',
    )
    with open(outfilename, 'r') as file:
        lines = file.readlines()

    # Check for the occurence of code
    if remove_all_inputs_notebook['metadata']['jupyter-docx-bundler']['exclude_input'] in \
            (True, 'True'):
        assert len(re.findall('jupyter.*docx.*bundler.*remove.*input', ''.join(lines))) == 0, \
            'Keyword not removed'
        assert len(re.findall('Hide my input!', ''.join(lines))) == \
               remove_all_inputs_notebook['metadata']['ncells'], 'Number of inputs do not match.'
        assert len(re.findall('print(.*Hide my input!.*)', ''.join(lines))) == 0, 'Input not hided'
    else:
        assert len(re.findall('Hide my input!', ''.join(lines))) == \
               remove_all_inputs_notebook['metadata']['ncells'] * 2, \
               'Number of inputs do not match.'
        assert len(re.findall('print(.*Hide my input!.*)', ''.join(lines))) == \
               remove_all_inputs_notebook['metadata']['ncells'], 'Input not hided'


def test_math_notebook(tmpdir, math_notebook):
    # convert notebook to docx
    docxbytes = converters.notebookcontent_to_docxbytes(
        math_notebook,
        'test-notebook',
        math_notebook['metadata']['path'],
    )

    # write to file on disk
    filename = tmpdir / 'test-notebook.docx'
    outfilename = tmpdir / 'test-cell-notebook.rst'
    with open(filename, 'wb') as file:
        file.write(docxbytes)

    # convert to rst and read text
    pypandoc.convert_file(
        f'{filename}',
        'rst',
        'docx',
        outputfile=f'{outfilename}',
    )
    with open(outfilename, 'r') as file:
        lines = file.readlines()

    assert len(re.findall(r'(:math:)|(\.\. math::)', ''.join(lines))) == \
           math_notebook['metadata']['ncells'], 'Not all math formulars are converted correctly.'


def test_pandas_html_table(tmpdir, pandas_html_table_notebook):
    # read HTML table
    df_html = pd.read_html(
        pandas_html_table_notebook['cells'][1]['outputs'][0]['data']['text/html'],
        index_col=0,
    )[0]

    # convert notebook to docx
    docxbytes = converters.notebookcontent_to_docxbytes(
        pandas_html_table_notebook,
        'test-notebook',
        pandas_html_table_notebook['metadata']['path'],
    )

    # write to file on disk
    filename = tmpdir / 'test-notebook.docx'
    outfilename = tmpdir / 'test-cell-notebook.md'
    with open(filename, 'wb') as file:
        file.write(docxbytes)

    # convert docx back to markdown
    pypandoc.convert_file(
        f'{filename}',
        'markdown',
        'docx',
        outputfile=f'{outfilename}',
    )

    # replace some weird escape sequence for markdown export of pandoc
    with open(outfilename, 'r') as file:
        lines = file.readlines()
    lines = [line.replace('\\', '').replace(', ', ',') for line in lines]
    with open(outfilename, 'w') as file:
        file.writelines(lines)

    # load markdown table
    df_md = pd.read_table(outfilename, skiprows=[0, 1, 2, 3, 6], sep=r'\s+')

    # compare index and data
    assert all(df_md.index == df_html.index), 'Index does not match'
    np.testing.assert_allclose(df_md.values, df_html.values, atol=1e-5)
