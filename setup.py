from distutils.core import setup

setup(
    name='photon_stream_production',
    version='0.0.1',
    description='Produce the photon_stream at ISDC at Geneva',
    url='https://github.com/fact-project/',
    author='Sebastian Achim Mueller',
    author_email='sebmuell@phys.ethz.ch',
    license='MIT',
    packages=[
        'photon_stream_production',
        'photon_stream_production.ethz',
        'photon_stream_production.isdc',
        'photon_stream_production.sim',
    ],
    package_data={
        'photon_stream_production': [
            'tests/resources/*',
            'resources/*',
        ]
    },
    install_requires=[
        'docopt',
        'scipy',
        'scikit-learn',
        'scikit-image',
        'matplotlib',
        'pyfact',
        'pandas',
        'tqdm',
        'ujson',
        'qstat',
        'filelock'
    ],
    entry_points={'console_scripts': [
        'phs.isdc.obs.synclapalma = ' +
        'photon_stream.production.isdc.synclapalma_main:main',
        'phs.isdc.obs.produce = ' +
        'photon_stream.production.isdc.produce_main:main',
        'phs.isdc.obs.produce.worker = ' +
        'photon_stream.production.isdc.worker_node_produce:main',
        'phs.isdc.obs.status = ' +
        'photon_stream.production.isdc.status_main:main',
        'phs.isdc.obs.status.worker = ' +
        'photon_stream.production.isdc.worker_node_status:main',
        'phs.sim.produce.worker = ' +
        'photon_stream.production.sim.worker_node_produce:main',
        'phs.isdc.backup.to.ethz = ' +
        'photon_stream.production.backup_main:main',
    ]},
    zip_safe=False,
)
