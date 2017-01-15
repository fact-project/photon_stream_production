from distutils.core import setup

setup(
    name='photon_stream',
    version='0.0.0',
    description='Read, write, manipulate and plot a Photon Stream',
    url='https://github.com/fact-project/',
    author='Sebastian Achim Mueller',
    author_email='sebmuell@phys.ethz.ch',
    license='MIT',
    packages=[
        'photon_stream',
        'photon_stream.fact',
        'photon_stream.experimental'
    ],
    package_data={'photon_stream': ['tests/resources/*']},
    install_requires=[
        'docopt',
        'scipy',
        'sklearn',
        'matplotlib',
    ],
    zip_safe=False,
)
