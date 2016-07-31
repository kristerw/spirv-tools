#!/usr/bin/env python

from setuptools import setup,  find_packages

with open("README.rst", "rt") as inf:
    readme = inf.read()

setup(
        name="spirv_tools",
        version="2016.1",
        description=(
            "Read/write/process Khronos's SPIR-V intermediate language"),
        long_description=readme,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Other Audience',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering',
            'Topic :: Software Development :: Libraries',
            'Topic :: Utilities',
            ],

        author="Krister Walfridsson",
        author_email="krister.walfridsson@gmail.com",
        license="MIT",
        url="http://documen.tician.de/genpy/",

        scripts=["bin/spirv-as", "bin/spirv-dis"],
        packages=find_packages())
