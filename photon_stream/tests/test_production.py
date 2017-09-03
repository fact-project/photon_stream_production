import numpy as np
import photon_stream as ps
import tempfile
import os
from os.path import join
from os.path import exists
import pkg_resources
import glob


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


def test_production_run_collection():
    #with tempfile.TemporaryDirectory(prefix='photon_stream_run_collection') as tmp:
    with open('/dev/null', 'rb') as lalala:
        tmp = '/home/sebastian/Desktop/phs_production'
        os.makedirs(tmp, exist_ok=True)
        fact_dir = join(tmp, 'fact')

        ri = ps.production.runinfo.read(runinfo_path)
        ps.production.runinfo.create_fake_fact_dir(fact_dir, ri)

        rs1 = ps.production.runinfo.read(old_runstatus_path)
        my_fact_tools_jar_path = join(tmp, 'my_fact_tools.jar')
        with open(my_fact_tools_jar_path, 'w') as fftools:
            fftools.write('Hi, I am a fact tools dummy java jar!')

        my_fact_tools_xml_path = join(tmp, 'observations_passX.xml')
        with open(my_fact_tools_xml_path, 'w') as fxml:
            fxml.write('Hi, I am a fact tools xml steering dummy!')

        phs_dir = join(tmp, 'phs')

        # FIRST CHUNK
        ps.production.isdc.qsub(
            phs_dir=phs_dir, 
            only_a_fraction=1.0,
            fact_raw_dir=join(fact_dir, 'raw'),
            fact_drs_dir=join(fact_dir, 'raw'),
            fact_aux_dir=join(fact_dir, 'aux'),
            java_path='/usr/java/jdk1.8.0_77/bin',
            fact_tools_jar_path=my_fact_tools_jar_path,
            fact_tools_xml_path=my_fact_tools_xml_path,
            tmp_dir_base_name='fact_photon_stream_JOB_ID_',
            queue='fact_medium', 
            use_dummy_qsub=True,
            runqstat_dummy=runqstat,
            latest_runstatus=rs1,
            start_new=True,
        )

        assert os.path.exists(phs_dir)
        assert os.path.exists(join(phs_dir,'obs'))
        assert os.path.exists(join(phs_dir,'obs','runstatus.csv'))
        assert os.path.exists(join(phs_dir,'obs','.lock.runstatus.csv'))
        assert os.path.exists(join(phs_dir,'obs.std'))


        #input('Take a look into '+tmp+' or press any key to continue')

        rs2 = ps.production.runinfo.read(new_runstatus_path)
        my_2nd_fact_tools_jar_path = join(tmp, 'my_2nd_fact_tools.jar')
        with open(my_2nd_fact_tools_jar_path, 'w') as fftools:
            fftools.write('Hi, I am another fact tools dummy java jar!')    

        # SECOND CHUNK with 2nd fact-tools.jar
        ps.production.isdc.qsub(
            phs_dir=phs_dir,
            only_a_fraction=1.0,
            fact_raw_dir=join(fact_dir, 'raw'),
            fact_drs_dir=join(fact_dir, 'raw'),
            fact_aux_dir=join(fact_dir, 'aux'),
            java_path='/usr/java/jdk1.8.0_77/bin',
            fact_tools_jar_path=my_2nd_fact_tools_jar_path,
            fact_tools_xml_path=my_fact_tools_xml_path,
            tmp_dir_base_name='fact_photon_stream_JOB_ID_',
            queue='fact_medium', 
            use_dummy_qsub=True,
            runqstat_dummy=runqstat,
            latest_runstatus=rs2,
            start_new=False,
        )

        #input('Take a look into '+tmp+' or press any key to continue')


def test_status_bar_string():
    progress_bar_str = ps.production.status.progress(ratio=0.0, length=50)
    assert len(progress_bar_str) < 50

    progress_bar_str = ps.production.status.progress(ratio=1.0, length=50)
    assert len(progress_bar_str) > 50    
    assert len(progress_bar_str) < 60    

    progress_bar_str = ps.production.status.progress(ratio=10.0, length=50)
    assert len(progress_bar_str) > 50    
    assert len(progress_bar_str) < 61  

    progress_bar_str = ps.production.status.progress(ratio=100.0, length=50)
    assert len(progress_bar_str) > 50    
    assert len(progress_bar_str) < 62 