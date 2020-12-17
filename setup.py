# py2app setup file

from setuptools import setup

APP = ['BrainPainter.py']
DATA_FILES = []
OPTIONS = {
	'argv_emulation': True,
	'packages': ['tkinter', 'docker','subprocess'],
	'iconfile': 'app.icns',
}

setup(
	app=APP,
	data_files=DATA_FILES,
	options={'py2app': OPTIONS},
	setup_requires=['py2app'],
)
