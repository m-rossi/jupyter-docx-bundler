import json
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
        extra_args=['--extract-media', f'{tmpdir / "media"}'],
        outputfile=f'{tmpdir / "images-notebook.md"}',
    )

    # compare number of extracted media with generated media
    media = list(Path(tmpdir / 'media').glob('**/*.*'))
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
    # load source table
    df = pd.DataFrame(json.loads(pandas_html_table_notebook['metadata']['table']))
    # because of the intermediate conversion to json-string, the int-datatype is lost
    try:
        df.index = df.index.astype('int')
    except TypeError:
        pass

    # adujst column names to those we can extract from the markdown format later
    df.columns = [x.replace(', ', ',') for x in df.columns]
    try:
        df.index = [x.replace(', ', ',') for x in df.index]
    except AttributeError:
        pass

    # fix named index for json-converted pandas-dataframe
    if pandas_html_table_notebook['metadata']['named-index']:
        df.index.name = 'index'

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
    fixed_lines = []
    for line in lines:
        if line != '\n':
            fixed_lines.append(line.replace('\\', '').replace(', ', ','))
    with open(outfilename, 'w') as file:
        file.writelines(fixed_lines[-(df.shape[0]+2):])

    # load markdown table
    df_md = pd.read_csv(outfilename, skiprows=[1], sep=r'\s+')

    # set index for named-index dataframes
    cols = re.split(r'\s+', fixed_lines[-(df.shape[0])])
    cols = sum([len(x) > 0 for x in cols])
    if cols == df_md.shape[1]:
        df_md.set_index('index', inplace=True)

    # compare index and data
    assert all(df_md.index == df.index), 'Index does not match'
    assert all(df_md.columns == df.columns), 'Columns does not match'
    np.testing.assert_allclose(df_md.values, df.values, atol=1e-5)


def test_ipython_output(tmpdir, ipython_output_notebook):
    # convert notebook to docx
    docxbytes = converters.notebookcontent_to_docxbytes(
        ipython_output_notebook,
        'test-notebook',
        ipython_output_notebook['metadata']['path'],
    )

    # write to file on disk
    docx_filename = tmpdir / 'test-notebook.docx'
    with open(docx_filename, 'wb') as file:
        file.write(docxbytes)

    # convert to markdown and read text
    markdown_filename = tmpdir / 'test-notebook.md'
    pypandoc.convert_file(
        f'{docx_filename}',
        'md',
        'docx',
        outputfile=f'{markdown_filename}',
    )
    with open(markdown_filename, 'r') as file:
        lines = file.readlines()

    # replace newlines
    lines = [line.replace('\n', '') for line in lines]
    assert len(lines) == 1
    assert re.search(ipython_output_notebook['metadata']['expected_pattern'], lines[0])
