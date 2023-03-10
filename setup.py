import os
from distutils.command.build import build

from django.core import management
from setuptools import setup, find_packages


try:
    with open(
        os.path.join(os.path.dirname(__file__), "README.rst"), encoding="utf-8"
    ) as f:
        long_description = f.read()
except:
    long_description = ""


class CustomBuild(build):
    def run(self):
        management.call_command("compilemessages", verbosity=1, interactive=False)
        build.run(self)


cmdclass = {"build": CustomBuild}


setup(
    name="byro-groups",
    version="0.0.1",
    description="Plugin adds user groups to byro.",
    long_description=long_description,
    url="https://github.com/houndlord/byro-groups",
    author="Lev E. Chechulin",
    author_email="l.e.chechulin@gmail.com",
    license="Apache Software License",
    install_requires=[],
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[byro.plugin]
byro_groups=byro_groups:ByroPluginMeta
""",
)
