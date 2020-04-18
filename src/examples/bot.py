#!/bin/python

import ppfun
import numpy as np
import cv2
import sys
import math

def run():
    if '--help' in sys.argv:
        print(sys.argv)
        print('Usage: bot.py path x y [restore_x restore_y]')
        return
    # read command-line arguments
    path = sys.argv[1]
    tl_x = int(sys.argv[2])
    tl_y = int(sys.argv[3])
    st_x = 0
    st_y = 0
    if len(sys.argv) == 6:
        st_x = int(sys.argv[4]) - tl_x
        st_y = int(sys.argv[5]) - tl_y
    # read the image
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    (sz_y, sz_x, _) = img.shape
    print('Read image with size: ' + str((sz_x, sz_y)))
    print('Estimated draw time: ' + str(math.ceil(sz_x * sz_y * 4 / 60)) + ' minutes')
    # create the ppfun API class
    pp = ppfun.PPFun_api()
    canv = pp.get_canv('d')
    # draw the image
    for y in range(st_y, sz_y):
        for x in range(st_x, sz_x):
            # stay at 50 seconds of cooldown
            while canv.remaining_cooldown() >= 50:
                pass
            # get pixel color
            (b, g, r, a) = img[y, x]
            # place a pixel if it's not fully transparent
            if a > 64:
                print(str((x, y)))
                canv.set_pixel((tl_x + x, tl_y + y), canv.approx_color((r, g, b)))
                print('Placed a pixel at ' + str((tl_x + x, tl_y + y)) + ' - ' +
                  str((100 * (y * sz_x + x)) / (sz_x * sz_y)) + '% - cooldown: ' + str(canv.remaining_cooldown()) + ' s')
        st_x = 0

if __name__ == "__main__":
    run()