from setuptools import setup
from setuptools.command.test import test as TestCommand

import sys
import re


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


def find_version():
    with open('skipper/__init__.py') as f:
        version_file = f.read()
        version_match = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")

requires = [
    'click==2.0',
    'boto==2.27.0',
    'Fabric==1.9.0',
    'docker-py==0.3.2',
    'Jinja2==2.7.2',
    'PyYAML==3.10',
    'requests==2.2.1',
    'texttable==0.8.1'
]

setup(
    name='skipper',
    author="Cameron Maske",
    author_email="cameronmaske@gmail.com",
    version=find_version(),
    description="Build, deploy and orchestrate your application using Docker.",
    url="https://github.com/cameronmaske/skipper",
    py_modules=['skipper'],
    include_package_data=True,
    install_requires=requires,
    tests_require=['pytest'],
    license="BSD",
    cmdclass={'test': PyTest},
    keywords=["docker", "paas", "coreos"],
    entry_points="""
        [console_scripts]
        skipper=skipper.cli:cli
    """,
)
