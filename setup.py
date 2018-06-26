""" Setup file """
import os

from setuptools import setup


HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, "README.rst")) as f:
    README = f.read()


def get_version():
    with open(os.path.join(HERE, "brainfm/__init__.py")) as f:
        for line in f:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1])


if __name__ == "__main__":
    setup(
        name="brainfm",
        version=get_version(),
        description="Unofficial python API for brain.fm",
        long_description=README,
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5",
            "Topic :: Software Development :: Libraries"
        ],
        author="Joe Cross",
        author_email="joe.mcross@gmail.com",
        url="https://github.com/numberoverzero/brainfm",
        license="MIT",
        keywords="brainfm api",
        platforms="any",
        include_package_data=True,
        packages=[
            "brainfm",
            "brainfm.main"
        ],
        entry_points={
            "console_scripts": [
                "brain = brainfm.main.cli:main"
            ]
        },
        install_requires=[
            "click>=6",
            "jmespath>=0.9",
            "requests>=2.11",
            "terminaltables>=3.1"
        ],
    )
