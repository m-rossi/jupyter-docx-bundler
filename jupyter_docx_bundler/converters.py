import base64
try:
    from importlib.resources import files as resources_files
except ImportError:
    from importlib_resources import files as resources_files
import json
import os
import re
import tempfile
from pathlib import Path

import nbformat
import pandas as pd
import pypandoc
import requests
from nbconvert import preprocessors

RE_IMAGE = re.compile(r'!\[.+]\((?!attachment:).+\)')
RE_EXTRA_TITLE = re.compile(r'\s".+"')
RE_MATH_SINGLE = re.compile(r'(?<=\$).+(?=\$)')
RE_MATH_DOUBLE = re.compile(r'(?<=\$\$).+(?=\$\$)')


def _strip_match(matchobj):
    """Strip whitespace from a RE-match-object

    Parameters
    ----------
    matchobj : re.Match
        Match-object of regular-expression.

    Returns
    -------
    str
        Stripped string

    """
    return matchobj.group(0).strip()


def encode_image_base64(filepath):
    """Encode an image as a base64 string

    Parameters
    ----------
    filepath : str
        Filepath of the image file

    Returns
    -------
    nbformat.NotebookNode
        Dictionary with identifier as key and base64-encoded data as value.

    """
    name = os.path.split(filepath)[-1]
    mime = 'image/' + os.path.splitext(filepath)[1][1:]
    if f'{filepath}'.startswith('http'):
        r = requests.get(filepath)
        data = base64.b64encode(r.content).decode('utf8')
    else:
        with open(filepath, 'rb') as image:
            data = base64.b64encode(image.read()).decode('utf8')

    return nbformat.from_dict({name: {mime: data}})


def html_to_pandas_table(s):
    """Get HTML-string of pandas-dataframe out of Jupyter-notebook and transform it back to a
    pandas-dataframe

    Parameters
    ----------
    s : str
        HTML-representation of pandas-dataframe

    Returns
    -------
    pandas.DataFrame

    """
    df = pd.read_html(s)[0]
    if isinstance(df.columns, pd.MultiIndex):
        # find columns which starts with "Unnamed"
        index_col = [all([y.startswith('Unnamed') for y in x]) for x in df.columns]

        # check if there are columns which do not all start with "Unnamed"
        if not any(index_col):
            index_col = [all([y.startswith('Unnamed') for y in x][:len(x)-1]) for x in df.columns]

        # get names of these columns as a list
        index_column_names = df.columns[index_col].values.tolist()

        # set index
        df.set_index(index_column_names, inplace=True)

        # set names of new index to last row of multiindex
        df.index.names = [x[-1] for x in index_column_names]

        # check for "Unnamed*" columns and drop them
        unnamed_cols = [sum([y.startswith('Unnamed') for y in x]) for x in df.columns]
        if all([x == unnamed_cols[0] for x in unnamed_cols]) and unnamed_cols[0] > 0:
            idx = df.columns
            for ii in range(len(idx[0]) - 1, len(idx[0]) - 1 - unnamed_cols[0], -1):
                idx = idx.droplevel(ii)
            df.columns = idx
    elif isinstance(df.columns, pd.Index):
        # find columns which starts with "Unnamed"
        index_col = [x.startswith('Unnamed') for x in df.columns]

        # get names of these columns as a list
        index_column_names = df.columns[index_col].values.tolist()

        # set index
        df.set_index(index_column_names, inplace=True)

    # Remove "Unnamed*" name from indexes
    if isinstance(df.index, pd.MultiIndex):
        for ii, name in enumerate(df.index.names):
            if name.startswith('Unnamed'):
                df.index.names[ii] = None
    elif isinstance(df.index, pd.Index) and df.index.name.startswith('Unnamed'):
        df.index.name = None
    return df


