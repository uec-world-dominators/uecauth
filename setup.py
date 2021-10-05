import setuptools
import os
import uecauth.info

root_dir = os.path.abspath(os.path.dirname(__file__))


def _requirements():
    return [name.rstrip() for name in open(os.path.join(root_dir, 'requirements.txt')).readlines()]


def _readme():
    with open('README.md', 'rt', encoding='utf-8') as f:
        return f.read()


setuptools.setup(
    name=uecauth.info.name,
    packages=setuptools.find_packages(),

    version=uecauth.info.version,

    license=license,


    install_requires=_requirements(),

    author='shosatojp',
    author_email='me@shosato.jp',

    url='https://github.com/uec-world-dominators/uecauth',

    description='UEC Auth',
    long_description=_readme(),
    long_description_content_type='text/markdown',
    keywords='',

    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
