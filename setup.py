# python3 setup.py build
import os
import subprocess
import sys
import zipfile

import requests

from distutils.command.build import build
from setuptools import setup, Extension

APIVER = '1.31.2.40'
APIVER_SHORT = '1.31.2'
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DONE_FILE = f'{CURRENT_DIR}/mercuryapi-{APIVER}/.done'


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


class CustomBuild(build):
    """Customized setuptools build command - builds protos on build."""

    def run(self):

        if not os.path.isfile(DONE_FILE):
            # Download API source
            api_source_file = f'https://www.jadaktech.com/wp-content/uploads/2018/11/mercuryapi-{APIVER_SHORT}.zip'
            zip_filename = f'mercuryapi-{APIVER_SHORT}.zip'

            if not os.path.isfile(f'{CURRENT_DIR}/{zip_filename}'):
                print('Downloading api')
                r = requests.get(api_source_file, allow_redirects=True)
                open(zip_filename, 'wb').write(r.content)

            # Extract API
            print('extracting ...')
            with zipfile.ZipFile(f'{CURRENT_DIR}/{zip_filename}', 'r') as zip_ref:
                zip_ref.extractall(CURRENT_DIR)

            # Patch
            print('patching ...')
            try:
                os.system(f"""patch -p0 -d {CURRENT_DIR}/mercuryapi-{APIVER} < {CURRENT_DIR}/mercuryapi.patch""")
            except IOError:
                sys.exit(-1)

            # Touch file
            touch(DONE_FILE)

        # Make API
        if subprocess.call(['make', '-C', f'mercuryapi-{APIVER}/c/src/api']) != 0:
            sys.exit(-1)

        # Move Files to include dir
        os.makedirs('build/mercuryapi/include', exist_ok=True)
        subprocess.call(
            """find mercuryapi-*/c/src/api -type f -name '*.h' ! -name '*_imp.h' | grep -v 'ltkc_win32' | xargs cp -t build/mercuryapi/include""",
            shell=True)

        # Move files to lib dir
        os.makedirs('build/mercuryapi/lib', exist_ok=True)
        subprocess.call(
            """find mercuryapi-*/c/src/api -type f -name '*.a' -or -name '*.so.1' | xargs cp -t build/mercuryapi/lib""",
            shell=True)

        # Run original python build
        build.run(self)


setup(
    name="mercuryapi",
    version="0.4.2",
    cmdclass={
        'build': CustomBuild,
    },
    ext_modules=[Extension("mercury",
                           sources=["mercury.c"],
                           libraries=["mercuryapi", "ltkc", "ltkctm"],
                           include_dirs=['build/mercuryapi/include'],
                           library_dirs=['build/mercuryapi/lib'])
                 ]

)
