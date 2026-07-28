
import astropy.units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time
import numpy as np

"""
##Note: Needs to be executed in fove envrionment

location = EarthLocation(
    lat=31.674997676 * u.deg, lon=-110.9521311 * u.deg, height=1268 * u.m
)

#time in UTC; mountain time is -7 hours
time = Time("2026-06-10 04:45:00")

altaz_frame = AltAz(obstime=time, location=location)

Elevation, Azimuth = 44.833203, 83.484093
local_coords=SkyCoord(
    az=Azimuth * u.deg, alt=Elevation * u.deg, frame=altaz_frame
)

convert = local_coords.transform_to("icrs")

print(f"RA (HMS):      {convert.ra.to_string(unit=u.hour, sep='hms')}")
print(f"Dec (Degrees): {convert.dec.deg:.5f}°")
"""

#"""

##change timestamps, elevations, and azimiuths accordingly
timestamps = [
    "2026-05-26 03:52:54",
    "2026-05-26 03:55:12",
    "2026-05-26 03:56:50",
    "2026-05-26 03:57:43",
    "2026-05-26 04:02:05",
    "2026-05-26 04:10:33",
    "2026-05-26 04:16:38",
    "2026-05-26 04:26:27",
    "2026-05-26 04:30:43",
    "2026-05-26 04:37:26",
    "2026-05-26 04:43:28",
    "2026-05-26 04:50:37",
    "2026-05-26 04:59:50",
    "2026-05-26 05:08:22",
    "2026-05-26 05:17:35",
    "2026-05-26 05:28:45",
    "2026-05-26 05:35:47",
    "2026-05-26 05:41:31",
    "2026-05-26 05:49:50",
    "2026-05-26 05:58:04",
    "2026-05-26 06:05:58",
    "2026-05-26 06:10:35",
    "2026-05-26 06:19:19",
    "2026-05-26 06:25:46",
    "2026-05-26 06:31:39",
    "2026-05-26 06:36:45",
    "2026-05-26 06:41:56",
    "2026-05-26 06:47:30",
    "2026-05-26 06:57:43",
    "2026-05-26 07:03:08",
    "2026-05-26 07:08:39",
    "2026-05-26 07:17:14",
    "2026-05-26 07:24:06",
    "2026-05-26 07:29:33",
    "2026-05-26 07:35:34",
    "2026-05-26 07:41:45",
    "2026-05-26 07:49:43",
    "2026-05-26 07:59:07",
    "2026-05-26 08:04:48",
    "2026-05-26 08:13:39",
    "2026-05-26 08:19:12",
    "2026-05-26 08:25:48",
    "2026-05-26 08:30:42",
    "2026-05-26 08:36:46",
    "2026-05-26 08:42:07",
    "2026-05-26 08:47:10",
    "2026-05-26 08:51:49",
    "2026-05-26 08:56:11",
]

elevations = [
    66.6017,
    66.898,
    67.203,
    67.50950661,
    68.12959911,
    69.72024188,
    70.71202185,
    72.801,
    73.619,
    74.831,
    76.375,
    77.187,
    78.868,
    80.089,
    81.449,
    82.464,
    82.838,
    82.93825487,
    82.705,
    82.17,
    81.352,
    80.745,
    79.541,
    78.432,
    77.338,
    76.483,
    75.608,
    74.54,
    72.535,
    71.406,
    70.82,
    68.971,
    67.659,
    66.637,
    65.364,
    64.115,
    62.576,
    60.741,
    59.579,
    58.055,
    56.78,
    55.453,
    54.426,
    53.366,
    52.307,
    51.244,
    50.378,
    49.513
]

azimuths = [
    66.519889,
    66.412,
    66.292,
    66.17220183,
    65.90273854,
    65.05390838,
    64.39909726,
    62.579,
    61.664,
    60.048,
    58.117,
    55.546,
    50.555,
    45.209,
    35.889,
    22.577,
    11.879,
    1.0493,
    347.846,
    336.762,
    327.157,
    322.198,
    315.192,
    310.665,
    307.269,
    305.135,
    303.323,
    301.479,
    298.847,
    297.715,
    296.964,
    295.882,
    295.161,
    294.7,
    294.228,
    293.856,
    293.505,
    293.232,
    293.121,
    293.044,
    293.033,
    293.053,
    293.106,
    293.189,
    293.277,
    293.397,
    293.509,
    293.63
]

location = EarthLocation(
    lat=31.674997676 * u.deg, lon=-110.9521311 * u.deg, height=1268 * u.m
)

print("RA And DEC in order of provided timestamps:")
for t, el, az in zip(timestamps, elevations, azimuths):

    time = Time(t)
    altaz_frame = AltAz(obstime=time, location=location)

    local_coords = SkyCoord(
        az=az * u.deg,
        alt=el * u.deg,
        frame=altaz_frame
    )

    convert = local_coords.transform_to("icrs")

    print(f"{convert.ra.to_string(unit=u.hour, sep='hms')}    {convert.dec.deg:.5f}°")
    # {convert.dec.deg:.5f}
    # {convert.ra.to_string(unit=u.hour, sep='hms')}
#"""

