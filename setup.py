import sys

from setuptools import setup, find_packages


cffi_modules = [
    'cffi_builders/jpg_c_build.py:ffi',
    'cffi_builders/png_c_build.py:ffi',
    'cffi_builders/sdl_c_build.py:ffi',
    'cffi_builders/sdl_keys_c_build.py:ffi',
]


if sys.platform.startswith("darwin"):
    # If we're on Mac OS X, we need extra stuff.
    cffi_modules.append('cffi_builders/macosx_c_build.py:ffi')


setup(
    name="pygame_cffi",
    version="0.0.1",
    url='http://github.com/CTPUG/pygame_cffi',
    license='LGPL',
    description="A cffi-based SDL wrapper that copies the pygame API.",
    long_description=open('README.md', 'r').read(),
    packages=find_packages(),
    include_package_data=True,
    scripts=[
    ],
    setup_requires=[
        'cffi>=1.0.3',
    ],
    cffi_modules=cffi_modules,
    install_requires=[
        'cffi>=1.0.3',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: LGPL License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
