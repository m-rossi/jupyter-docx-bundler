from setuptools import setup

requirements = [
    'nbconvert>=5.3', 'pypandoc'
]

setup(
    name='jupyter_docx_bundler',
    version='0.1.0',
    description='Jupyter bundler extension to export notebook as a docx file',
    author='Marco Rossi',
    author_email='developer@marco-rossi.com',
    url='https://github.com/m-rossi/jupyter_docx_bundler',
    packages=['jupyter_docx_bundler'],
    install_requires=requirements,
    keywords=['jupyter', 'docx', 'bundler'],
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ]
)
