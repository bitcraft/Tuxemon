"""
Responsible for building the Windows binary package of the
game with cx_Freeze and python 3.6

To build the package on Windows, run the following command on Windows:
    `python3 build_win32_py36.py build`

"""
from itertools import chain
from functools import partial
from os import scandir
from os.path import join, relpath

from cx_Freeze import Executable, setup


def mangle(root, path):
    """ Required due to Tuxemon's folder layout
    
    :param root: 
    :param path: 
    :return: 
    """

    return join(root, path), path


def scantree(path, root):
    """ Recursively find and return tuples for cx_Freeze
    
    relpath is used due to the layout of the tuxemon code
    
    :param path: 
    :param root: 
    :return: 
    """

    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path, root)
        else:   # path to find, path to copy to
            yield entry.path, relpath(entry.path, root)


# TODO: rumble support
"""
excludes is maintained by monitoring the build folder and adding packages
to the list that don't belong.

core is added to excludes because the plugin system confuses distutils
and doesn't include the right files and generally just makes a mess of it.
core is added to 'include_files' so that the folder tree is copied without
any modification to the structure.
"""
excludes = [
    'core', # don't remove; needs to be copied through includes
    "tkinter",
    "tk",
    "sdl2",
    "ctypes",
    "email",
    "curses",
    "setuptools",
    "unittest",
    "pydoc_data",
    "test",
    "pygame.camera",
    "numpy",
    "distutils",
    "pyglet",
    "OpenGL",
    "dbm",
]
# modules/packages not detected by cx_freeze
install_requires = [
    'pygame',
    'pytmx',
    'pyscroll',
    # 'neteria'

    # add additional requirements that don't get picked up
    # by distutils/cx_Freeze; these are found through trial error
    'ConfigParser',
    'json',
    'importlib',
    'shelve',
]

root_path = 'tuxemon'
core_path = join(root_path, 'core')
reasources_path = join(root_path, 'resources')
root_includes = map(partial(mangle, root_path), ['tuxemon.cfg'])

datafiles = chain(
    root_includes,
    scantree(reasources_path, root_path),
    scantree(core_path, root_path))

build_exe_options = {
    "packages": install_requires,
    "excludes": excludes,
    'include_files': datafiles,
    "optimize": 2,
}

# TODO: Consolidate all this random metadata about the project
main_script = join(root_path, 'tuxemon.py')
icon_path = join(reasources_path, 'gfx', 'icon.ico')

setup(
    name="Tuxemon",
    version="0.3.2",

    # py2exe specific options
    options={
        'build_exe': build_exe_options,
    },
    executables=[Executable(main_script, base="Win32GUI", icon=icon_path)],

    # possibly only required for pypi
    description="Free, open source monster-fighting RPG.",
    keywords="monster fighting game rpg pygame",
    url="https://tuxemon.org/",
    license="LGPLv3",
    classifiers=[
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    ]
)
