import numpy as np
import photon_stream as ps
import photon_stream_production as psp
import pkg_resources
import os

runinfo_path = pkg_resources.resource_filename(
    'photon_stream_production',
    os.path.join('tests', 'resources', 'runinfo_20161115_to_20170103.csv')
)

drs_fRunID_for_obs_run = psp.drs_run._drs_fRunID_for_obs_run


def test_drs_run_assignment():

    ri = psp.runinfo.read(runinfo_path)
    ro = psp.drs_run.assign_drs_runs(ri)

    ri = ri[(ri.fNight > 20161229) & (ri.fNight <= 20170102)]
    ro = ro[(ro.fNight > 20161229) & (ro.fNight <= 20170102)]

    for i, row in ri.iterrows():
        assert row.fNight == ro.loc[i, 'fNight']
        assert row.fRunID == ro.loc[i, 'fRunID']

        if row.fRunTypeKey == psp.runinfo.OBSERVATION_RUN_TYPE_KEY:

            first_method_drs_run_id = drs_fRunID_for_obs_run(
                runinfo=ri,
                fNight=row.fNight,
                fRunID=row.fRunID
            )
            second_method_drs_run_id = ro.loc[i, 'DrsRunID']

            if np.isnan(first_method_drs_run_id):
                assert np.isnan(second_method_drs_run_id)
            else:
                assert first_method_drs_run_id == second_method_drs_run_id
