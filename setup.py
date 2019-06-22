import os
import shutil
import platform
from setuptools import setup

install_dependencies = ['PyQt5']
setup(
    name='osx-tapman', 
    version='0.1', 
    license='GPLv3', 
    author='kanishka-linux', 
    author_email='kanishka.linux@gmail.com', 
    url='https://github.com/kanishka-linux/osx-tapman', 
    long_description="README.md", 
    packages=['osx_tapman'], 
    include_package_data=True, 
    entry_points={
        'gui_scripts':['osx-tapman = osx_tapman.osx_tapman:main'], 
        'console_scripts':['osx-tapman-console = osx_tapman.osx_tapman:main']
        }, 
    install_requires=install_dependencies, 
    description="CPU and Battery temperature monitor for OSX", 
)
