#!/bin/python

import ppfun
import numpy as np
import cv2
import sys, os
import math
import random
import time
import curses

def curses_selection(scrn, text, options):
    selection = 0
    # get terminal width and height
    h, w = scrn.getmaxyx()
    # draw a box
    b_w = len(text) + 2
    scrn.addstr((h - 5) // 2    , (w - b_w) // 2, ' ' * b_w, curses.A_REVERSE)
    scrn.addstr((h - 5) // 2 + 1, (w - b_w) // 2, ' ' + text + ' ', curses.A_REVERSE)
    scrn.addstr((h - 5) // 2 + 2, (w - b_w) // 2, ' ' * b_w, curses.A_REVERSE)
    scrn.addstr((h - 5) // 2 + 4, (w - b_w) // 2, ' ' * b_w, curses.A_REVERSE)
    scrn.refresh()
    # input logic
    btn_w = ((b_w - 1) // len(options)) - 1
    while True:
        # draw the buttons
        # pls don't try to understand this, I wrote this at like 1 AM and have absolutely no idea how it works but it does
        scrn.addstr((h - 5) // 2 + 3, (w - b_w) // 2, '', curses.A_REVERSE)
        total_w = 0
        for option in options:
            attr = curses.A_REVERSE if options.index(option) != selection else 0
            scrn.addstr(' ', curses.A_REVERSE)
            total_w = total_w + 1
            scrn.addstr(' ' * ((btn_w - len(option)) // 2), attr)
            total_w = total_w + (btn_w - len(option)) // 2
            scrn.addstr(option, attr)
            total_w = total_w + len(option)
            scrn.addstr(' ' * ((btn_w - len(option)) // 2), attr)
            total_w = total_w + (btn_w - len(option)) // 2
        scrn.addstr(' ' * (b_w - total_w), curses.A_REVERSE)
        scrn.refresh()
        # input
        ch = scrn.getch()
        if ch == 10: # ASCII for the enter key
            # remove the textbox
            for y in range((h - 5) // 2, (h - 5) // 2 + 5):
                scrn.addstr(y, (w - b_w) // 2, ' ' * b_w)
            scrn.refresh()
            return options[selection]
        if ch == curses.KEY_RIGHT and selection < len(options) - 1:
            selection = selection + 1
        if ch == curses.KEY_LEFT and selection > 0:
            selection = selection - 1

def curses_prompt(scrn, text):
    result = ''
    # get terminal width and height
    h, w = scrn.getmaxyx()
    # draw a box
    b_w = len(text) + 2
    scrn.addstr((h - 5) // 2    , (w - b_w) // 2, ' ' * b_w, curses.A_REVERSE)
    scrn.addstr((h - 5) // 2 + 1, (w - b_w) // 2, ' ' + text + ' ', curses.A_REVERSE)
    scrn.addstr((h - 5) // 2 + 2, (w - b_w) // 2, ' ' * b_w, curses.A_REVERSE)
    scrn.addstr((h - 5) // 2 + 4, (w - b_w) // 2, ' ' * b_w, curses.A_REVERSE)
    scrn.refresh()
    while True:
        # draw the text field
        scrn.addstr((h - 5) // 2 + 3, (w - b_w) // 2, ' ', curses.A_REVERSE)
        scrn.addstr(result + ' ' * (b_w - 2 - len(result)))
        scrn.addstr(' ', curses.A_REVERSE)
        # input
        ch = scrn.getch()
        if ch == 10: # ASCII for the enter key
            # remove the textbox
            for y in range((h - 5) // 2, (h - 5) // 2 + 5):
                scrn.addstr(y, (w - b_w) // 2, ' ' * b_w)
            scrn.refresh()
            return result
        elif ch == curses.KEY_BACKSPACE and len(result) > 0:
            result = result[:-1]
        else:
            result = result + chr(ch)

def run(scrn):
    # clear the screen
    scrn.clear()
    curses.curs_set(False)
    t_h, t_w = scrn.getmaxyx()
    # print some info
    scrn.addstr('PPFunBot by portasynthinca3' + (' ' * (t_w - len('PPFunBot by portasynthinca3'))), curses.A_REVERSE)
    scrn.addstr(1, 0, 'Please wait, communicating with the server...', curses.A_BLINK)
    scrn.refresh()
    # create the ppfun API class
    pp = ppfun.PPFun_api()
    canv = pp.get_canv('d')
    choice_list = []
    scrn.addstr(1, 0, ' ' * len('Please wait, communicating with the server...'), 0)
    scrn.refresh()
    # ask the user for the file path
    path = curses_prompt(scrn, 'Please enter the full path to the image you would like to draw')
    # read the image
    try:
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        (sz_y, sz_x, channels) = img.shape
    except:
        curses_selection(scrn, 'Image loading error. Is this path correct?', ['OK'])
        exit()
    # render the preview
    render_preview = curses_selection(scrn, 'Would you like to see the preview of the image you\'re about to draw?', ['NO', 'YES'])
    if render_preview == 'YES':
        img_preview = img.copy()
        # actual rendering
        for y in range(sz_y):
            for x in range(sz_x):
                # extract pixel data
                if channels == 4:
                    (b, g, r, a) = img[y, x]
                else:
                    (b, g, r) = img[y, x]
                    a = 255
                # adjust the color
                (r, g, b) = canv.colors[canv.approx_color((r, g, b)) - 2]
                # assign the new color
                img_preview[y, x] = (b, g, r) if channels == 3 else (b, g, r, a)
        # extract path parts
        path_parts = os.path.splitext(path)
        # write the image
        preview_path = path_parts[0] + '_ppfun_prev' + path_parts[1]
        cv2.imwrite(preview_path, img_preview)
        curses_selection(scrn, 'Preview saved to ' + preview_path, ['OK'])
    # make a list of pixels
    for y in range(sz_y):
        for x in range(sz_x):
            if channels == 3:
                choice_list.append((x, y))
            elif img[y, x][3] > 64:
                choice_list.append((x, y))
    start_px_cnt = len(choice_list)
    # check if a backup exists
    path_parts = os.path.splitext(path)
    if os.path.exists(path_parts[0] + '_bup' + path_parts[1]):
        load_bup = curses_selection(scrn, 'There is a state backup for this image. Load it?', ['YES', 'NO'])
        if load_bup == 'YES':
            img = cv2.imread(path_parts[0] + '_bup' + path_parts[1], cv2.IMREAD_UNCHANGED)
            # re-make the list of pixels
            choice_list.clear()
            for y in range(sz_y):
                for x in range(sz_x):
                    if channels == 3:
                        choice_list.append((x, y))
                    elif img[y, x][3] > 64:
                        choice_list.append((x, y))
    # ask whether we should start drawing
    proceed = curses_selection(scrn, 'Estimated draw time: ' + str(math.ceil(len(choice_list) * 4 / 60)) + ' minutes. Proceed?', ['YES', 'NO'])
    if proceed == 'NO':
        exit()
    # ask the coordinates
    tl_x = int(curses_prompt(scrn, 'Enter the X ccordinate of the top-left corner in the world'))
    tl_y = int(curses_prompt(scrn, 'Enter the Y ccordinate of the top-left corner in the world'))
    # draw the image
    bup_cnt = 0
    while len(choice_list) > 0:
        # pick a random pixel
        element = random.choice(choice_list)
        choice_list.remove(element)
        (x, y) = element
        # stay at 50 seconds of cooldown
        while canv.remaining_cooldown() >= 50:
            scrn.addstr(2, 0, 'Cooldown        : ' + '{:4.1f}'.format(canv.remaining_cooldown()) + ' seconds')
            scrn.refresh()
        # get pixel color
        if channels == 4:
            (b, g, r, a) = img[y, x]
        else:
            (b, g, r) = img[y, x]
            a = 255
        # place it
        scrn.addstr(1, 0, 'Please wait, communicating with the server...', curses.A_BLINK)
        scrn.refresh()
        trying = True
        while trying:
            try:
                canv.set_pixel((tl_x + x, tl_y + y), canv.approx_color((r, g, b)))
                trying = False
            except:
                curses_selection(scrn, 'An error occured. Place a pixel manually in your browser, return here and hit enter', ['OK'])
        scrn.addstr(1, 0, ' ' * len('Please wait, communicating with the server...'), 0)
        scrn.refresh()
        # print some info
        scrn.addstr(1, 0, 'Current position: ' + str((tl_x + x, tl_y + y)))
        scrn.addstr(2, 0, 'Cooldown        : ' + '{:4.1f}'.format(canv.remaining_cooldown()) + ' seconds')
        scrn.addstr(3, 0, 'Progress        : ' + '{:5.2f}'.format(100 - (100 * len(choice_list) / start_px_cnt)) + '%')
        progress = int((1 - (len(choice_list) / start_px_cnt)) * (t_w - 2))
        scrn.addstr(4, 0, '[')
        for i in range(progress):
            scrn.addstr(' ', curses.A_REVERSE)
        for i in range(t_w - 2 - progress):
            scrn.addstr(' ')
        scrn.addstr(']')
        scrn.addstr(5, 0, 'Remaining time  : around ' + str(math.ceil(len(choice_list) / 15)) + ' minutes     ')
        scrn.refresh()
        bup_cnt = bup_cnt + 1
        if bup_cnt >= 10:
            bup_cnt = 0
            bup_img = np.zeros(img.shape, np.uint8)
            for point in choice_list:
                (x, y) = point
                bup_img[y, x] = img[y, x]
            path_parts = os.path.splitext(path)
            cv2.imwrite(path_parts[0] + '_bup' + path_parts[1], bup_img)
    curses_selection(scrn, 'The art is complete!', ['OK'])
    # remove the backup if it exists
    if os.path.exists(path_parts[0] + '_bup' + path_parts[1]):
        os.remove(path_parts[0] + '_bup' + path_parts[1])

if __name__ == "__main__":
    curses.wrapper(run)