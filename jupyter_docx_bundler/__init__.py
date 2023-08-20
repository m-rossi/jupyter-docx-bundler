from nbconvert.exporters import Exporter

from . import converters


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
