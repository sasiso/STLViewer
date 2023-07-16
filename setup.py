from setuptools import setup
import py2exe

import PyQt5.QtCore
from PyQt5.QtCore import QCoreApplication, QLibraryInfo

script_name = 'main.py'

# Retrieve the path to the 'plugins' directory
plugins_dir = QLibraryInfo.location(QLibraryInfo.PluginsPath)

setup(
    options={
        'py2exe': {
            'bundle_files': 1,
            'compressed': True,
            'optimize': 2,
            'packages': ['PyQt5'],
        }
    },
    windows=[{'script': script_name}],
    # Use the retrieved 'plugins' directory to locate the required plugins
    data_files=[('platforms', [f'{plugins_dir}/platforms/qwindows.dll'])],
    zipfile=None,
    # Add all your top-level modules here
    py_modules=[
        'annotation_interactor',
        'custom_pdf',
        'drawing_interactor',
        'main',
        'main_window',
        'measurement_interactor',
    ],
)
