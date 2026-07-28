import numpy as np
from PIL import Image
from astropy.io import fits

## grayscale =('L' mode)
img = Image.open("subject.png").convert("L")

data = np.array(img)

hdu = fits.PrimaryHDU(data=data)

hdu.writeto("grayscale.fits", overwrite=True)
