import os
from pathlib import Path

from nbconvert.exporters import Exporter
from tornado import gen

from . import converters


def _jupyter_bundlerextension_paths():
    """ Declare bundler extensions provided by this package."""

    return [
        {
            # unique bundler name
            'name': 'docx_bundler',
            # module containing bundle function
            'module_name': 'jupyter_docx_bundler',
            # human-redable menu item label
            'label': 'Office Open XML (.docx)',
            # group under 'deploy' or 'download' menu
            'group': 'download',
        }
    ]  # pragma: no cover


@gen.coroutine
def bundle(handler, model):
    """ Create a compressed tarball containing the notebook document.

    Parameters
    ----------

    handler : tornado.web.RequestHandler
        Handler that serviced the bundle request
    model : dict
        Notebook model from the configured ContentManager
    """

    # prepare notebook
    if Path(model['path']).is_absolute():
        notebook_path = Path(model['path']).parent
    else:
        notebook_path = (Path.cwd() / model['path']).parent
    notebook_filename = os.path.basename(model['name'])
    notebook_name = os.path.splitext(notebook_filename)[0]

    # Set headers to trigger browser download
    handler.set_header(
        'Content-Disposition', f'attachment; filename="{os.path.basename(notebook_name)}.docx"',
    )
    handler.set_header(
        'Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )

    # send content to handler
    yield handler.write(
        converters.notebookcontent_to_docxbytes(model['content'], notebook_filename, notebook_path)
    )

    # Return the buffer value as the response
    handler.finish()


class DocxExporter(Exporter):
    """Convert a notebook to docx
    This is the API which nbconvert calls.
    """

    output_mimetype = 'application/docx'

    def _file_extension_default(self):
        return '.docx'

    def from_notebook_node(self, nb, resources=None, **kw):
        nb_copy, resources = super().from_notebook_node(nb, resources)

        return (
            converters.notebookcontent_to_docxbytes(
                nb_copy, resources['metadata']['name'], resources['metadata']['path'],
            ),
            resources,
        )
