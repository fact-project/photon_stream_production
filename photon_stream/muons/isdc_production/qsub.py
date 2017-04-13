import os
from os.path import join
from os.path import split
from os.path import exists
from tqdm import tqdm
import subprocess as sp
from .write_worker_node_script import write_worker_node_script

def qsub(
    input_phs_dir,
    out_muon_dir,
    queue='fact_medium', 
    email='sebmuell@phys.ethz.ch'):
    """
    Run the Muon extraction on all photon-stream runs in the 'phs' directory.
    """
    input_phs_dir = os.path.abspath(input_phs_dir)
    out_muon_dir = os.path.abspath(out_muon_dir)
    os.makedirs(out_muon_dir, exist_ok=True)

    print('Start extracting muons...')


    run_paths = glob.glob(join(input_phs_dir,'2014/01/01/*.phs.jsonl.gz'))
    

    print('Found', len(run_paths), 'potential runs.')
    print('Set up output paths for the potential runs...')


    potential_jobs = []
    for run_path in tqdm.tqdm(run_paths):

        run_path = os.path.abspath(run_path)
        year = split(split(split(split(run_path)[0])[0])[0])[1]
        month = split(split(split(run_path)[0])[0])[1]
        night = split(split(run_path)[0])[1]
        base = split(run_path)[1].split('.')[0]

        output_dir = join()
        job = {
            'input_run_path': run_path,
            'year': year,
            'month': month,
            'night': night,
            'base': base,
            'output_muon_path': join(out_muon_dir, 'muons', year, month, night, base)}
        potential_jobs.append(job)


    print('Set up paths for', len(job), 'potential runs.')
    print('Sort out all potential runs which were already processed...')

    jobs = []
    # check if output already exists
    for job in tqdm.tqdm(potential_jobs):
        if exists(job['output_run_path']) and exists(job['output_run_header_path']):
            pass
        else:
            jobs.append(job)


    print('There are', len(jobs), 'runs left to be processed.')
    print('Submitt into qsub...')

    for job in tqdm.tqdm(jobs):

        job['job_path'] = join(
            out_muon_dir, 
            'job', 
            job['year'], 
            job['month'], 
            job['night'], 
            job['base']+'.sh')

        job['stdout_path'] = join(
            out_muon_dir, 
            'std', 
            job['year'], 
            job['month'], 
            job['night'], 
            job['base']+'.o')

        job['stderr_path'] = join(
            out_muon_dir, 
            'std', 
            job['year'], 
            job['month'], 
            job['night'], 
            job['base']+'.e')

        job_dir = os.path.split(job['job_path'])[0]
        os.makedirs(job_dir, exist_ok=True)

        std_dir = os.path.split(job['stdout_path'])[0]
        os.makedirs(std_dir, exist_ok=True)

        output_muon_dir = os.path.split(job['output_muon_path'])[0]
        os.makedirs(output_muon_dir, exist_ok=True)

        write_worker_node_script(
            path=job['job_path'],
            input_run_path=job['input_run_path'],
            output_muon_path=job['output_muon_path'])

        cmd = [ 'qsub',
                '-q', queue,
                '-o', job['stdout_path'],
                '-e', job['stderr_path'],
                '-m', 'ae', # send email in case of (e)nd or (a)bort
                '-M', email,
                job['job_path']]
   
        #qsub_return_code = sp.call(cmd)