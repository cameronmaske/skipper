from setuptools import setup
from setuptools.command.test import test as TestCommand

import sys

install_requires = []
dependency_links = []


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


with open('requirements.txt') as f:
    requires = f.read().splitlines()
    for require in requires:
        install_requires.append(require)


setup(
    name='skipper',
    version='0.0.1',
    py_modules=['skipper'],
    include_package_data=True,
    dependency_links=['git+git://github.com/lfasnacht/fabric.git@local_tunnel#egg=fabric'],
    install_requires=install_requires,
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    entry_points="""
        [console_scripts]
        skipper=skipper.cli:cli
    """,
)
