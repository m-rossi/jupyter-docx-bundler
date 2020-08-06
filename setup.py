from setuptools import setup


with open('README.md') as f:
    long_description = f.read()

setup(
    author='Marco Rossi',
    author_email='developer@marco-rossi.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Jupyter',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description='Jupyter bundler extension to export notebook as a docx file',
    extras_require={
        'test': [
            'matplotlib>=3.1',
            'mock',
            'nbformat',
            'numpy',
            'pillow>=6.0.0',
            'pytest',
            'pytest-cov',
            'pytest-lazy-fixture',
        ],
    },
    install_requires=[
        'nbconvert>=5.5',
        'notebook>=5.0',
        'pandocfilters',
        'pypandoc>=1.4',
        'requests',
        'tornado',
    ],
    keywords=[
        'jupyter',
        'docx',
        'bundler',
    ],
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='jupyter-docx-bundler',
    packages=[
        'jupyter_docx_bundler',
        'jupyter_docx_bundler.tests',
    ],
    python_requires='>=3.6',
    setup_requires=[
        'setuptools>=38.6.0',
        'setuptools_scm',
    ],
    url='https://github.com/m-rossi/jupyter-docx-bundler',
    use_scm_version=True,
    entry_points={
        'nbconvert.exporters': [
            'docx = jupyter_docx_bundler:DocxExporter',
        ],
    }
)
