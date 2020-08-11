import base64
import os
from pathlib import Path
import re
import tempfile

from nbconvert import preprocessors
import nbformat
import pypandoc
import requests


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


def preprocess(content, path):
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
    for cell in content['cells']:
        # Set input of cells with transient 'remove_source' to later remove it with a pandoc-filter
        if 'transient' in cell and 'remove_source' in cell['transient'] and \
                cell['transient']['remove_source']:
            cell['source'] = 'jupyter-docx-bundler-remove-input'
            del cell['transient']
        # Replace whitespace in math formulas
        if cell['cell_type'] == 'markdown':
            cell['source'] = RE_MATH_SINGLE.sub(_strip_match, cell['source'])
            cell['source'] = RE_MATH_DOUBLE.sub(_strip_match, cell['source'])

    for cell in content['cells']:
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
        content = preprocess(content, path)

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
                        'docx_bundler/blob/master/README.md'
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
