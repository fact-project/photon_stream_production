#! /usr/bin/env python
"""
Syncronize the local phs/obs/runstatus.csv with the latest runinfo database
from La Palma.
Export the FACT password: export FACT_PASSWORD=*********

Usage: phs.isdc.obs.synclapalma [options]

Options:
    -h | --help
"""
import docopt
import photon_stream_production as psp
import os


def main():
    try:
        docopt.docopt(__doc__)
        psp.tools.jsonlog('Start')
        psp.runstatus.update_to_latest(
            obs_dir=os.path.join(
                '/gpfs0',
                'fact',
                'processing',
                'public',
                'phs',
                'obs'
            ),
            lock_timeout=23*60*60
        )
        psp.tools.jsonlog('End')
    except docopt.DocoptExit as e:
        psp.tools.jsonlog(str(e))

if __name__ == '__main__':
    main()
