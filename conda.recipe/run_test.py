import sys

from nbconvert import nbconvertapp


# Check if nbconvert lists docx as available format
formats = nbconvertapp.get_export_names()
if 'docx' not in formats:
    sys.exit('*.docx not in nbconvert export-names.')
