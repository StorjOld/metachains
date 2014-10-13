from setuptools import setup, find_packages

setup(
    name='metachains_dtc',
    version='0.3.0',
    author='Hugo Peixoto',
    author_email='hugo.peixoto@gmail.com',
    packages=find_packages(),
    scripts=[],
    url='https://github.com/Storj/metachains_dtc',
    license='LICENSE',
    description='Tool for accessing and dumping metadata into the Florincoin blockchain',
    long_description=open('README.md').read(),
    install_requires=[
        'requests >= 0.11.0',
    ],
)
