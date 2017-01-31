import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from .PhotonStream import PhotonStream
from .plot import add_event_2_ax

class Event(object):
    def __init__(self):
        self.trigger_type = None
        self.photon_stream = None
        self.id = None
        self.run = None
        self._time_unix_s = None
        self._time_unix_us = None
        self.time = None
        self.saturated_pixels = None

    @classmethod
    def from_event_dict_and_run(cls, event_dict, run):
        event = cls()

        event.trigger_type = event_dict['Trigger']
        event.zd = event_dict['Zd_deg']
        event.az = event_dict['Az_deg']
        event.id = event_dict['Event']
        event._time_unix_s = event_dict['UnixTime_s_us'][0]
        event._time_unix_us = event_dict['UnixTime_s_us'][1]
        event.saturated_pixels = event_dict['SaturatedPixels']
        event.time = dt.datetime.utcfromtimestamp(
            event._time_unix_s + event._time_unix_us / 1e6)

        event.run = run

        event.photon_stream = PhotonStream.from_event_dict(event_dict)
        return event

    def plot(self, mask=None):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        add_event_2_ax(self, ax, mask=mask)
        plt.show()

    def __repr__(self):
        out = 'FactEvent('
        out += 'Id '+str(self.id)
        out += ')\n'
        return out