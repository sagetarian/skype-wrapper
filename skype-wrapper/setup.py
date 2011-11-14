#!/usr/bin/env python

from distutils.core import setup

setup(name='skype-wrapper',
      version='0.5.2.5',
      description='Integrate Skype with Unity',
      author='Shannon Black',
      author_email='shannon@netforge.co.za',
      url='https://github.com/sagetarian/skype-wrapper/',
      scripts=['skype-wrapper'],
      data_files=[('share/schemas', ['data/schemas/applets.skype-wrapper-py.gschema.xml']),
        ('share/applications', ['data/applications/skype-wrapper.desktop']),
        ('share/pixmaps', ['data/pixmaps/skype-wrapper.svg']),
        ('share/skype-wrapper', ['src/indicator-applet-skype','src/indicator-applet-skype.py','src/postinst.py','src/settings.py','src/shared.py','src/skype-wrapper.py','src/unitylauncher.py']),
        ('share/skype-wrapper/icons', ['src/icons/skype-24.svg','src/icons/skype-wrapper-16.png','src/icons/skype-wrapper-22.png','src/icons/skype-wrapper-24.png','src/icons/skype-wrapper-48.svg'])
      ],
     )

