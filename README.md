# Jupyter docx bundler extension

Jupyter bundler extension to export notebook as a docx file

## Install

### Installing from git

```
git clone https://github.com/m-rossi/jupyter_docx_bundler.git
cd jupyter_docx_bundler
pip install .
jupyter bundlerextension enable --py jupyter_docx_bundler --sys-prefix
```

## Usage

### Adding Metadata

The bundle extension uses metadata of the notebook, if you you provide it.

* You can add a title by adding `"name": "Notebook name"`
* You can add authors by adding `"authors": [{"name": "author1"}, {"name": "author2"}]`

The notebook metadata can be edited under _Edit_ -> _Edit Notebook Metadata_.

### Hiding inputs or complete code cells

You can hide individual code cells or just their inputs by defining cell tags:

* `nbconvert-remove-cell`: Remove the entire cell
* `nbconvert-remove-input`: Remove the input code of the cell

_(Currently there are no default values configured for these tags, the ones listed above are defined in my code and not in [nbconvert](https://github.com/jupyter/nbconvert). This may will change in the future.)_

Cell tags can be shown by activating the cell toolbar under _View_ -> _Cell Toolbar_ -> _Tags_.
