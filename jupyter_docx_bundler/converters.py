from nbconvert import HTMLExporter
import os
import pypandoc


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
    html_exporter = HTMLExporter(anchor_link_text=' ')

    # export to html
    content, resources = html_exporter.from_notebook_node(
        content,
        resources={'metadata': content['metadata']})

    # check if export path exists
    if os.path.dirname(htmlfile) is not '' and not os.path.isdir(
            os.path.dirname(htmlfile)):
        raise FileNotFoundError('Path to html-file does not exist: {}'.format(
            os.path.dirname(htmlfile)))

    # write content to html file
    with open(htmlfile, 'w', encoding='utf-8') as file:
        file.write(content)


def html_to_docx(htmlfile, docxfile):
    """ Convert html file to docx file.

    Parameters
    ----------

    htmlfile : str
        Filename of the notebook exported as html
    docxfile : str
        Filename for the notebook exported as docx
    """

    # check if html file exists
    if not os.path.isfile(htmlfile):
        raise FileNotFoundError('html-file does not exist: {}'.format(
            htmlfile))

    # check if export path exists
    if os.path.dirname(docxfile) is not '' and not os.path.isdir(
            os.path.dirname(docxfile)):
        raise FileNotFoundError('Path to docx-file does not exist: {}'.format(
            os.path.dirname(docxfile)))

    # convert to docx
    pypandoc.convert_file(htmlfile,
                          'docx',
                          format='html+tex_math_dollars',
                          outputfile=docxfile)
