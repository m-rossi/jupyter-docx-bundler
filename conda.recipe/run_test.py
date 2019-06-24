import re
import subprocess
import sys

from nbconvert import nbconvertapp


# Check if bundler extension is enabled
out = subprocess.run(['jupyter-bundlerextension', 'list', '--sys-prefix'], capture_output=True)
if not re.search(r'Office Open XML \(\.docx\).*enable', out.stdout.decode('utf8')):
    sys.exit(1)

# Check if nbconvert lists docx as available format
formats = nbconvertapp.get_export_names()
if 'docx' not in formats:
    sys.exit(1)