def preprocess(content, path, handler=None):
    """Preprocess the notebook data.
    * Cells will specific tags will be removed and attached images will be embedded.
    * Input of cells with specific tags will be prepared for later removal with a pandoc filter
    * Math-formulas will be fixed to comply with pandoc-requirements

    Parameters
    ----------
    content : nbformat.NotebookNode
        A dict-like node of the notebook with attribute-access
    path : str
        Path to the notebook as string
    handler : tornado.web.RequestHandler, optional
        Handler that serviced the bundle request

    Returns
    -------
    content : nbformat.NotebookNode
        Preprocessed notebook content

    """
    if 'jupyter-docx-bundler' in content['metadata'] and \
            'exclude_input' in content['metadata']['jupyter-docx-bundler'] and \
            content['metadata']['jupyter-docx-bundler']['exclude_input'] in (True, 'True'):
        for cell in content['cells']:
            if cell['cell_type'] == 'code':
                if 'tags' not in cell['metadata']:
                    cell['metadata']['tags'] = []
                cell['metadata']['tags'].append('nbconvert-remove-input')

    # Use cell tags
    tag_preprocessor = preprocessors.TagRemovePreprocessor()
    tag_preprocessor.remove_cell_tags.add('nbconvert-remove-cell')
    tag_preprocessor.remove_input_tags.add('nbconvert-remove-input')
    tag_preprocessor.preprocess(content, {})

    # Apply non-standard operations on cells
    for ii, cell in enumerate(content['cells']):
        # Set input of cells with transient 'remove_source' to later remove it with a pandoc-filter
        if 'transient' in cell and 'remove_source' in cell['transient'] and \
                cell['transient']['remove_source']:
            cell['source'] = 'jupyter-docx-bundler-remove-input'
            del cell['transient']
        # Replace whitespace in math formulas
        if cell['cell_type'] == 'markdown':
            cell['source'] = RE_MATH_SINGLE.sub(_strip_match, cell['source'])
            cell['source'] = RE_MATH_DOUBLE.sub(_strip_match, cell['source'])

        # process outputs
        if 'outputs' in cell:
            for jj, output in enumerate(cell['outputs']):
                # pandas table
                if 'data' in output and 'text/plain' in output['data'] and \
                        'text/html' in output['data'] and \
                        re.search('<table', output['data']['text/html']):
                    try:
                        content['cells'].insert(
                            ii + 1,
                            nbformat.v4.new_markdown_cell(
                                html_to_pandas_table(output['data']['text/html']).to_markdown(),
                            )
                        )
                        del cell['outputs'][jj]
                    except Exception as e:
                        if handler is not None:
                            handler.log.warning(f'Conversion of pandas HTML-table failed : {e}')
                        else:
                            raise e
                # plotly figure
                elif 'data' in output and 'application/vnd.plotly.v1+json' in output['data']:
                    try:
                        from plotly import io
                        from kaleido.scopes.plotly import PlotlyScope

                        scope = PlotlyScope(
                            plotlyjs=resources_files('plotly') / 'package_data' / 'plotly.min.js',
                        )

                        fig = io.from_json(
                            json.dumps(output['data']['application/vnd.plotly.v1+json'])
                        )
                        imagedata = scope.transform(fig, format='png', scale=2.0)
                        output['data']['image/png'] = base64.b64encode(imagedata)
                    except ModuleNotFoundError as e:
                        if handler is not None:
                            handler.log.warning('Found plotly-figure in notebook, we need plotly '
                                                'and kaleido to convert figure.')
                        else:
                            raise e
                # latex but not code cells (it write also a latex output)
                elif 'data' in output and 'text/latex' in output['data'] and \
                        'text/html' not in output['data']:
                    content['cells'].insert(
                        ii + 1,
                        nbformat.v4.new_markdown_cell(
                            source=output['data']['text/latex'],
                        ),
                    )
                    del cell['outputs'][jj]
                # markdown
                elif 'data' in output and 'text/plain' in output['data'] and \
                        'text/markdown' in output['data']:
                    content['cells'].insert(
                        ii + 1,
                        nbformat.v4.new_markdown_cell(
                            source=output['data']['text/markdown'],
                        )
                    )
                    del cell['outputs'][jj]

        # convert linked images to attachments
        linked_to_attachment_image(cell, path)

    return content


