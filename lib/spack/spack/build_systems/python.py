##############################################################################
# Copyright (c) 2013-2016, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################

import inspect
import os

from spack.directives import depends_on, extends
from spack.package import PackageBase, run_after

from llnl.util.filesystem import working_dir


class PythonPackage(PackageBase):
    """Specialized class for packages that are built using Python
    setup.py files

    This class provides the following phases that can be overridden:

    * build
    * build_py
    * build_ext
    * build_clib
    * build_scripts
    * clean
    * install
    * install_lib
    * install_headers
    * install_scripts
    * install_data
    * sdist
    * register
    * bdist
    * bdist_dumb
    * bdist_rpm
    * bdist_wininst
    * upload
    * check

    These are all standard setup.py commands and can be found by running:

    .. code-block:: console

       $ python setup.py --help-commands

    By default, only the 'build' and 'install' phases are run, but if you
    need to run more phases, simply modify your ``phases`` list like so:

    .. code-block:: python

       phases = ['build_ext', 'install', 'bdist']

    Each phase provides a function <phase> that runs:

    .. code-block:: console

       $ python setup.py --no-user-cfg <phase>

    Each phase also has a <phase_args> function that can pass arguments to
    this call. All of these functions are empty except for the ``install_args``
    function, which passes ``--prefix=/path/to/installation/directory``.

    If you need to run a phase which is not a standard setup.py command,
    you'll need to define a function for it like so:

    .. code-block:: python

       def configure(self, spec, prefix):
           self.setup_py('configure')
    """
    # Default phases
    phases = ['build', 'install']

    # Name of modules that the Python package provides
    # This is used to test whether or not the installation succeeded
    # These names generally come from running:
    #
    # >>> import setuptools
    # >>> setuptools.find_packages()
    #
    # in the source tarball directory
    import_modules = []

    # To be used in UI queries that require to know which
    # build-system class we are using
    build_system_class = 'PythonPackage'

    #: Callback names for build-time test
    build_time_test_callbacks = ['test']

    #: Callback names for install-time test
    install_time_test_callbacks = ['import_module_test']

    extends('python')

    depends_on('python', type=('build', 'run'))

    def setup_file(self):
        """Returns the name of the setup file to use."""
        return 'setup.py'

    @property
    def build_directory(self):
        """The directory containing the ``setup.py`` file."""
        return self.stage.source_path

    def python(self, *args, **kwargs):
        inspect.getmodule(self).python(*args, **kwargs)

    def setup_py(self, *args, **kwargs):
        setup = self.setup_file()

        with working_dir(self.build_directory):
            self.python(setup, '--no-user-cfg', *args, **kwargs)

    def _setup_command_available(self, command):
        """Determines whether or not a setup.py command exists.

        Args:
            command (str): The command to look for

        Returns:
            bool: True if the command is found, else False
        """
        kwargs = {
            'output': os.devnull,
            'error':  os.devnull,
            'fail_on_error': False
        }

        python = inspect.getmodule(self).python
        setup = self.setup_file()

        python(setup, '--no-user-cfg', command, '--help', **kwargs)
        return python.returncode == 0

    # The following phases and their descriptions come from:
    #   $ python setup.py --help-commands

    # Standard commands

    def build(self, spec, prefix):
        """Build everything needed to install."""
        args = self.build_args(spec, prefix)

        self.setup_py('build', *args)

    def build_args(self, spec, prefix):
        """Arguments to pass to build."""
        return []

    def build_py(self, spec, prefix):
        '''"Build" pure Python modules (copy to build directory).'''
        args = self.build_py_args(spec, prefix)

        self.setup_py('build_py', *args)

    def build_py_args(self, spec, prefix):
        """Arguments to pass to build_py."""
        return []

    def build_ext(self, spec, prefix):
        """Build C/C++ extensions (compile/link to build directory)."""
        args = self.build_ext_args(spec, prefix)

        self.setup_py('build_ext', *args)

    def build_ext_args(self, spec, prefix):
        """Arguments to pass to build_ext."""
        return []

    def build_clib(self, spec, prefix):
        """Build C/C++ libraries used by Python extensions."""
        args = self.build_clib_args(spec, prefix)

        self.setup_py('build_clib', *args)

    def build_clib_args(self, spec, prefix):
        """Arguments to pass to build_clib."""
        return []

    def build_scripts(self, spec, prefix):
        '''"Build" scripts (copy and fixup #! line).'''
        args = self.build_scripts_args(spec, prefix)

        self.setup_py('build_scripts', *args)

    def clean(self, spec, prefix):
        """Clean up temporary files from 'build' command."""
        args = self.clean_args(spec, prefix)

        self.setup_py('clean', *args)

    def clean_args(self, spec, prefix):
        """Arguments to pass to clean."""
        return []

    def install(self, spec, prefix):
        """Install everything from build directory."""
        args = self.install_args(spec, prefix)

        self.setup_py('install', *args)

    def install_args(self, spec, prefix):
        """Arguments to pass to install."""
        args = ['--prefix={0}'.format(prefix)]

        # This option causes python packages (including setuptools) NOT
        # to create eggs or easy-install.pth files.  Instead, they
        # install naturally into $prefix/pythonX.Y/site-packages.
        #
        # Eggs add an extra level of indirection to sys.path, slowing
        # down large HPC runs.  They are also deprecated in favor of
        # wheels, which use a normal layout when installed.
        #
        # Spack manages the package directory on its own by symlinking
        # extensions into the site-packages directory, so we don't really
        # need the .pth files or egg directories, anyway.
        if ('py-setuptools' == spec.name or          # this is setuptools, or
            'py-setuptools' in spec._dependencies):  # it's an immediate dep
            args += ['--single-version-externally-managed', '--root=/']

        return args

    def install_lib(self, spec, prefix):
        """Install all Python modules (extensions and pure Python)."""
        args = self.install_lib_args(spec, prefix)

        self.setup_py('install_lib', *args)

    def install_lib_args(self, spec, prefix):
        """Arguments to pass to install_lib."""
        return []

    def install_headers(self, spec, prefix):
        """Install C/C++ header files."""
        args = self.install_headers_args(spec, prefix)

        self.setup_py('install_headers', *args)

    def install_headers_args(self, spec, prefix):
        """Arguments to pass to install_headers."""
        return []

    def install_scripts(self, spec, prefix):
        """Install scripts (Python or otherwise)."""
        args = self.install_scripts_args(spec, prefix)

        self.setup_py('install_scripts', *args)

    def install_scripts_args(self, spec, prefix):
        """Arguments to pass to install_scripts."""
        return []

    def install_data(self, spec, prefix):
        """Install data files."""
        args = self.install_data_args(spec, prefix)

        self.setup_py('install_data', *args)

    def install_data_args(self, spec, prefix):
        """Arguments to pass to install_data."""
        return []

    def sdist(self, spec, prefix):
        """Create a source distribution (tarball, zip file, etc.)."""
        args = self.sdist_args(spec, prefix)

        self.setup_py('sdist', *args)

    def sdist_args(self, spec, prefix):
        """Arguments to pass to sdist."""
        return []

    def register(self, spec, prefix):
        """Register the distribution with the Python package index."""
        args = self.register_args(spec, prefix)

        self.setup_py('register', *args)

    def register_args(self, spec, prefix):
        """Arguments to pass to register."""
        return []

    def bdist(self, spec, prefix):
        """Create a built (binary) distribution."""
        args = self.bdist_args(spec, prefix)

        self.setup_py('bdist', *args)

    def bdist_args(self, spec, prefix):
        """Arguments to pass to bdist."""
        return []

    def bdist_dumb(self, spec, prefix):
        '''Create a "dumb" built distribution.'''
        args = self.bdist_dumb_args(spec, prefix)

        self.setup_py('bdist_dumb', *args)

    def bdist_dumb_args(self, spec, prefix):
        """Arguments to pass to bdist_dumb."""
        return []

    def bdist_rpm(self, spec, prefix):
        """Create an RPM distribution."""
        args = self.bdist_rpm(spec, prefix)

        self.setup_py('bdist_rpm', *args)

    def bdist_rpm_args(self, spec, prefix):
        """Arguments to pass to bdist_rpm."""
        return []

    def bdist_wininst(self, spec, prefix):
        """Create an executable installer for MS Windows."""
        args = self.bdist_wininst_args(spec, prefix)

        self.setup_py('bdist_wininst', *args)

    def bdist_wininst_args(self, spec, prefix):
        """Arguments to pass to bdist_wininst."""
        return []

    def upload(self, spec, prefix):
        """Upload binary package to PyPI."""
        args = self.upload_args(spec, prefix)

        self.setup_py('upload', *args)

    def upload_args(self, spec, prefix):
        """Arguments to pass to upload."""
        return []

    def check(self, spec, prefix):
        """Perform some checks on the package."""
        args = self.check_args(spec, prefix)

        self.setup_py('check', *args)

    def check_args(self, spec, prefix):
        """Arguments to pass to check."""
        return []

    # Testing

    def test(self):
        """Run unit tests after in-place build.

        These tests are only run if the package actually has a 'test' command.
        """
        if self._setup_command_available('test'):
            args = self.test_args(self.spec, self.prefix)

            self.setup_py('test', *args)

    def test_args(self, spec, prefix):
        """Arguments to pass to test."""
        return []

    run_after('build')(PackageBase._run_default_build_time_test_callbacks)

    def import_module_test(self):
        """Attempts to import the module that was just installed.

        This test is only run if the package overrides
        :py:attr:`import_modules` with a list of module names."""

        # Make sure we are importing the installed modules,
        # not the ones in the current directory
        with working_dir('..'):
            for module in self.import_modules:
                self.python('-c', 'import {0}'.format(module))

    run_after('install')(PackageBase._run_default_install_time_test_callbacks)

    # Check that self.prefix is there after installation
    run_after('install')(PackageBase.sanity_check_prefix)
