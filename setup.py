import os
from setuptools import setup

requirements = [
    'nbconvert>=5.3', 'pypandoc'
]

# Get the long description from the README file
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                       'README.md'),
          encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='jupyter_docx_bundler',
    version='0.1.0',
    description='Jupyter bundler extension to export notebook as a docx file',
    long_description=long_description,
    author='Marco Rossi',
    author_email='developer@marco-rossi.com',
    url='https://github.com/m-rossi/jupyter_docx_bundler',
    packages=['jupyter_docx_bundler'],
    python_requires='>=3, >=2.7',
    install_requires=requirements,
    keywords=['jupyter', 'docx', 'bundler'],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Jupyter',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ]
)
