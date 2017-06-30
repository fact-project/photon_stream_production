import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from .PhotonStream import PhotonStream
from .ObservationInformation import ObservationInformation
from .SimulationTruth import SimulationTruth
from .plot import add_event_2_ax


MAX_RESIDUAL_POINTING_DEG = 1e-5


class Event(object):
    """
    A FACT event in photon-stream representation.

    Fields
    ------
    zd                  The telescope pointing zenith distance in deg.

    az                  The telescope pointing azimuth in deg.

    saturated_pixels    A list of pixels in CHID which have time line 
                        saturations out of the DRS4 chips.

    photon_stream       The photon-stream of all photons detected by all pixels
                        in this event.

    simulation_truth    [optional] 

    observation_info    [optional]
    """
    def __init__(self):
        pass

    @classmethod
    def from_event_dict(cls, event_dict):
        event = cls()
        event.zd = np.float32(event_dict['Zd_deg'])
        event.az = np.float32(event_dict['Az_deg'])
        event.photon_stream = PhotonStream.from_event_dict(event_dict)
        if 'UnixTime_s_us' in event_dict:
            event.observation_info = ObservationInformation.from_event_dict(
                event_dict
            )
        if 'Reuse' in event_dict:
            event.simulation_truth = SimulationTruth.from_event_dict(
                event_dict
            )
        return event


    def plot(self, mask=None):
        """
        Creates a new figure with 3D axes to show the photon-stream of the 
        event. Call plt.show() to see it. 
        """
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        add_event_2_ax(self, ax, mask=mask)


    def to_dict(self):
        evt = {}
        evt['Zd_deg'] = float(self.zd)
        evt['Az_deg'] = float(self.az)
        evt = self.photon_stream.add_to_dict(evt)
        if hasattr(self, 'observation_info'):
            evt = self.observation_info.add_to_dict(evt)
        if hasattr(self, 'simulation_truth'):
            evt = self.simulation_truth.add_to_dict(evt)
        return evt


    def _info(self):
        out = ''
        if hasattr(self, 'observation_info'):
            out += 'observation, ' + self.observation_info._info()
        if hasattr(self, 'simulation_truth'):
            out += 'simulation, ' + self.simulation_truth._info()
        return out        


    def __repr__(self):
        out = 'Event('
        out += self._info() + ', '
        out += 'photon-stream ' + self.photon_stream._info()
        out += ')\n'
        return out


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if not np.abs(self.zd - other.zd) < MAX_RESIDUAL_POINTING_DEG: return False
            if not np.abs(self.az - other.az) < MAX_RESIDUAL_POINTING_DEG: return False
            if not self.photon_stream == other.photon_stream: return False
            if hasattr(self, 'simulation_truth'):
                if not self.simulation_truth == other.simulation_truth: return False
            if hasattr(self, 'observation_info'):
                if not self.observation_info == other.observation_info: return False
            return True
        else:
            return NotImplemented