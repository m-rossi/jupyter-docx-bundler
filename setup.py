from setuptools import setup

requirements = [
    'nbconvert>=5.3.1', # TODO Update nbconvert version when released
    'pypandoc>=1.4',
    'notebook>=5.0'
]

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except ImportError:
    long_description = open('README.md').read()

setup(
    author='Marco Rossi',
    author_email='developer@marco-rossi.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Jupyter',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    description='Jupyter bundler extension to export notebook as a docx file',
    extras_require={'test': ['pytest',
                             'pytest-lazy-fixture',
                             'matplotlib',
                             'nbformat',
                             'numpy'
                             'requests']},
    install_requires=requirements,
    keywords=['jupyter', 'docx', 'bundler'],
    license='MIT',
    long_description=long_description,
    name='jupyter_docx_bundler',
    packages=['jupyter_docx_bundler'],
    python_requires='>=3, >=2.7',
    setup_requires=['setuptools_scm'],
    url='https://github.com/m-rossi/jupyter_docx_bundler',
    use_scm_version=True,
)
