from pathlib import Path

import pypandoc

from .. import converters


def test_notebookcontent_to_docxbytes(test_notebook):
    converters.notebookcontent_to_docxbytes(
        test_notebook, 'test-notebook', test_notebook['metadata']['path'],
    )


def test_image_conversion(tmpdir, images_notebook):
    # convert notebook to docx
    docxbytes = converters.notebookcontent_to_docxbytes(
        images_notebook, 'test-notebook', images_notebook['metadata']['path'],
    )

    # write to file on disk
    filename = tmpdir / 'images-notebook.docx'
    with open(filename, 'wb') as file:
        file.write(docxbytes)

    # convert to markdown and extract media
    pypandoc.convert(
        f'{filename}',
        'markdown',
        'docx',
        extra_args=['--extract-media', f'{tmpdir}'],
        outputfile=f'{tmpdir / "images-notebook.md"}',
    )

    # compare number of extracted media with generated media
    media = list(Path(tmpdir / 'media').glob('*.*'))
    assert images_notebook['metadata']['image_count'] == len(media),\
        'Number of generated images does not match in docx-document.'
