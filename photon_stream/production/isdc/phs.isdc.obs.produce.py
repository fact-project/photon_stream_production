#! /usr/bin/env python
"""
Converting FACT raw observation runs into photon-stream runs. You need to export
the universal FACT password: export FACT_PASSWORD=*********

Usage: phs.production.isdc.automatic [options]

Options:
    -h | --help
"""
import docopt
from tqdm import tqdm
import os
from os.path import join
import numpy as np
import pkg_resources

from .. import prepare
from .. import runstatus as rs
from .. import runinfo as ri
from .qsub import qsub


worker_node_main_path = os.path.abspath(
    pkg_resources.resource_filename(
        'photon_stream', 
        os.path.join('production','isdc','worker_node_main.py')
    )
)


def automatic(
    init=False,
    start_night=0,
    end_night=99999999,
    only_a_fraction=1.0,
    fact_raw_dir='/fact/raw',
    fact_drs_dir='/fact/raw',
    fact_aux_dir='/fact/aux',
    phs_dir='/gpfs0/fact/processing/public/phs',
    java_path='/home/guest/relleums/java8/jdk1.8.0_111',
    fact_tools_jar_path='/home/guest/relleums/fact_photon_stream/fact-tools/target/fact-tools-0.18.1.jar',
    fact_tools_xml_path='/home/guest/relleums/fact_photon_stream/photon_stream/photon_stream/production/resources/observations_pass4.xml',
    tmp_dir_base_name='phs_obs_',
    queue='fact_medium', 
    latest_runstatus=None,
    max_jobs_in_qsub=128,
    use_dummy_qsub=False,
    runqstat_dummy=None,
):  
    obs_dir = join(phs_dir,'obs')

    if init:
        rs.init(
            obs_dir=obs_dir, 
            latest_runstatus=latest_runstatus
        )

    rs.update_to_latest(
        obs_dir=obs_dir, 
        latest_runstatus=latest_runstatus
    )

    runstatus = rs.read(join(obs_dir, 'runstatus.csv'))

    was_not_checked_yet = np.isnan(runstatus['IsOk'].values)
    all_runjobs = runstatus[was_not_checked_yet]

    if runqstat_dummy is None:
        runqstat = ps.production.isdc.qstat.qstat(is_in_JB_name='phs_obs')
    else:
        runqstat = runqstat_dummy

    if len(runqstat) > max_jobs_in_qsub:
        print('Stop. Qsub is busy.')
        return

    runjobs = ri.remove_from_first_when_also_in_second(
        first=all_runjobs,
        second=runqstat,
    )

    todo = prepare.make_job_list(
        phs_dir=phs_dir,
        start_night=start_night,
        end_night=end_night,
        only_a_fraction=only_a_fraction,
        fact_raw_dir=fact_raw_dir,
        fact_drs_dir=fact_drs_dir,
        fact_aux_dir=fact_aux_dir,
        java_path=java_path,
        fact_tools_jar_path=fact_tools_jar_path,
        fact_tools_xml_path=fact_tools_xml_path,
        tmp_dir_base_name=tmp_dir_base_name,
        runinfo=runjobs,
    )
    prepare.prepare_output_tree(todo['tree'])

    for job in tqdm(todo['jobs']):
        qsub(
            job=job, 
            exe_path=worker_node_main_path, 
            dummy=use_dummy_qsub
        )


def main():
    try:
        arguments = docopt.docopt(__doc__)
        automatic()
    except docopt.DocoptExit as e:
        print(e)

if __name__ == '__main__':
    main()