from setuptools import setup, find_packages

setup(
    name="zoocore_maya",
    version="0.1.0",
    description="Core Python Library for Zootools Maya",
    author="David Sparrow",
    author_email="dsparrow27@gmail.com",
    url="https://github.com/dsparrow27/zoocore_maya",
    license="GNU",
    packages=find_packages(),
    zip_safe=False,
    dependency_links=["https://github.com/dsparrow27/zoocore.git"]
)
