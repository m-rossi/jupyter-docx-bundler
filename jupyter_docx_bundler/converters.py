import base64
import os
from pathlib import Path
import re
import tempfile

from nbconvert import preprocessors
import nbformat
import pypandoc
import requests


RE_IMAGE = re.compile(r'!\[.+\)')
RE_EXTRA_TITLE = re.compile(r'\s".+"')


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
    if f'{filepath}'.startswith('http'):
        r = requests.get(filepath)
        data = base64.b64encode(r.content).decode('utf8')
    else:
        with open(filepath, 'rb') as image:
            data = base64.b64encode(image.read()).decode('utf8')

    return {key: data}


def preprocess(content, path):
    """Preprocess the notebook data.
    Cells will specific tags will be removed and attached images will be embedded.

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
    tag_preprocessor = preprocessors.TagRemovePreprocessor()
    tag_preprocessor.remove_cell_tags.add('nbconvert-remove-cell')
    tag_preprocessor.remove_input_tags.add('nbconvert-remove-input')
    tag_preprocessor.preprocess(content, {})

    for cell in content['cells']:
        attachment_to_embedded_image(cell)
        linked_to_embedded_image(cell, path)

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


def attachment_to_embedded_image(cell):
    """Converts cell with embedded images as attachments of notebook cell to
    markdown embedded images.

    Parameters
    ----------
    cell : NotebookNode
        Cell with attachments
    """
    if 'attachments' in cell:
        for att in cell['attachments']:
            s = re.split(rf'!\[.+\]\(attachment:{att}\)', cell['source'])
            if len(s) != 2:
                raise NotImplementedError
            for key, val in cell['attachments'][att].items():
                s.insert(1, f'<img src="data:{key};base64,{val}" />')
            cell['source'] = ''.join(s)
        cell.pop('attachments')


def linked_to_embedded_image(cell, path):
    """Converts cell with linked images of notebook cell to markdown embedded images.

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
            _, image = image.split('](')
            # search for an additional title and save it for later
            if RE_EXTRA_TITLE.search(image):
                title = f' title={RE_EXTRA_TITLE.search(image).group(0)[1:]}'
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
            b64 = encode_image_base64(image)
            key = list(b64.keys())[0]
            s.insert(ii + 1, f'<img src="data:{key};base64,{b64[key]}"{title} />')
        cell['source'] = ''.join(s)
