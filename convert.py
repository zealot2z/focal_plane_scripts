import astropy.units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

##Note: Needs to be executed in fove envrionment

target = SkyCoord(ra="14h50m32s", dec="+74d09m20s", frame="icrs")

location = EarthLocation(
    lat=31.674997676 * u.deg, lon=-110.9521311 * u.deg, height=1268 * u.m
)

#time in UTC; mountain time is -7 hours
time = Time("2026-06-10 8:00:55")

altaz_frame = AltAz(obstime=time, location=location)

convert = target.transform_to(altaz_frame)

print(f"Elevation: {convert.alt.deg:.4f}")
print(f"Azimuth:  {convert.az.deg:.4f}")

"""
#uses LEDs from 5-25-20_18_07
leds = np.array([
    [2406.31, 641.55],
    [770.69, 1410.00],
    [768.56, 639.61],
    [1216.57, 1850.31],
    [1982.91, 1842.83],
    [2418.52, 1398.68],
    [1210.03, 197.01],
    [1974.15, 198.08]
])

pts = leds.astype(np.float32)

ellipse = cv2.fitEllipse(pts)

(center_x, center_y), (major_axis, minor_axis), angle = ellipse

print("Center:", center_x, center_y)

fig, ax = plt.subplots()

ax.scatter(leds[:,0], leds[:,1], c='red')

e = Ellipse(
    (center_x, center_y),
    major_axis,
    minor_axis,
    angle=angle,
    fill=False,
    color='blue',
    lw=2
)

ax.add_patch(e)

ax.plot(center_x, center_y, 'gx', ms=15, mew=3)

ax.set_aspect('equal')
plt.savefig('fit.png')
"""