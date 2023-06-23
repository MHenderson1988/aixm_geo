import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AIXMGeo",
    version="0.0.2",
    author="Mark Henderson",
    author_email="mark.henderson1988@gmail.com",
    description="A Python module which wraps KMLPlus to produce kml files from AIXM 5.1 geographical data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MHenderson1988/aixm_geo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
