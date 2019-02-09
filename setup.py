import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='knu_parser',
    version='0.0.2',
    packages=setuptools.find_packages(),
    url='https://github.com/vlade11115/knu-parser',
    license='CC0 1.0 Universal',
    author='vlade11115',
    author_email='vlade11115@gmail.com',
    description='Simple scraper for new KNU site timetable.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    install_requires=[
        'scrapy',
    ],
)
