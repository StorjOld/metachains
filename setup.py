from distutils.core import setup

setup(
    name='metachains_dtc',
    version='0.1.5',
    author='Hugo Peixoto',
    author_email='hugo.peixoto@gmail.com',
    packages=['metachains_dtc'],
    scripts=[],
    url='https://github.com/Storj/metachains_dtc',
    license='LICENSE',
    description='Tool for accessing and dumping metadata into the Datacoin blockchain',
    long_description=open('README.md').read(),
    install_requires=[
        'requests >= 0.11.0',
    ],
)
