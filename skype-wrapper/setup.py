#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; mode: python -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: t -*-
# vi: set ft=python sts=4 ts=4 sw=4 noet 
#
# Copyright 2011 Shannon Black
#
# Authors:
#    Shannon A Black <shannon@netforge.co.za>
#
# This program is free software: you can redistribute it and/or modify it 
# under the terms of either or both of the following licenses:
#
# 1) the GNU Lesser General Public License version 3, as published by the 
# Free Software Foundation; and/or
# 2) the GNU Lesser General Public License version 2.1, as published by 
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the applicable version of the GNU Lesser General Public 
# License for more details.
#
# You should have received a copy of both the GNU Lesser General Public 
# License version 3 and version 2.1 along with this program.  If not, see 
# <http://www.gnu.org/licenses/>
#

from distutils.core import setup
#from distutils.cmd import Command
from distutils.command.install_data import install_data
import os

#class Uninstall(Command):
#  def run(self):
#    return

class InstallData(install_data):
  def run (self):
    os.system('glib-compile-schemas /usr/share/glib-2.0/schemas/')
    install_data.run (self)
    return

setup(name='skype-wrapper',
      version='0.6.2.0',
      description='Integrate Skype with Unity',
      author='Shannon Black',
      author_email='shannon@netforge.co.za',
      url='https://github.com/sagetarian/skype-wrapper/',
      scripts=['skype-wrapper', 's-wrapper-settings'],
      data_files=[('share/glib-2.0/schemas', ['data/schemas/apps.skype-wrapper.gschema.xml']),
        ('share/applications', ['data/applications/skype-wrapper.desktop', 'data/applications/skype-wrapper-settings.desktop']),
        ('share/pixmaps', ['data/pixmaps/skype-wrapper.svg']),
        ('share/skype-wrapper', ['src/helpers.py', 'src/indicator-applet-skype','src/indicator-applet-skype.py','src/postinst.py','src/settings.py','src/shared.py','src/skype-wrapper.py','src/unitylauncher.py','src/uisettings.py']),
        ('share/skype-wrapper/icons', ['src/icons/skype-24.svg','src/icons/skype-wrapper-16.png','src/icons/skype-wrapper-22.png','src/icons/skype-wrapper-24.png','src/icons/skype-wrapper-48.svg'])
      ],
      cmdclass={'install_data': InstallData},#, 'uninstall': Uninstall},
     )

