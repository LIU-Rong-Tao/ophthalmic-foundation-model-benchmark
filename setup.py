import sys
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.egg_info import egg_info
from setuptools.command.sdist import sdist

sys.path.insert(0, str(Path.cwd()))

from build_support import sync_registry_data


class SyncBuildPy(build_py):
    def run(self):
        sync_registry_data()
        super().run()


class SyncEggInfo(egg_info):
    def run(self):
        sync_registry_data()
        super().run()


class SyncSdist(sdist):
    def run(self):
        sync_registry_data()
        super().run()


setup(cmdclass={"build_py": SyncBuildPy, "egg_info": SyncEggInfo, "sdist": SyncSdist})
