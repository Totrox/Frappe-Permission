from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in permission/__init__.py
from permission import __version__ as version

setup(
	name="permission",
	version=version,
	description="Special Permission for Frappe",
	author="Totrox Technology Totrox Technology",
	author_email="info@totrox.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
