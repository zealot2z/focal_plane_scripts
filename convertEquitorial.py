import astropy.units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time
import numpy as np

##Note: Needs to be executed in fove envrionment

location = EarthLocation(
    lat=31.674997676 * u.deg, lon=-110.9521311 * u.deg, height=1268 * u.m
)

#time in UTC; mountain time is -7 hours
time = Time("2026-05-25 3:54:52")

altaz_frame = AltAz(obstime=time, location=location)

Elevation, Azimuth = 66.6117, 66.518889

local_coords=SkyCoord(
    az=Azimuth * u.deg, alt=Elevation * u.deg, frame=altaz_frame
)

convert = local_coords.transform_to("icrs")

print(f"RA (HMS):      {convert.ra.to_string(unit=u.hour, sep='hms')}")
print(f"Dec (Degrees): {convert.dec.deg:.5f}°")