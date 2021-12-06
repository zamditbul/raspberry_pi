import board
import neopixel
import time

#neopixel
num_pixels=16
pixel_pin=board.D18
ORDER=neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5,auto_write=False,pixel_order=ORDER)

def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    hlen= len(hex)
    return tuple(int(hex[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))
print(hex_to_rgb('#ff9999'))
pixels.fill(hex_to_rgb('#ff9999'))
#pixels.fill((255,153,153))
pixels.show()