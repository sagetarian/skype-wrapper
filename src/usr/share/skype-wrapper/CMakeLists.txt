# project data
project(skype-indicator)
cmake_minimum_required(VERSION 2.6)

set(PYTHON_FILES indicator-applet-skype.py)
set(INDICATOR_FILES indicator-applet-skype)

install(FILES ${PYTHON_FILES} DESTINATION bin)
install(FILES ${INDICATOR_FILES} DESTINATION share/indicators/messages/applications)

# ------------------------------------------------------------
# packaging
set(CPACK_PACKAGE_DESCRIPTION "skype-indicator-applet")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Ubuntu Indicator Applet for Skype.")
set(CPACK_PACKAGE_NAME "skype-indicator-applet")
set(CPACK_DEBIAN_PACKAGE_DEPENDS "python-skype, skype")
set(CPACK_PACKAGE_CONTACT "Andreas Happe <andreashappe@snikt.net>")
set(CPACK_PACKAGE_VENDOR "none")
set(CPACK_PACKAGE_VERSION_MAJOR "0")
set(CPACK_PACKAGE_VERSION_MINOR "0")
set(CPACK_PACKAGE_VERSION_PATCH "2")

set(CPACK_GENERATOR "DEB;RPM;")
set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}-${CMAKE_SYSTEM_PROCESSOR}")

set(VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}")

include(CPack)
