import os
import fact
from .runinfo import OBSERVATION_RUN_TYPE_KEY
from .runinfo import DRS_RUN_TYPE_KEY


def touch(path):
    with open(path, 'a') as out:
        os.utime(path)


def create_fake_fact_dir(path, runinfo):
    fact_raw = os.path.join(path, 'raw')
    for index, row in runinfo.iterrows():
        Night = runinfo['fNight'][index]
        Run = runinfo['fRunID'][index]
        run_type = runinfo['fRunTypeKey'][index]

        if run_type == DRS_RUN_TYPE_KEY:
            drs_path = fact.path.tree_path(Night, Run, prefix=fact_raw, suffix='.drs.fits.gz')
            os.makedirs(os.path.dirname(drs_path), exist_ok=True, mode=0o755)
            with open(drs_path, 'w') as drs_file:
                drs_file.write('I am a fake FACT drs file.')

        if run_type == OBSERVATION_RUN_TYPE_KEY:
            run_path = fact.path.tree_path(Night, Run, prefix=fact_raw, suffix='.fits.fz')
            os.makedirs(os.path.dirname(run_path), exist_ok=True, mode=0o755)
            with open(run_path, 'w') as raw_file:
                raw_file.write('I am a fake FACT raw observation file.')