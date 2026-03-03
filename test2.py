from PIL import Image
import numpy as np

# Make an image with large "fake pixels" like ComfyUI might generate
img = Image.new("RGB", (256, 256), "white")
pixels = img.load()
for x in range(256):
    for y in range(256):
        # 16x16 blocks
        cx = x // 16
        cy = y // 16
        if (cx+cy) % 2 == 0:
            pixels[x, y] = (0, 0, 0)
        else:
            pixels[x, y] = (255, 255, 255)

# Add a slight noise or offset (since AI isn't perfect)
for x in range(256):
    for y in range(256):
        if x > 120 and x < 135:
            pixels[x, y] = (255, 0, 0)

# Downscale using nearest to 16x16
d_nearest = img.resize((16, 16), Image.NEAREST)
d_box = img.resize((16, 16), Image.BOX)