def notebookcontent_to_docxbytes(content, filename, path, handler=None):
    """Convert content of a Jupyter notebook to the raw bytes content of a *.docx file

    Parameters
    ----------
    content : nbformat.NotebookNode
        A dict-like node of the notebook with attribute-access
    filename : str
        Filename of the notebook without extension
    handler : tornado.web.RequestHandler, optional
        Handler that serviced the bundle request
    path : str
        Path to the notebook as string
    Returns
    -------
    bytes

    """
    with tempfile.TemporaryDirectory() as tempdir:
        # preprocess notebook
        content = preprocess(content, path, handler=handler)

        # prepare file names
        ipynbfile = os.path.join(tempdir, f'{filename}.ipynb')
        docxfile = os.path.join(tempdir, f'{filename}.docx')

        # set extra args for pandoc
        extra_args = []
        if content['metadata'] is not None:
            if 'authors' in content['metadata']:
                if isinstance(content['metadata']['authors'], list) and all(
                        ['name' in x for x in content['metadata']['authors']]
                ):
                    author_list = [x["name"] for x in content["metadata"]["authors"]]
                    extra_args.append(
                        f'--metadata=author:' f'{", ".join(author_list)}'
                    )
                elif handler is not None:
                    handler.log.warning(
                        'Author metadata has wrong format, see https://github.com/m-rossi/jupyter_'
                        'docx_bundler/blob/main/README.md'
                    )
            if 'title' in content['metadata']:
                extra_args.append(f'--metadata=title:{content["metadata"]["title"]}')
            if 'subtitle' in content['metadata']:
                extra_args.append(f'--metadata=subtitle:{content["metadata"]["subtitle"]}')
            if 'date' in content['metadata']:
                extra_args.append(f'--metadata=date:{content["metadata"]["date"]}')

        nbformat.write(content, ipynbfile)

        # add filter specification to args
        extra_args.append('--filter')
        extra_args.append(f'{(Path(__file__).parent / "pandoc_filter.py").absolute()}')

        # convert to docx
        pypandoc.convert_file(
            ipynbfile,
            'docx',
            outputfile=docxfile,
            extra_args=extra_args,
        )

        # read raw data
        with open(docxfile, 'rb') as bundle_file:
            rawdata = bundle_file.read()

        return rawdata


def linked_to_attachment_image(cell, path):
    """Converts cell with linked images of notebook cell to attachment image.

    Parameters
    ----------
    cell : NotebookNode
        Cell with attachments
    path : str
        Path to the notebook as string
    """
    path = Path(path)
    if cell['cell_type'] == 'markdown':
        s = RE_IMAGE.split(cell['source'])
        images = RE_IMAGE.findall(cell['source'])
        for ii, image in enumerate(images):
            # split markdown link by alt and link
            alt, image = image.split('](')
            # search for an additional title and save it for later
            if RE_EXTRA_TITLE.search(image):
                title = rf' "{RE_EXTRA_TITLE.search(image).group(0)[1:]}"'
            else:
                title = ''
            # replace extra title in image link
            image = RE_EXTRA_TITLE.sub('', image)
            if image.startswith('http'):
                image = image[:-1]
            elif Path(image[:-1]).is_absolute():
                image = Path(image[:-1])
            else:
                image = (path / Path(image[:-1])).resolve()
            nn = encode_image_base64(image)
            key = list(nn.keys())[0]
            s.insert(ii + 1, f'{alt}](attachment:{key}{title})')
            if 'attachments' in cell:
                cell['attachments'].update(nn)
            else:
                cell['attachments'] = nn
        cell['source'] = ''.join(s)
