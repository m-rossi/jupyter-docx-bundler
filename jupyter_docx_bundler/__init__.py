import os
import tempfile
from . import converters


def _jupyter_bundlerextension_paths():
    """ Declare bundler extensions provided by this package."""

    return [{
        # unique bundler name
        "name": "docx_bundler",
        # module containing bundle function
        "module_name": "jupyter_docx_bundler",
        # human-redable menu item label
        "label": "Office Open XML (.docx)",
        # group under 'deploy' or 'download' menu
        "group": "download",
    }]


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
    notebook_filename = os.path.basename(model['name'])
    notebook_name = os.path.splitext(notebook_filename)[0]

    with tempfile.TemporaryDirectory() as tempdir:
        # prepare file names
        htmlfile = os.path.join(tempdir, f'{notebook_name}.html')
        docxfile = os.path.join(tempdir, f'{notebook_name}.docx')

        # convert notebook to html
        converters.notebook_to_html(model['content'], htmlfile)

        # convert html to docx
        converters.html_to_docx(htmlfile,
                                docxfile,
                                metadata=model['content']['metadata'],
                                handler=handler)

        # Set headers to trigger browser download
        handler.set_header('Content-Disposition',
                           f'attachment; filename="'
                           f'{os.path.basename(docxfile)}"')
        handler.set_header('Content-Type',
                           'application/vnd.openxmlformats-officedocument.word'
                           'processingml.document')

        # send file to handler
        with open(docxfile, 'rb') as bundle_file:
            handler.write(bundle_file.read())

        # Return the buffer value as the response
        handler.finish()
