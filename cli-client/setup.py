import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='grahoot-py',  
    version='0.2',
    author="Fabian Specht",
    author_email="git@fabianspecht.xyz",
    description="cli client for grahoot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fabiancodes/grahoot",
    packages=["grahoot_cli"],
    install_requires=["inputimeout"],
    entry_points={
        'console_scripts': [
            'grahootcli=grahoot_cli.grahoot:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
 )
