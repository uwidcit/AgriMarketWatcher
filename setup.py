import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md")) as f:
    README = f.read()
with open(os.path.join("{0}/docs".format(here), "CHANGES.md")) as f:
    CHANGES = f.read()

with open("requirements.txt") as f:
    requires = f.read().splitlines()

setup(
    name="agrimarketwatcher",
    version="0.4.0",
    long_description=README + "\n\n" + CHANGES,
    author="Kyle De Freitas",
    author_email="kyle.e.defreitas@gmail.com",
    url="https://github.com/uwidcit/AgriMarketWatcher",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    maintainer="Kyle De Freitas",
    maintainer_email="kyle.e.defreitas@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
