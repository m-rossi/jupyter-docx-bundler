import os
import tempfile
from . import converters
from nbconvert.exporters import Exporter


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
        # preprocess notebook
        model['content'] = converters.preprocess(model['content'])

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


class DocxExporter(Exporter):
    """Convert a notebook to docx
    This is the API which nbconvert calls.
    """
    output_mimetype = 'application/docx'

    def _file_extension_default(self):
        return '.docx'

    def from_notebook_node(self, nb, resources=None, **kw):
        nb_copy, resources = super().from_notebook_node(nb, resources)

        with tempfile.TemporaryDirectory() as tempdir:
            # preprocess notebook
            nb_copy = converters.preprocess(nb_copy)

            # Prepare file names
            htmlfile = os.path.join(tempdir, resources['metadata']['name'] + '.html')
            docxfile = os.path.join(tempdir, resources['metadata']['name'] + '.docx')

            # Convert notebook to html
            converters.notebook_to_html(nb_copy, htmlfile)

            # Convert html to docx (handler is not required)
            converters.html_to_docx(htmlfile,
                                    docxfile,
                                    metadata=resources['metadata'])

            # Send file to handler
            with open(docxfile, 'rb') as bundle_file:
                fileContents = bundle_file.read()

        return fileContents, resources
