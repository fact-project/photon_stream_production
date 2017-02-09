# Binary Photon-Stream Format for FACT -- Pass4


### Event Header (32 Byte)
    
    uint32
    +--------+--------+--------+--------+
    |              Night Id             |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |               Run Id              |
    +--------+--------+--------+--------+
    
    uint32
    +--------+--------+--------+--------+
    |             Event Id              |
    +--------+--------+--------+--------+
    
    uint32
    +--------+--------+--------+--------+
    |          UNIX time [s]            |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |      UNIX time [us] mod. [s]      |
    +--------+--------+--------+--------+
    
    uint32
    +--------+--------+--------+--------+
    |            Trigger type           |
    +--------+--------+--------+--------+
    
    float32
    +--------+--------+--------+--------+
    |   Pointing Zenith Distance [Deg]  |
    +--------+--------+--------+--------+
    
    float32
    +--------+--------+--------+--------+
    |          Pointing Azimuth  [Deg]  |
    +--------+--------+--------+--------+
    
    
### Photon-Stream Header (8 Byte)
    
    float32
    +--------+--------+--------+--------+
    |         Slice time duration [s]   |
    +--------+--------+--------+--------+

    uint32
    +--------+--------+--------+--------+
    |   Number of pixels and photons    |
    +--------+--------+--------+--------+
    The size of the photon-stream in bytes.


### Photon-Stream (num. photons + num. pixel Byte)

         Photon arrival times in slices (EXAMPLE, shape and structure depent on the individual event)
         uint8 
         +--------+--------+--------+--------+
       0 |   XXX  |   XXX  |   XXX  |   256  |
         +--------+--------+--------+--------+   
       1 |   XXX  |   XXX  |   256  |
         +--------+--------+--------+ 
       2 |   XXX  |   256  |
         +--------+--------+--------+--------+--------+
       3 |   XXX  |   XXX  |   XXX  |   XXX  |   256  |
         +--------+--------+--------+--------+--------+--------+--------+ 
       4 |   XXX  |   XXX  |   XXX  |   XXX  |   XXX  |   XXX  |   256  |
         +--------+--------+--------+--------+--------+--------+--------+   
       5 |   XXX  |   256  |
         +--------+--------+
       6 |   256  |
         +--------+--------+--------+
       7 |   XXX  |   XXX  |   256  |
         +--------+--------+--------+
       .
       .
       .
         +--------+--------+
    1437 |   XXX  |   256  |
         +--------+--------+--------+--------+--------+
    1438 |   XXX  |   XXX  |   XXX  |   XXX  |   256  |
         +--------+--------+--------+--------+--------+
    1439 |   XXX  |   XXX  |   256  |
         +--------+--------+--------+
    Pixel
    CHID

    A list of lists of photon arrival time slices.
    The line break from one pixel to the next one is marked by the linebreab 
    symbol 2^8 = 256. This leaves 255 slices to encode arrival times.

### Saturated Pixels (2 + 2 * num. saturated pixel Byte)
   
    uint16
    +--------+--------+
    |        N        |
    +--------+--------+
    Number of saturated pixels

    uint16
    +--------+--------+--------+--------+     +--------+--------+
    |      CHID 0     |      CHID 1     | ... |      CHID N-1   |
    +--------+--------+--------+--------+     +--------+--------+
    A list of CHIDS of saturated pixels