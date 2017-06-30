import numpy as np
import photon_stream as ps

event_dict_A = {
    'Run': 1337,
    'Event': 42,
    'Reuse': 13,
    'Particle': 402,
    'Energy_GeV': 1337.42,
    'Phi_deg': 270.3,
    'Theta_deg': 5.6,
    'ImpactX_m': 10.43,
    'ImpactY_m': 23.55,
    'FirstInteractionAltitude_m': 25697.64
}

event_dict_B = {
    'Run': 1447,
    'Event': 41,
    'Reuse': 0,
    'Particle': 5624,
    'Energy_GeV': 2000.0,
    'Phi_deg': 88.5,
    'Theta_deg': 6.6,
    'ImpactX_m': 100.5,
    'ImpactY_m': 0.34,
    'FirstInteractionAltitude_m': 42333.78
}

def test_constructor():
    a = np.abs
    sim_truth_A = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_A)
    assert sim_truth_A.run == 1337
    assert sim_truth_A.event == 42
    assert sim_truth_A.reuse == 13
    assert a(sim_truth_A.energy - 1337.42) < 1e-4
    assert a(sim_truth_A.phi - 270.3) < 1e-4
    assert a(sim_truth_A.theta - 5.6) < 1e-4
    assert a(sim_truth_A.impact_x - 10.43) < 1e-4
    assert a(sim_truth_A.impact_y - 23.55) < 1e-4
    assert a(sim_truth_A.first_interaction_altitude - 25697.64) < 1e-3


def test_equal():
    sim_truth_1A = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_A)
    sim_truth_1B = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_B)
    
    sim_truth_2A = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_A)
    sim_truth_2B = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_B)

    assert sim_truth_1A == sim_truth_1A
    assert sim_truth_1A != sim_truth_1B
    assert sim_truth_1A == sim_truth_2A

def test_repr():
    sim_truth = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_A)
    print(sim_truth.__repr__())

def test_to_dict():
    sim_truth_A = ps.simulation_truth.SimulationTruth.from_event_dict(event_dict_A)

    dict_back = {'Test': True}
    dict_back = sim_truth_A.add_to_dict(dict_back)

    for key in event_dict_A:
        assert key in dict_back
        assert np.abs(dict_back[key] - event_dict_A[key]) < 1e-3