# Contributing

## Setup development environment

## Download

Make a fork of the main [jupyter-docx-bundler repository](https://github.com/m-rossi/jupyter-docx-bundler) and clone the fork

```sh
git clone https://github.com/<your-github-username>/jupyter-docx-bundler
```

Contributions to jupyter-docx-bundler can then be made by submitting pull requests on GitHub.

## Install

To build the library you can install the necessary requirements using
pip or conda

```sh
cd jupyter-docx-bundler
```

### conda

Install all development requirements by executing

```sh
conda install --file requirements.txt --file requirements_test.txt
```

Install the package in _editable_ mode by executing

```sh
pip install --no-deps -e .
```

Make the package available to nbconvert and as an entry in the _Download As_ menu by executing

```sh
jupyter bundlerextension enable --py jupyter_docx_bundler --sys-prefix
```

### pip

Make sure you have [Pandoc](https://pandoc.org) installed, see [installing-pandoc](https://github.com/bebraw/pypandoc#installing-pandoc) for instructions.

Install the package in _editable_ mode and all necessary requirements by executing

```sh
pip install -e ".[test]"
```

Make the package available to nbconvert and as an entry in the _Download As_ menu by executing

```sh
jupyter bundlerextension enable --py jupyter_docx_bundler --sys-prefix
```

## Test

Test the package with [pytest](https://docs.pytest.org/en/latest/) by executing the following command

```sh
pytest .
```

## Build

### PyPI.org

This package follows the [packaing guide](https://packaging.python.org/tutorials/packaging-projects/) and you can create new packages for [PyPI](https://pypi.org/) by executing.

```sh
python setup.py sdist bdist_wheel
```

### Anaconda.org

Furthermore this package is also build with [conda-build](https://github.com/conda/conda-build) by executing the following command for Python 3.9

```sh
conda-build conda.recipe python=3.9
```

As documented in [noarch-builds](https://conda-forge.org/docs/maintainer/knowledge_base.html#noarch-builds) a Python- and OS-dependent build is necessary.

## Release

1. `git tag` a commit with a new version like `0.3.1`
2. Let the GitHub Actions pass, it builds all PyPI and conda-packages. You can download them as artifacts.
3. Put the PyPI-artifacts in the folder `dist`. Upload the packages to PyPI with
   ```sh
   twine upload dist/*
   ```
4. Upload the conda-packages to anaconda.org with
   ```sh
   anaconda upload jupyter-docx-bundler-0.3.1-py39_0.tar.bz2
   ```
