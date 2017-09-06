import numpy as np
import photon_stream as ps
import tempfile
import os
from os.path import join
from os.path import exists
import pkg_resources
import glob
import pytest
import fact
import pandas as pd


old_runstatus_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('tests','resources','runstatus_20161115_to_20161231.csv')
)

new_runstatus_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('tests','resources','runstatus_20161115_to_20170103.csv')
)

runinfo_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('tests','resources','runinfo_20161115_to_20170103.csv')
)

qstat_xml_path = pkg_resources.resource_filename(
    'photon_stream', 
    os.path.join('tests','resources','qstat.xml')
)
with open(qstat_xml_path, 'rt') as fin:
    qstat_xml = fin.read()
    runqstat = ps.production.isdc.qstat.qstat(xml=qstat_xml)


def run_production_scenario(out_dir):
    fact_dir = join(out_dir, 'fact')
    ri = ps.production.runinfo.read(runinfo_path)
    ps.production.tools.create_fake_fact_dir(fact_dir, ri)


    rs1 = ps.production.runstatus.read(old_runstatus_path)
    my_fact_tools_jar_path = join(out_dir, 'my_fact_tools.jar')
    with open(my_fact_tools_jar_path, 'w') as fftools:
        fftools.write('Hi, I am a fact tools dummy java jar!')

    my_fact_tools_xml_path = join(out_dir, 'observations_passX.xml')
    with open(my_fact_tools_xml_path, 'w') as fxml:
        fxml.write('Hi, I am a fact tools xml steering dummy!')

    phs_dir = join(out_dir, 'phs')
    obs_dir = join(phs_dir, 'obs')


    ps.production.runstatus.init(
        obs_dir=obs_dir, 
        latest_runstatus=rs1
    )
    assert os.path.exists(phs_dir)
    assert os.path.exists(join(phs_dir,'obs'))
    assert os.path.exists(join(phs_dir,'obs','runstatus.csv'))
    assert os.path.exists(join(phs_dir,'obs','.lock.runstatus.csv'))


    # FIRST CHUNK
    ps.production.isdc.produce(
        phs_dir=phs_dir, 
        only_a_fraction=1.0,
        fact_raw_dir=join(fact_dir, 'raw'),
        fact_drs_dir=join(fact_dir, 'raw'),
        fact_aux_dir=join(fact_dir, 'aux'),
        java_path='/usr/java/jdk1.8.0_77/bin',
        fact_tools_jar_path=my_fact_tools_jar_path,
        fact_tools_xml_path=my_fact_tools_xml_path,
        tmp_dir_base_name='fact_photon_stream_JOB_ID_',
        queue='test_dummy',
        runqstat_dummy=runqstat,
        max_jobs_in_qsub=1000,
    )

    assert os.path.exists(join(phs_dir,'obs.std'))
    ps.production.runstatus.update_phs_status(obs_dir=obs_dir)

    runs_1st_chunk = runs_in_obs_dir(obs_dir)
    assert len(runs_1st_chunk) < 1000
    assert len(runs_1st_chunk) > 1000 - 100
    assert np.all(runs_1st_chunk.fNight < 20170101)
    assert np.all(runs_1st_chunk.fNight > 20161223)


    # SECOND CHUNK
    ps.production.isdc.produce(
        phs_dir=phs_dir, 
        only_a_fraction=1.0,
        fact_raw_dir=join(fact_dir, 'raw'),
        fact_drs_dir=join(fact_dir, 'raw'),
        fact_aux_dir=join(fact_dir, 'aux'),
        java_path='/usr/java/jdk1.8.0_77/bin',
        fact_tools_jar_path=my_fact_tools_jar_path,
        fact_tools_xml_path=my_fact_tools_xml_path,
        tmp_dir_base_name='fact_photon_stream_JOB_ID_',
        queue='test_dummy', 
        runqstat_dummy=runqstat,
        max_jobs_in_qsub=1000,
    )

    runs_2nd_chunk = runs_in_obs_dir(obs_dir)
    assert len(runs_2nd_chunk) < 2000
    assert len(runs_2nd_chunk) > 1000
    assert np.all(runs_2nd_chunk.fNight < 20170101)
    assert np.all(runs_2nd_chunk.fNight > 20161115)


    # THIRD CHUNK
    rs2 = ps.production.runstatus.read(new_runstatus_path)
    ps.production.isdc.produce(
        phs_dir=phs_dir,
        only_a_fraction=1.0,
        fact_raw_dir=join(fact_dir, 'raw'),
        fact_drs_dir=join(fact_dir, 'raw'),
        fact_aux_dir=join(fact_dir, 'aux'),
        java_path='/usr/java/jdk1.8.0_77/bin',
        fact_tools_jar_path=my_fact_tools_jar_path,
        fact_tools_xml_path=my_fact_tools_xml_path,
        tmp_dir_base_name='fact_photon_stream_JOB_ID_',
        queue='test_dummy', 
        runqstat_dummy=runqstat,
        latest_runstatus=rs2,
        max_jobs_in_qsub=100,
    )

    ps.production.runstatus.update_phs_status(obs_dir=join(phs_dir,'obs'))
    runs_3rd_chunk = runs_in_obs_dir(obs_dir)
    assert len(runs_3rd_chunk) < 2000
    assert len(runs_3rd_chunk) > 1000
    assert np.all(runs_3rd_chunk.fNight < 20170103)
    assert np.all(runs_3rd_chunk.fNight > 20161115)



def test_production_scenario(out_dir):
    if out_dir is None:
        with tempfile.TemporaryDirectory(prefix='phs_') as tmp:
            run_production_scenario(out_dir=tmp)
    else:
        os.makedirs(out_dir, exist_ok=True)
        run_production_scenario(out_dir=out_dir)


def runs_in_obs_dir(obs_dir):
    runs_produced_paths = glob.glob(join(obs_dir,'*','*','*','*phs.jsonl.gz'))
    runs_produced = []
    for run_produced_path in runs_produced_paths:
        r = fact.path.parse(run_produced_path)
        runs_produced.append({'fNight': r['night'], 'fRunID': r['run']})

    runids = pd.DataFrame(runs_produced)
    runids.sort_values(by=ps.production.runinfo.ID_RUNINFO_KEYS , inplace=True)
    return runids