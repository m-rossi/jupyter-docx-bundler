# Jupyter docx bundler extension

[![PyPi Version](https://img.shields.io/pypi/v/jupyter_docx_bundler.svg)](https://pypi.org/project/jupyter-docx-bundler/)
[![Conda Version](https://img.shields.io/conda/vn/mrossi/jupyter_docx_bundler.svg)](https://anaconda.org/mrossi/jupyter_docx_bundler)

Jupyter bundler extension to export notebook as a docx file

## Install

### Installing with pip

Make sure you have [Pandoc](https://pandoc.org) installed.

```
pip install jupyter_docx_bundler
jupyter bundlerextension enable --py jupyter_docx_bundler --sys-prefix
```

### Installing with conda

```
conda install -c mrossi jupyter_docx_bundler
```

## Usage

### Adding Metadata

The bundle extension uses metadata of the notebook, if you you provide it.

* You can add a title by adding `"title": "Notebook title"`
* You can add authors by adding `"authors": [{"name": "author1"}, {"name": "author2"}]`

The notebook metadata can be edited under _Edit_ -> _Edit Notebook Metadata_.

### Hiding inputs or complete code cells

You can hide individual code cells or just their inputs by defining cell tags:

* `nbconvert-remove-cell`: Remove the entire cell
* `nbconvert-remove-input`: Remove the input code of the cell

_(Currently there are no default values configured for these tags, the ones listed above are defined in my code and not in [nbconvert](https://github.com/jupyter/nbconvert). This may will change in the future.)_

Cell tags can be shown by activating the cell toolbar under _View_ -> _Cell Toolbar_ -> _Tags_.

## Development

### Testing

The package is tested with [pytest](https://docs.pytest.org/en/latest/).

### Building

To build the package with [conda-build](https://github.com/conda/conda-build) you need to call
```
conda-build conda.recipe
```
