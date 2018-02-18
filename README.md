# Jupyter docx bundler extension

[![PyPi Version](https://img.shields.io/pypi/v/jupyter_docx_bundler.svg)](https://pypi.python.org/pypi/jupyter_docx_bundler)

Jupyter bundler extension to export notebook as a docx file

## Install

Make sure you have [Pandoc](https://pandoc.org) installed. You can easily install it from conda with `conda install pandoc`.

### Installing with pip

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

## Known issues

### Out of Memory error on Windows

Converting large files on Windows can fail because by default pandoc can only use 2 GB of memory, see the discussion here: [jgm/pandoc#3669](https://github.com/jgm/pandoc/issues/3669).
There is a workaround mentioned here: [Fixing pandoc "out of memory" errors on Windows](https://jonathanchang.org/blog/fixing-pandoc-out-of-memory-errors-on-windows/). It worked for me on my Windows 10, 64-bit machine.

Therefore I've forked [conda-forge/pandoc-feedstock](https://github.com/conda-forge/pandoc-feedstock) and modified it to include the necessary commands: [m-rossi/pandoc-feedstock](https://github.com/m-rossi/pandoc-feedstock). Now you can install my version of pandoc with
```
conda install -c mrossi pandoc
```
