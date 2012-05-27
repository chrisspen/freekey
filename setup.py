#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
#from distutils.core import setup
from setuptools import setup, find_packages
from setuptools.command.install import install as _install

from freekey import freekey

class install(_install):
    def run(self):
        _install.run(self)
        
        # Install bin.
        bin_src_fqfn = '%s/freekey/freekey.py' % (self.install_libbase,)
        bin_dst_fqfn = '%s/freekey' % (self.install_scripts,)
        print 'writing %s' % bin_dst_fqfn
        os.chmod(bin_src_fqfn, 0755)
        if os.path.isfile(bin_src_fqfn+'c'):
            os.chmod(bin_src_fqfn+'c', 0755)
        if os.path.isfile(bin_dst_fqfn):
            os.remove(bin_dst_fqfn)
        os.symlink(bin_src_fqfn, bin_dst_fqfn)
        #os.chmod(bin_dst_fqfn, 755)

setup(
    name='freekey',
    version=freekey.__version__,
    description='Allows limited keyboard use on a locked desktop',
    author='Chris Spencer',
    author_email='chrisspen@gmail.com',
    url='https://github.com/chrisspen/freekey',
    license='LGPL',
    packages=find_packages(),
    #install_requires=[],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    platforms=['Linux'],
    cmdclass={
        'install': install
    },
)