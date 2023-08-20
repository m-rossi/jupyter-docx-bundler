import os

from nbconvert import nbconvertapp
import nbformat


def test_jupyter_nbconvert_cli(tmpdir, download_notebook):
    ipynb_filename = os.path.join(tmpdir, 'download_notebook.ipynb')
    with open(ipynb_filename, 'w', encoding='utf8') as file:
        file.write(nbformat.writes(download_notebook))

    app = nbconvertapp.NbConvertApp()
    app.initialize(argv=[ipynb_filename, '--to', 'jupyter_docx_bundler.DocxExporter'])
    app.convert_notebooks()
