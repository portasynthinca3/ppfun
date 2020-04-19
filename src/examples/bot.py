#!/bin/python

import ppfun
import numpy as np
import cv2
import sys, os
import math
import random

def run():
    if '--help' in sys.argv:
        print(sys.argv)
        print('Usage: bot.py path x y')
        return
    # read command-line arguments
    path = sys.argv[1]
    tl_x = int(sys.argv[2])
    tl_y = int(sys.argv[3])
    # read the image
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    (sz_y, sz_x, channels) = img.shape
    print('Read image with size: ' + str((sz_x, sz_y)))
    # create the ppfun API class
    pp = ppfun.PPFun_api()
    canv = pp.get_canv('d')
    choice_list = []
    # make a list of pixels
    for y in range(sz_y):
        for x in range(sz_x):
            if channels == 3:
                choice_list.append((x, y))
            elif img[y, x][3] > 64:
                choice_list.append((x, y))
    print('Estimated draw time: ' + str(math.ceil(len(choice_list) * 4 / 60)) + ' minutes')
    # draw the image
    while len(choice_list) > 0:
        # pick a random pixel
        element = random.choice(choice_list)
        choice_list.remove(element)
        (x, y) = element
        # stay at 50 seconds of cooldown
        while canv.remaining_cooldown() >= 50:
            pass
        # get pixel color
        if channels == 4:
            (b, g, r, a) = img[y, x]
        else:
            (b, g, r) = img[y, x]
            a = 255
        # place it
        trying = True
        while trying:
            try:
                canv.set_pixel((tl_x + x, tl_y + y), canv.approx_color((r, g, b)))
                trying = False
            except Exception as e:
                print('An error occured. You probably need to enter Captcha in your browser. Place a pixel somewhere manually, then return here and hit Enter.\nError code: ' + str(e))
                print('Pixel: ' + str((x, y)) + ', color: ' + str((r, g, b, a)) + ', color index: ' + str(canv.approx_color((r, g, b))))
                input()
        # print some info
        print('Placed a pixel at ' + str((tl_x + x, tl_y + y)) + ' - ' +
              '{:5.2f}'.format(100 - (100 * len(choice_list) / (sz_x * sz_y))) + '% - cooldown: ' + '{:4.1f}'.format(canv.remaining_cooldown()) + ' s')

if __name__ == "__main__":
    run()