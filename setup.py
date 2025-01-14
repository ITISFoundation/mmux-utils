# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib


here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="mmux_utils",
    version="0.0.1",
    description="Utilities for the MetaModeling UX",
    long_description=long_description,
    author="Javier Garcia Ordonez",
    author_email="ordonez@itis.swiss",
    packages=find_packages(),
    python_requires="==3.10",
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "seaborn",
        "scipy",
        "statsmodels",
    ],
)
