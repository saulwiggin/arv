from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import multiprocessing
import os
import shutil
import unittest

# From http://stackoverflow.com/a/26698408/21028
class lazy_cythonize(list):
    def __init__(self, callback):
        self._list, self.callback = None, callback
    def c_list(self):
        if self._list is None: self._list = self.callback()
        return self._list
    def __iter__(self):
        for e in self.c_list(): yield e
    def __getitem__(self, ii): return self.c_list()[ii]
    def __len__(self): return len(self.c_list())

def configure_google_hashmap():
    # TODO: Perform out-of-source
    print("Configuring Google hash map")
    if os.system("3rd-party/sparsehash/configure") != 0:
        raise RuntimeError("Error configuring Google hash map")
    shutil.copy("src/config.h", "cpp/sparsehash/internal/sparseconfig.h")

class BuildExt(build_ext):
    def run(self):
        configure_google_hashmap()
        return build_ext.run(self)

def extensions():
    from Cython.Build import cythonize
    import multiprocessing

    exts = [
        Extension("_arv", [
                "cpp/dnatraits.cpp",
                "cpp/file.cpp",
                "cpp/fileptr.cpp",
                "cpp/filesize.cpp",
                "cpp/mmap.cpp",
                "cpp/parse_file.cpp",
                "cython/_arv.pyx",
            ],
            language="c++",
            include_dirs=["cpp"],
            extra_compile_args=["-std=c++11", "-g0"], # gcc specific
        ),
    ]
    #configure_google_hashmap()
    return cythonize(exts, nthreads=multiprocessing.cpu_count())

def slurp(filename):
    with open(filename, "rt") as f:
        return f.read()

def get_testsuite():
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test*.py")
    return suite

setup(
    name="arv",
    packages=["arv"],
    package_dir={"arv": "python/arv"},
    version="0.1",
    description="A fast 23andMe raw genome file parser",
    author="Christian Stigen Larsen",
    author_email="csl@csl.name",
    url="https://github.com/cslarsen/arv",
    license="https://www.gnu.org/licenses/gpl-3.0.html",
    long_description=slurp("README.rst"),
    keywords=[
        "23andMe",
        "bio",
        "biology",
        "biopython",
        "disease",
        "DNA",
        "gene",
        "genome",
        "health",
        "protein",
        "RNA",
        "RSID",
        "SNP",
    ],
    platforms=["unix", "linux", "osx"],
    install_requires=["cython>=0.25"],
    setup_requires=["cython>=0.25"],
    ext_modules=lazy_cythonize(extensions),
    test_suite="setup.get_testsuite",
    cmdclass={'build_ext': BuildExt},
)