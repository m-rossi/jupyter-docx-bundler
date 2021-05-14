# Jupyter docx bundler extension

[![PyPi Version](https://img.shields.io/pypi/v/jupyter-docx-bundler.svg)](https://pypi.org/project/jupyter-docx-bundler/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/jupyter-docx-bundler.svg)](https://anaconda.org/conda-forge/jupyter-docx-bundler)
[![Conda Version](https://img.shields.io/conda/vn/mrossi/jupyter-docx-bundler.svg)](https://anaconda.org/mrossi/jupyter-docx-bundler)
[![CI](https://github.com/m-rossi/jupyter-docx-bundler/workflows/CI/badge.svg)](https://github.com/m-rossi/jupyter-docx-bundler/actions)
[![codecov](https://codecov.io/gh/m-rossi/jupyter-docx-bundler/branch/main/graph/badge.svg)](https://codecov.io/gh/m-rossi/jupyter-docx-bundler)

Jupyter bundler extension to export notebook as a docx file

## Installation

### Using conda

```
conda install -c conda-forge jupyter-docx-bundler
```

### Using pip

Make sure you have [Pandoc](https://pandoc.org) installed, see [installing-pandoc](https://github.com/bebraw/pypandoc#installing-pandoc) for instructions.

```
pip install jupyter-docx-bundler
jupyter bundlerextension enable --py jupyter_docx_bundler --sys-prefix
```

## Usage

### Adding Metadata

The bundle extension uses metadata of the notebook, if you you provide it.

* `"title": "Notebook title"`
* `"authors": [{"name": "author1"}, {"name": "author2"}]`
* `"subtitle": "Notebook subtitle"`
* `"date": "Notebook date"`

The notebook metadata can be edited under _Edit_ -> _Edit Notebook Metadata_.

### Hiding inputs or complete code cells

You can hide individual code cells or just their inputs by defining cell tags:

* `nbconvert-remove-cell`: Remove the entire cell
* `nbconvert-remove-input`: Remove the input code of the cell

_(Currently there are no default values configured for these tags, the ones listed above are defined in my code and not in [nbconvert](https://github.com/jupyter/nbconvert). This may will change in the future.)_

Cell tags can be shown by activating the cell toolbar under _View_ -> _Cell Toolbar_ -> _Tags_.

#### Hiding all inputs

It is also possible to hide all inputs. To achive this you need to add the following lines to your notebook metadata:

```json
{
    "jupyter-docx-bundler": {
        "exclude_input": "True"
    }
}
```

The notebook metadata can be edited under _Edit_ -> _Edit Notebook Metadata_.

### Direct call from console (nbconvert)

To use the bundler direct from console the nbconvert utility can be used with target format docx:

* `jupyter nbconvert --execute --to=docx <source notebook>.ipynb --output <target document>.docx`

The `--execute` option should be used to ensure that the notebook is run before generation.

## Development

See [CONTRIBUTING](CONTRIBUTING.md)
