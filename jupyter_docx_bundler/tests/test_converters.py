from .. import converters


def test_notebookcontent_to_docxbytes(test_notebook):
    converters.notebookcontent_to_docxbytes(
        test_notebook,
        'download-notebook',
        test_notebook['metadata']['path'],
    )
