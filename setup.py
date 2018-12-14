# python3 setup.py build
import subprocess
import sys

from distutils.command.build import build
from setuptools import setup, Extension


class Build(build):
    """Customized setuptools build command - builds protos on build."""
    def run(self):
        protoc_command = ["make"]
        if subprocess.call(protoc_command) != 0:
            sys.exit(-1)
        build.run(self)


setup(
    name="mercuryapi",
    version="0.4.2",
    cmdclass={
        'build': Build,
    },
    ext_modules=[Extension("mercury",
                           sources=["mercury.c"],
                           libraries=["mercuryapi", "ltkc", "ltkctm"],
                           include_dirs=['build/mercuryapi/include'],
                           library_dirs=['build/mercuryapi/lib'])
                 ]

)
