# Jupyter docx bundler extension

Jupyter bundler extension to export notebook as a docx file

## Install

### Installing from git

```
git clone https://github.com/m-rossi/jupyter_docx_bundler.git
cd hdf5widget
pip install .
jupyter bundlerextension enable --py jupyter_docx_bundler --sys-prefix
```

## Usage

### Adding Metadata

The bundle extension uses metadata of the notebook, if you you provide it. You can add a title to your docx-document by adding `"name": "Notebook name"` to the notebook metadata, which can be edited under _Edit_ -> _Edit Notebook Metadata_.
