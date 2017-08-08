import numpy as np
from ..PhotonStream import PhotonStream
from ..Event import Event
from ..ObservationInformation import ObservationInformation
from ..simulation_truth import SimulationTruth
from array import array
import datetime as dt
import os
import gzip

LINEBREAK = np.array([np.iinfo(np.uint8).max], dtype=np.uint8)
OBSERVATION_HEADER = {
    'pass': np.uint8(4),
    'type': 'observation',
    'future_problems_0': np.uint8(0),
    'future_problems_1': np.uint8(1),
}
SIMULATION_HEADER = {
    'pass': np.uint8(4),
    'type': 'simulation',
    'future_problems_0': np.uint8(0),
    'future_problems_1': np.uint8(1),
}

def append_header_to_file(header, fout):
    fout.write(np.uint8(header['pass']).tobytes())
    if header['type'] == 'observation':
        event_type = np.uint8(0)
    elif header['type'] == 'simulation':
        event_type = np.uint8(1)
    else:
        raise
    fout.write(event_type.tobytes())
    fout.write(np.uint8(header['future_problems_0']).tobytes())
    fout.write(np.uint8(header['future_problems_1']).tobytes())


def read_header_from_file(fin):
    raw_header = np.fromstring(fin.read(4), dtype=np.uint8, count=4)
    if raw_header[1] == 0:
        type_str = 'observation'
    elif raw_header[1] == 1:
        type_str = 'simulation'
    else:
        raise
    return {
        'pass': raw_header[0],
        'type': type_str,
        'future_problems_0': raw_header[2],
        'future_problems_1': raw_header[3]
    }


def append_simulation_id_to_file(simulation_truth, fout):
    fout.write(simulation_truth.run.tobytes())
    fout.write(simulation_truth.event.tobytes())
    fout.write(simulation_truth.reuse.tobytes())


def read_simulation_id_from_file(simulation_truth, fin):
    raw_id = np.fromstring(
        fin.read(12), 
        dtype=np.uint32, 
        count=3
    )
    simulation_truth.run = raw_id[0]
    simulation_truth.event = raw_id[1]
    simulation_truth.reuse = raw_id[2]


def append_observation_id_to_file(observation_info, fout):
    fout.write(observation_info.night.tobytes())
    fout.write(observation_info.run.tobytes())
    fout.write(observation_info.event.tobytes())


def read_observation_id_from_file(observation_info, fin):
    raw_id = np.fromstring(
        fin.read(12), 
        dtype=np.uint32, 
        count=3
    )
    observation_info.night = raw_id[0]
    observation_info.run = raw_id[1]
    observation_info.event = raw_id[2]


def append_observation_info_to_file(observation_info, fout):
    fout.write(observation_info._time_unix_s.tobytes())
    fout.write(observation_info._time_unix_us.tobytes())
    fout.write(observation_info.trigger_type.tobytes())


def read_observation_info_from_file(observation_info, fin):
    raw_info = np.fromstring(
        fin.read(12), 
        dtype=np.uint32, 
        count=3
    )
    observation_info.set_time_unix(
        time_unix_s=raw_info[0], 
        time_unix_us=raw_info[1],
    )
    observation_info.trigger_type = raw_info[2]


def append_pointing_to_file(event, fout):
    fout.write(event.zd.tobytes())
    fout.write(event.az.tobytes())


def read_pointing_from_file(event, fout):
    raw_pointing= np.fromstring(
        fout.read(8), 
        dtype=np.float32, 
        count=2
    )
    event.zd = raw_pointing[0]
    event.az = raw_pointing[1]


