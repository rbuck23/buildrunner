"""
Copyright (C) 2020 Adobe
"""

from __future__ import print_function

import importlib.machinery
import os
import subprocess
import sys
import types

from setuptools import setup, find_packages

_VERSION = '1.3.3'

_SOURCE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)
_BUILDRUNNER_DIR = os.path.join(_SOURCE_DIR, 'buildrunner')
_VERSION_FILE = os.path.join(_BUILDRUNNER_DIR, 'version.py')

THIS_DIR = os.path.dirname(__file__)


def read_requirements(filename):
    """
    :param filename:
    """
    requires = []
    dep_links = []
    try:
        with open(os.path.join(THIS_DIR, filename)) as robj:
            lnr = 0
            for line in robj.readlines():
                lnr += 1
                _line = line.strip()
                if not _line:
                    continue
                if _line.startswith('#'):
                    continue

                if _line.startswith('--extra-index-url'):
                    args = _line.split(None, 1)
                    if len(args) != 2:
                        print(
                            'ERROR: option "--extra-index-url" must have a URL argument: {}:{}'.format(
                                filename,
                                lnr
                            ),
                            file=sys.stderr,
                        )
                        continue
                    dep_links.append(args[1])

                elif _line[0].isalpha():
                    requires.append(_line)

                else:
                    print(
                        'ERROR: {}:{}:"{}" does not appear to be a requirement'.format(
                            filename,
                            lnr,
                            _line
                        ),
                        file=sys.stderr,
                    )

    except IOError as err:
        sys.stderr.write('Failure reading "{0}": {1}\n'.format(filename, err))
        sys.exit(err.errno)

    return requires, dep_links


REQUIRES, DEP_LINKS = read_requirements('requirements.txt')
requirements, dependency_links = read_requirements('test_requirements.txt')
TEST_REQUIRES = requirements
DEP_LINKS.extend(dependency_links)


def get_version():
    """
    Call out to the git command line to get the current commit "number".
    """
    _ver = _VERSION

    try:
        cmd = subprocess.Popen(
            args=[
                'git',
                'rev-list',
                '--count',
                'HEAD',
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout = cmd.communicate()[0]
        outdata = stdout.strip().decode('utf-8')
        if cmd.returncode == 0:
            _version = '{0}.{1}'.format(_ver, outdata)

            # write the version file
            if os.path.exists(_BUILDRUNNER_DIR):
                with open(_VERSION_FILE, 'w') as _ver:
                    _ver.write("__version__ = '%s'\n" % _version)
    except:
        pass

    if os.path.exists(_VERSION_FILE):
        loader = importlib.machinery.SourceFileLoader('buildrunnerversion', _VERSION_FILE)
        version_mod = types.ModuleType(loader.name)
        loader.exec_module(version_mod)
        _version = version_mod.__version__  # pylint: disable=no-member
    else:
        _version += '.DEVELOPMENT'

    return _version


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as fobj:
    long_description = fobj.read().strip()

setup(
    name='buildrunner',
    version=get_version(),
    author='Adobe',
    author_email="noreply@adobe.com",
    license="MIT",
    url="https://github.com/adobe/buildrunner",
    description="Docker-based build tool",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
    scripts=[
        'bin/buildrunner',
    ],
    package_data={
        'buildrunner': ['SourceDockerfile'],
        'buildrunner.sshagent': [
            'SSHAgentProxyImage/Dockerfile',
            'SSHAgentProxyImage/run.sh',
            'SSHAgentProxyImage/login.sh',
        ],
    },
    install_requires=REQUIRES,
    tests_require=TEST_REQUIRES,
    dependency_links=DEP_LINKS,
    test_suite='tests',
)

# Local Variables:
# fill-column: 100
# End:
