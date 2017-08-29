from .Event import Event
from .io.JsonLinesReader import JsonLinesReader
import pandas as pd


class EventListReader:
    """
    An EventListReader() reads Events() from a file.
    The Events are sequentially loaded from the file as needed.
    """
    def __init__(self, path):
        """
        Load FACT observations from a file.

        Parameters
        ----------
        path        The path to the observation file.
        """
        self.reader = JsonLinesReader(path)

    def __iter__(self):
        return self

    def __next__(self):
        return Event.from_event_dict(next(self.reader))

    def __repr__(self):
        out = 'EventListReader('
        out += "path '" + self.reader.path + "'"
        out += ')\n'
        return out

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.reader.close()

    @staticmethod
    def inspect(path):
        """
        Returns a pandas DataFrame() containing a summarized statistics of this
        run.
        """
        reader = EventListReader(path)
        inspection = pd.DataFrame([{
            'number_of_saturated_pixels': len(event.photon_stream.saturated_pixels),
            'total_number_of_photons': event.photon_stream.number_photons,
            'zd': event.zd,
            'az': event.az,
        } for event in reader])
        """
        'trigger_type': event.trigger_type,
        'time': event.time,
        'id': event.id,
        """
        return inspection
