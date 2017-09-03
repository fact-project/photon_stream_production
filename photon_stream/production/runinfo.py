import os
from fact import credentials
import pandas as pd
import numpy as np
import warnings
import shutil


OBSERVATION_RUN_TYPE_KEY = 1
DRS_RUN_TYPE_KEY = 2

DRS_STEP_KEY = 2

ID_RUNINFO_KEYS = [
    'fNight',
    'fRunID',
]

TRIGGER_NUMBER_RUNINFO_KEYS = [
    'fNumExt1Trigger',
    'fNumExt2Trigger',
    'fNumPhysicsTrigger',
    'fNumPedestalTrigger',
]

PHS_KEYS = [
    'NumExpectedPhsEvents',
    'NumActualPhsEvents',
    'StdOutSize',
    'StdErrorSize',
    'IsOk',
]

RUNINFO_KEYS = (
    ID_RUNINFO_KEYS +
    ['fRunTypeKey'] +
    ['fDrsStep'] +
    TRIGGER_NUMBER_RUNINFO_KEYS
)

RUNSTATUS_KEYS = (
    ID_RUNINFO_KEYS +
    ['DrsRunID'] +
    PHS_KEYS
)


def read(path='runstatus.csv'):
    return pd.read_csv(path)


def write(runinfo, path='runstatus.csv'):
    runinfo.to_csv(path+'.part', index=False, na_rep='nan')
    shutil.move(path+'.part', path)


def latest_runinfo():
    factdb = credentials.create_factdb_engine()
    return pd.read_sql_table(
        table_name="RunInfo",
        con=factdb,
        columns=RUNINFO_KEYS
    )


def latest_runstatus():
    """
    Returns only a part of the FACT runinfo database relevant for the 
    photon-stream.
    """
    ri = latest_runinfo()
    ri = assign_drs_runs(ri)
    ri = drop_not_obs_runs(ri)
    ri = add_expected_phs_event_column(ri)
    ri = add_empty_runstatus_columns(ri)
    return drop_not_matching_keys(ri, RUNSTATUS_KEYS)


def drop_not_matching_keys(runinfo, desired_keys):
    riout = runinfo.copy()
    for key in riout.keys():
        if key not in desired_keys:
            riout.drop(key, axis=1, inplace=True)
    return riout


def drop_not_obs_runs(runinfo):
    return runinfo[
        runinfo.fRunTypeKey==OBSERVATION_RUN_TYPE_KEY
    ].copy()


def add_expected_phs_event_column(runinfo):
    riout = runinfo.copy()
    riout['NumExpectedPhsEvents'] = pd.Series(
        number_expected_phs_events(riout), 
        index=riout.index
    )
    return riout


def add_empty_runstatus_columns(runinfo):
    riout = runinfo.copy()
    for phs_key in RUNSTATUS_KEYS:
        if phs_key not in riout:
            riout[phs_key] = pd.Series(np.nan, index=riout.index)
    return riout


def append_new_runstatus(old_runstatus, new_runstatus):
    rsi1 = old_runstatus.set_index(ID_RUNINFO_KEYS)
    rsi2 = new_runstatus.set_index(ID_RUNINFO_KEYS)
    rsi2.loc[rsi1.index] = rsi1
    return rsi2.reset_index()


def number_expected_phs_events(runinfo):
    count = np.zeros(runinfo.shape[0])
    for key in TRIGGER_NUMBER_RUNINFO_KEYS:
        count += runinfo[key]
    count[runinfo['fRunTypeKey'] != OBSERVATION_RUN_TYPE_KEY] = np.nan
    return count


def remove_from_first_when_also_in_second(first, second):
    m = pd.merge(
        first,
        second, 
        how='outer', 
        indicator=True,
        on=ID_RUNINFO_KEYS,
    )
    result = m[m['_merge'] == 'left_only'].copy()
    result.drop('_merge', axis=1, inplace=True)
    return result


def _drs_fRunID_for_obs_run(runinfo, fNight, fRunID):
    warnings.warn(
        'This drs run locater function was replaced with "assign_drs_runs()"'
        'This function is still kept for unit testing the new one.', 
        DeprecationWarning
    )

    ri = runinfo
    drs_candidates = ri[
        (ri.fNight == fNight)&
        (ri.fDrsStep == DRS_STEP_KEY)&
        (ri.fRunTypeKey == DRS_RUN_TYPE_KEY)&
        (ri.fRunID < fRunID)
    ]
    if len(drs_candidates) >= 1:
        return drs_candidates.iloc[-1].fRunID
    else:
        return np.nan


def assign_drs_runs(runinfo):
    ri = runinfo.copy()
    ri.sort_values(inplace=True, ascending=True, by=ID_RUNINFO_KEYS)

    ri.insert(loc=2, column='DrsRunID', value=pd.Series(np.nan, index=ri.index))
    raw = ri.as_matrix()
    k = {}
    for c, key in enumerate(ri.keys()):
        k[key] = c
    current_drs_fRunID = np.nan
    current_drs_fNight = np.nan
    for i in range(raw.shape[0]):
        if (
            raw[i,k['fRunTypeKey']]==DRS_RUN_TYPE_KEY and 
            raw[i,k['fDrsStep']]==DRS_STEP_KEY
        ):
            current_drs_fRunID = raw[i,k['fRunID']]
            current_drs_fNight = raw[i,k['fNight']]
        else:
            if current_drs_fNight == raw[i,k['fNight']]:
                raw[i,k['DrsRunID']] = current_drs_fRunID
    ri = pd.DataFrame(raw, columns=ri.keys().tolist())
    return ri