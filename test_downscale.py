from PIL import Image, ImageDraw
import numpy as np
from src.modules.post_processing.downscaler import Downscaler

# create a dummy image that simulates AI "chunky" pixel art
# grid is not perfectly aligned
img = Image.new("RGB", (512, 512), "white")
d = ImageDraw.Draw(img)
for i in range(0, 512, 16):
    for j in range(0, 512, 16):
        c = (i//2, j//2, 100)
        # draw a block which is slightly off
        d.rectangle([i, j, i+15, j+15], fill=c)

# downscale it to 32x32
d_nearest = img.resize((32, 32), Image.NEAREST)
d_bilinear = img.resize((32, 32), Image.BILINEAR)
d_lanczos = img.resize((32, 32), Image.LANCZOS)
