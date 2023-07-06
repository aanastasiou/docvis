import sys

from setuptools import setup, find_packages

setup(
    name="docvis",
    version="0.0.1",
    description="Composable standalone documents",
    long_description=open("README.rst").read(),
    author="Athanasios Anastasiou",
    author_email="athanastasiou@gmail.com",
    zip_safe=True,
    url="",
    license="",
    packages=find_packages(exclude=("test", "test.*")),
    keywords="",
    setup_requires=["pytest-runner"] if any(x in ("pytest", "test") for x in sys.argv) else [],
    tests_require=["pytest",],
    install_requires=["bokeh", "markdown", "bokeh", "lark", "click"],
    classifiers=[])
