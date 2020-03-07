from pathlib import Path
import os

from mock import patch
from nbconvert import nbconvertapp
import nbformat
from nbformat import write
from nbformat.v4 import (
    new_notebook,
    new_markdown_cell,
    new_code_cell,
    new_output,
)
from notebook.tests.launchnotebook import NotebookTestBase


class BundleAPITest(NotebookTestBase):
    @classmethod
    def setup_class(cls):
        super(BundleAPITest, cls).setup_class()
        nbdir = Path(cls.notebook_dir)

        nb = new_notebook()

        nb.cells.append(new_markdown_cell(u'Created by test'))
        cc1 = new_code_cell(source=u'print(2*6)')
        cc1.outputs.append(new_output(output_type='stream', text=u'12'))
        nb.cells.append(cc1)

        with open(nbdir / 'testnb.ipynb', 'w', encoding='utf-8') as f:
            write(nb, f, version=4)

    def test_bundler_invoke(self):
        with patch('notebook.bundler.handlers.BundlerHandler.get_bundler') as mock:
            mock.return_value = {'module_name': 'jupyter_docx_bundler'}
            resp = self.request(
                'GET', 'bundle/testnb.ipynb', params={'bundler': 'jupyter_docx_bundler'}
            )
            mock.assert_called_with('jupyter_docx_bundler')
        self.assertEqual(resp.status_code, 200)


def test_jupyter_nbconvert_cli(tmpdir, download_notebook):
    ipynb_filename = os.path.join(tmpdir, 'download_notebook.ipynb')
    with open(ipynb_filename, 'w', encoding='utf8') as file:
        file.write(nbformat.writes(download_notebook))

    app = nbconvertapp.NbConvertApp()
    app.initialize(argv=[ipynb_filename, '--to', 'jupyter_docx_bundler.DocxExporter'])
    app.convert_notebooks()
