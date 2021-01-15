from setuptools import Extension, setup
from Cython.Build import cythonize

extensions = [Extension("fastxml", ["fastxml.pyx", "yxml.c"])]

setup(ext_modules=cythonize(extensions))
