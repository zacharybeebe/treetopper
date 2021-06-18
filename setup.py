import setuptools

keywords = ['forestry', 'natural resources', 'natural', 'resources',
            'forest', 'environmental', 'environmental science', 'science',
            'timber', 'tree', 'trees', 'west', 'coast', 'west coast', 'logging',
            'cruising', 'scaling', 'inventory', 'forests', 'board feet', 'cubic feet',
            'DBH', 'diameter at breast height', 'DIB', 'diameter inside bark', 'RD',
            'relative density', 'HDR', 'height to diamater ratio', 'species', 'VBAR',
            'volume to basal area ratio', 'BA', 'basal area', 'TPA', 'trees per acre',
            'scribner', 'timber marketing', 'forest marketing', 'timber management',
            'forest management']

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'treetopper',
    version = "1.0",
    author = 'Zach Beebe',
    author_email = 'z.beebe@yahoo.com',
    description = 'Python module for timber inventory for tree species of the west coast',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/zacharybeebe/timberscale',
    license = 'MIT',
    packages = setuptools.find_packages(),
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"],
    keywords = keywords,
    python_requires = '>=3.6',
    py_modules = ['timberscale']
)
