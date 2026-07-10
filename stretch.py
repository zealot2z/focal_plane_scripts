"""
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage import exposure


img = np.array(Image.open("05-25-21_30_43calibration_square.png").convert('L'))

img_step1 = (img - img.min()) / (img.max() - img.min())
img_step1 = (img_step1 * 255).astype(np.uint8)

p_low, p_high = np.percentile(img, (30, 60))
img_step2 = np.clip((img_step1 - p_low) / (p_high - p_low), 0, 1)
img_step2 = (img_step2 * 255).astype(np.uint8)


#plt.imshow(img_step2, cmap='gray')
#plt.title("Percentile stretch")
plt.colorbar()
#plt.savefig("StretchedStep2.png")

#img_step3 = exposure.equalize_hist(img_step2)
img_step3 = exposure.equalize_adapthist(img_step2, clip_limit=0.03)


plt.imshow(img_step3, cmap='gray')
plt.title("Percentile stretch")
plt.savefig("StretchedStep3.png")
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage import exposure
import os

input_dir = "Calibrations"
output_dir = "StretchedCalibrations"

"""
# Loop through files
for filename in os.listdir(input_dir):
    if filename.lower().endswith(".png"):
        print(f"Processing {filename}...")

        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(
            output_dir,
            os.path.splitext(filename)[0] + "_stretched.png"
        )

        # Load image as grayscale
        img = np.array(Image.open(input_path).convert('L'))

        # Step 1: Rescale to full range
        if img.max() == img.min():
            continue  # avoid divide-by-zero

        img_step1 = (img - img.min()) / (img.max() - img.min())
        img_step1 = (img_step1 * 255).astype(np.uint8)

        # Step 2: Percentile stretch
        p_low, p_high = np.percentile(img, (30, 60))
        if p_high == p_low:
            continue  # avoid divide-by-zero

        img_step2 = np.clip((img_step1 - p_low) / (p_high - p_low), 0, 1)
        img_step2 = (img_step2 * 255).astype(np.uint8)

        # Step 3: Adaptive histogram equalization
        img_step3 = exposure.equalize_adapthist(img_step2, clip_limit=0.03)

        # Save result (clean image, no axes)
        Image.fromarray((img_step3 * 255).astype(np.uint8)).save(output_path)
"""

for filename in os.listdir(input_dir):
    if filename.lower().endswith(".png"):
        print(f"Processing {filename}...")

        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(
            output_dir,
            os.path.splitext(filename)[0] + "_stretched.png"
        )

        # Load RGB image
        img = np.array(Image.open(input_path).convert('RGB'))

        # Convert to float [0,1]
        img = img / 255.0

        # Convert to HSV (Value = brightness)
        import matplotlib.colors as mcolors
        hsv = mcolors.rgb_to_hsv(img)

        v = hsv[:, :, 2]

        # --- Apply your pipeline to brightness channel ---
        if v.max() == v.min():
            continue

        v1 = (v - v.min()) / (v.max() - v.min())

        p_low, p_high = np.percentile(v1, (30, 60))
        if p_high == p_low:
            continue

        v2 = np.clip((v1 - p_low) / (p_high - p_low), 0, 1)

        v3 = exposure.equalize_adapthist(v2, clip_limit=0.03)

        # Put processed brightness back
        hsv[:, :, 2] = v3

        # Convert back to RGB
        rgb_out = mcolors.hsv_to_rgb(hsv)

        # Save
        Image.fromarray((rgb_out * 255).astype(np.uint8)).save(output_path)

print("Done!")
