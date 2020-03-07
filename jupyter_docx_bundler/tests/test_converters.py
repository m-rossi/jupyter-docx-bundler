from pathlib import Path
import tempfile

from .. import converters


def test_notebookcontent_to_docxbytes(test_notebook):
    converters.notebookcontent_to_docxbytes(
        test_notebook, 'download-notebook', test_notebook['metadata']['path'],
    )


def test_title_removed(metadata_notebook):
    if 'title' in metadata_notebook['metadata']:
        title_set = True
    else:
        title_set = False

    with tempfile.TemporaryDirectory() as htmldir:
        htmlfile = Path(htmldir) / 'notebook.html'
        converters.notebook_to_html(metadata_notebook, htmlfile)
        with open(htmlfile, 'r') as html:
            content = ''.join(html.readlines())
            assert title_set or (
                '<title>' not in content and '</title>' not in content and not title_set
            ), 'No title set in metadata but exported in html.'
