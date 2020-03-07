import base64
import os
from pathlib import Path
import re
import tempfile

from nbconvert import HTMLExporter, preprocessors
import pypandoc
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


def notebook_to_html(content, htmlfile):
    """ Convert notebook to html file.

    Parameters
    ----------

    content : nbformat.NotebookNode
        A dict-like node of the notebook with attribute-access
    htmlfile : str
        Filename for the notebook exported as html
    """
    # prepare html exporter, anchor_link_text=' ' suppress anchors being shown
    html_exporter = HTMLExporter(
        anchor_link_text=' ', exclude_input_prompt=True, exclude_output_prompt=True
    )

    # save metadata for possible title removement
    metadata = content['metadata']

    # export to html
    content, _ = html_exporter.from_notebook_node(content)

    # check if export path exists
    if os.path.dirname(htmlfile) != '' and not os.path.isdir(os.path.dirname(htmlfile)):
        raise FileNotFoundError(f'Path to html-file does not exist: {os.path.dirname(htmlfile)}')

    # Remove title from htmlfile if none is set to prevent pandoc from writing one
    if 'title' not in metadata:
        content = remove_html_title(content)

    # write content to html file
    with open(htmlfile, 'w', encoding='utf-8') as file:
        file.write(content)


def html_to_docx(htmlfile, docxfile, handler=None, metadata=None):
    """ Convert html file to docx file.

    Parameters
    ----------

    htmlfile : str
        Filename of the notebook exported as html
    docxfile : str
        Filename for the notebook exported as docx
    handler : tornado.web.RequestHandler, optional
        Handler that serviced the bundle request
    metadata : dict, optional
        Dicts with metadata information of the notebook
    """

    # check if html file exists
    if not os.path.isfile(htmlfile):
        raise FileNotFoundError(f'html-file does not exist: {htmlfile}')

    # check if export path exists
    if os.path.dirname(docxfile) != '' and not os.path.isdir(os.path.dirname(docxfile)):
        raise FileNotFoundError(f'Path to docx-file does not exist: {os.path.dirname(docxfile)}')

    # set extra args for pandoc
    extra_args = []
    if metadata is not None and 'authors' in metadata:
        if isinstance(metadata['authors'], list) and all(
            ['name' in x for x in metadata['authors']]
        ):
            extra_args.append(
                f'--metadata=author:' f'{", ".join([x["name"] for x in metadata["authors"]])}'
            )
        elif handler is not None:
            handler.log.warning(
                'Author metadata has wrong format, see https://github.com/m-rossi/jupyter_docx_bun'
                'dler/blob/master/README.md'
            )
    if metadata is not None and 'subtitle' in metadata:
        extra_args.append(f'--metadata=subtitle:{metadata["subtitle"]}')
    if metadata is not None and 'date' in metadata:
        extra_args.append(f'--metadata=date:{metadata["date"]}')

    # convert to docx
    pypandoc.convert_file(
        htmlfile,
        'docx',
        format='html+tex_math_dollars',
        outputfile=docxfile,
        extra_args=extra_args,
    )


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
        htmlfile = os.path.join(tempdir, f'{filename}.html')
        docxfile = os.path.join(tempdir, f'{filename}.docx')

        # convert notebook to html
        notebook_to_html(content, htmlfile)

        # convert html to docx
        html_to_docx(
            htmlfile, docxfile, metadata=content['metadata'], handler=handler,
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
    re_image = re.compile(rf'!\[.+\)')
    re_extra_title = re.compile(r'\s".+"')
    if cell['cell_type'] == 'markdown':
        s = re_image.split(cell['source'])
        images = re_image.findall(cell['source'])
        for ii, image in enumerate(images):
            # split markdown link by alt and link
            _, image = image.split('](')
            # search for an additional title and save it for later
            if re_extra_title.search(image):
                title = f' title={re_extra_title.search(image).group(0)[1:]}'
            else:
                title = ''
            # replace extra title in image link
            image = re_extra_title.sub('', image)
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


def remove_html_title(htmlcontent):
    """Remove <title> tag from htmlcontent.

    Parameters
    ----------
    htmlcontent : str
        Content of htmlfile.
    """
    return re.sub('<title>.+</title>', '', htmlcontent)