def append_photonstream_to_file(phs, fout):

    # WRITE SLICE DURATION
    fout.write(np.float32(phs.slice_duration).tobytes())

    # Write number of pixels plus number of photons
    number_of_pixels_and_photons = len(phs.time_lines) + phs.number_photons
    fout.write(np.uint32(number_of_pixels_and_photons).tobytes())

    # WRITE PHOTON ARRIVAL SLICES
    raw_time_lines = np.zeros(
        number_of_pixels_and_photons, 
        dtype=np.uint8)
    pos = 0
    for time_line in phs.time_lines:
        for photon_arrival in time_line:
            raw_time_lines[pos] = photon_arrival
            pos += 1
        raw_time_lines[pos] = LINEBREAK
        pos += 1
    fout.write(raw_time_lines.tobytes())


def read_photonstream_from_file(fin):
    phs = PhotonStream()

    # read slice duration
    phs.slice_duration = np.fromstring(
        fin.read(4),
        dtype=np.float32,
        count=1)[0]

    # read number of pixels and time lines
    number_of_pixels_and_photons = np.fromstring(
        fin.read(4),
        dtype=np.uint32,
        count=1)[0]

    # read photon-stream
    raw_time_lines = np.fromstring(
        fin.read(number_of_pixels_and_photons),
        dtype=np.uint8)

    phs.time_lines = []
    if len(raw_time_lines) > 0:
        phs.time_lines.append(array('B'))

    pixel = 0
    for i, symbol in enumerate(raw_time_lines):
        if symbol == LINEBREAK:
            pixel += 1
            if i+1 < len(raw_time_lines):
                phs.time_lines.append(array('B'))
        else:
            phs.time_lines[pixel].append(symbol)
    return phs


def append_saturated_pixels_to_file(saturated_pixels, fout):
    # WRITE NUMBER OF PIXELS
    number_of_pixels = len(saturated_pixels)
    fout.write(np.uint16(number_of_pixels).tobytes())

    saturated_pixels_raw = np.array(saturated_pixels, dtype=np.uint16)
    fout.write(saturated_pixels_raw.tobytes())


def read_saturated_pixels_from_file(fin):
    # READ NUMBER OF PIXELS
    number_of_pixels = np.fromstring(
        fin.read(2),
        dtype=np.uint16,
        count=1)[0]

    # READ saturated pixel CHIDs
    saturated_pixels_raw = np.fromstring(
        fin.read(number_of_pixels*2),
        dtype=np.uint16)
    return saturated_pixels_raw


def append_event_to_file(event, fout):
    if hasattr(event, 'observation_info'):
        append_header_to_file(OBSERVATION_HEADER, fout)
        append_observation_id_to_file(event.observation_info, fout)
        append_observation_info_to_file(event.observation_info, fout)
    elif hasattr(event, 'simulation_truth'):
        append_header_to_file(SIMULATION_HEADER, fout)
        append_simulation_id_to_file(event.simulation_truth, fout)
    else:
        raise
    append_pointing_to_file(event, fout)
    append_photonstream_to_file(event.photon_stream, fout)
    append_saturated_pixels_to_file(event.photon_stream.saturated_pixels, fout)


def read_event_from_file(fin):
    try:
        header = read_header_from_file(fin)
        event = Event()
        print(header['type'])
        if header['type'] == 'observation':
            obs = ObservationInformation()
            read_observation_id_from_file(obs, fin)
            read_observation_info_from_file(obs, fin)
            event.observation_info = obs
        elif header['type'] == 'simulation': 
            sim = SimulationTruth()
            read_simulation_id_from_file(sim, fin)
            event.simulation_truth = sim
        else:
            raise
        read_pointing_from_file(event, fin)
        event.photon_stream = read_photonstream_from_file(fin)  
        event.photon_stream.saturated_pixels = read_saturated_pixels_from_file(fin)
        return event
    except:
        raise StopIteration


class EventListReader(object):
    """
    Sequentially reads a gzipped binary run and provides events.
    """
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.file = gzip.open(path, "rb")

    def __exit__(self):
        self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        return read_event_from_file(self.file)

    def __repr__(self):
        out = 'BinaryEventListReader('
        out += self.path+')\n'
        return out