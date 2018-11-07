#! /usr/bin/env python
"""
Backup the photon-stream output to ETH Zurich.
Asserts, that only one instance is running.

Usage: phs.isdc.backup.to.ethz [options]

Options:
    -h | --help
"""
import docopt
from os.path import join
import os
from filelock import FileLock
from filelock import Timeout
import subprocess as sp
import datetime
import sys


def jsonlog(msg):
    print('{time:"' + datetime.datetime.now().isoformat() + '"' + ', msg:"' + msg + '"}')
    sys.stdout.flush()

def folder_wise_rsync_a(
    destination_path,
    source_path,
    source_host='',
    destination_host='',
):
    if destination_host:
        destination_host += ':'
    if source_host:
        source_host += ':'

    for dirname, subdirs, files in os.walk(source_path):
        rel_path = os.path.relpath(dirname, source_path)
        fr = rel_path+'/'
        to = destination_host + destination_path
        cmd = "rsync -lptgodD --relative " + fr + " " + to
        jsonlog(fr)
        sp.call(cmd, shell=True, cwd=source_path)


def backup():
    jsonlog('Start backup from ISDC-Geneva to ETH-Zurich')
    rsync_lock_path = join(
        '/',
        'home',
        'guest',
        'relleums',
        '.phs.isdc.backup.to.ethz.lock'
    )
    try:
        rsync_lock = FileLock(rsync_lock_path)
        with rsync_lock.acquire(timeout=3600):
            jsonlog('Aquiered lock for ' + rsync_lock_path)
            folder_wise_rsync_a(
                source_host='',
                source_path=join(
                    '/',
                    'gpfs0',
                    'fact',
                    'processing',
                    'public',
                    'phs/'
                ),
                destination_host='relleums@ihp-pc41.ethz.ch',
                destination_path=join('/', 'data', 'fact_public', 'phs/'),
            )
    except Timeout:
        jsonlog('Could not aquire lock for ' + rsync_lock_path)
    jsonlog('End backup from ISDC-Geneva to ETH-Zurich')


def main():
    try:
        docopt.docopt(__doc__)
        backup()
    except docopt.DocoptExit as e:
        jsonlog(str(e))

if __name__ == '__main__':
    main()
