#!/usr/bin/env python

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
      version='0.5.2.9',
      description='Integrate Skype with Unity',
      author='Shannon Black',
      author_email='shannon@netforge.co.za',
      url='https://github.com/sagetarian/skype-wrapper/',
      scripts=['skype-wrapper'],
      data_files=[('share/glib-2.0/schemas', ['data/schemas/apps.skype-wrapper.gschema.xml']),
        ('share/applications', ['data/applications/skype-wrapper.desktop']),
        ('share/pixmaps', ['data/pixmaps/skype-wrapper.svg']),
        ('share/skype-wrapper', ['src/helpers.py', 'src/indicator-applet-skype','src/indicator-applet-skype.py','src/postinst.py','src/settings.py','src/shared.py','src/skype-wrapper.py','src/unitylauncher.py']),
        ('share/skype-wrapper/icons', ['src/icons/skype-24.svg','src/icons/skype-wrapper-16.png','src/icons/skype-wrapper-22.png','src/icons/skype-wrapper-24.png','src/icons/skype-wrapper-48.svg'])
      ],
      cmdclass={'install_data': InstallData},#, 'uninstall': Uninstall},
     )

