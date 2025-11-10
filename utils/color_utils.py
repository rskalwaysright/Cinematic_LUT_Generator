# Placeholder for any additional color utilities you may want to add.
from PIL import Image
import numpy as np

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(int(x) for x in rgb)
