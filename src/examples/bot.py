#!/bin/python

import ppfun
import numpy as np
import cv2
import sys, os
import math
import random
import time
import curses
import json

paused = False
method = 'random'

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

def curses_prompt(scrn, text, suggestion):
    result = suggestion
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

def curses_bar(scrn, y, x, progress, width):
    s = '|'
    # calculate the amount of filled blocks
    b = (width - 2) * progress
    # print the full blocks
    for i in range(int(math.floor(b))):
        s = s + '█'
    # print the partial block
    remainder = b - math.floor(b)
    if remainder <= 1/8:
        s = s + '▏'
    elif remainder <= 2/8:
        s = s + '▎'
    elif remainder <= 3/8:
        s = s + '▍'
    elif remainder <= 4/8:
        s = s + '▌'
    elif remainder <= 5/8:
        s = s + '▋'
    elif remainder <= 6/8:
        s = s + '▊'
    elif remainder <= 7/8:
        s = s + '▉'
    else:
        s = s + '█'
    # print one string normally
    scrn.addstr(y, x, s)
    # print the rest as inverted blocks
    scrn.addstr('█' * int(width - 2 - math.ceil(b)), curses.A_REVERSE)
    scrn.addstr('|')

def curses_status(scrn, text):
    # get terminal width and height
    h, w = scrn.getmaxyx()
    scrn.addstr(h - 1, 0, 'Status: ' + text + (' ' * (w - len('Status: ' + text) - 1)), curses.A_REVERSE)
    scrn.refresh()

def run(scrn):
    global method
    global paused
    # clear the screen
    scrn.clear()
    curses.curs_set(False)
    t_h, t_w = scrn.getmaxyx()
    # print some info
    scrn.addstr('PPFunBot by portasynthinca3' + (' ' * (t_w - len('PPFunBot by portasynthinca3'))), curses.A_REVERSE)
    curses_status(scrn, 'communicating with the PPFun server')
    # create the ppfun API class
    pp = ppfun.PPFun_api()
    canv = pp.get_canv('d')
    choice_list = []
    # load the configuration
    cfg_path = os.path.expanduser('~/.ppfun_bot_cfg.json')
    if os.path.exists(cfg_path):
        with open(cfg_path, 'r') as f:
            cfg = json.load(f)
            if 'method' in cfg:
                method = cfg['method']
            if 'paused' in cfg:
                paused = cfg['paused']
    # ask the user for the file path
    curses_status(scrn, '')
    path = os.path.expanduser(curses_prompt(scrn, 'Please enter the full path to the image you would like to draw', ''))
    curses_status(scrn, 'loading the image')
    # read the image
    try:
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        (sz_y, sz_x, channels) = img.shape
    except:
        curses_selection(scrn, 'Image loading error. Is this path correct?', ['OK'])
        exit()
    # render the preview
    render_preview = curses_selection(scrn, 'Render the preview?', ['NO', 'YES'])
    if render_preview == 'YES':
        curses_status(scrn, 'rendering the preview')
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
                img_preview[y, x] = (b, g, r) if channels == 3 else (b, g, r, 255 if a > 64 else 0)
        # extract path parts
        path_parts = os.path.splitext(path)
        # write the image
        preview_path = path_parts[0] + '_ppfun_prev' + path_parts[1]
        cv2.imwrite(preview_path, img_preview)
        curses_selection(scrn, 'Preview saved to ' + preview_path, ['OK'])
    # make a list of pixels
    for y in range(sz_y):
        curses_status(scrn, 'processing the image - ' + '{:5.1f}'.format(100 * y / sz_y) + '%')
        for x in range(sz_x):
            if channels == 3:
                choice_list.append((x, y))
            elif img[y, x][3] > 64:
                choice_list.append((x, y))
    start_px_cnt = len(choice_list)
    curses_status(scrn, '')
    # check if a backup exists
    path_parts = os.path.splitext(path)
    if os.path.exists(path_parts[0] + '_bup' + path_parts[1]):
        load_bup = curses_selection(scrn, 'There is a state backup for this image. Load it?', ['YES', 'NO'])
        if load_bup == 'YES':
            curses_status(scrn, 'loading the backup')
            img = cv2.imread(path_parts[0] + '_bup' + path_parts[1], cv2.IMREAD_UNCHANGED)
            # re-make the list of pixels
            choice_list.clear()
            curses_status(scrn, 'processing the backup - ' + '{:5.1f}'.format(100 * y / sz_y) + '%')
            for y in range(sz_y):
                for x in range(sz_x):
                    if channels == 3:
                        choice_list.append((x, y))
                    elif img[y, x][3] > 64:
                        choice_list.append((x, y))
            # load the coordinates
            with open(path_parts[0] + '_bup.json', 'r') as fp:
                d = json.load(fp)
                tl_x = d['x']
                tl_y = d['y']
    else:
        load_bup = 'NO'
    # ask whether we should start drawing
    proceed = curses_selection(scrn, 'Estimated draw time: ' + str(math.ceil(len(choice_list) * 4 / 60)) + ' minutes. Proceed?', ['YES', 'NO'])
    if proceed == 'NO':
        exit()
    # ask the coordinates
    tl_x = int(curses_prompt(scrn, 'Enter the X ccordinate of the top-left corner in the world', str(tl_x) if load_bup == 'YES' else ''))
    tl_y = int(curses_prompt(scrn, 'Enter the Y ccordinate of the top-left corner in the world', str(tl_y) if load_bup == 'YES' else ''))
    # draw the image
    bup_cnt = 0
    while len(choice_list) > 0:
        # take user input, probably
        scrn.nodelay(1)
        inp = scrn.getch()
        scrn.nodelay(0)
        if inp < 256 and inp > 0:
            if chr(inp) == 'p':
                paused = True
            elif chr(inp) == 'r':
                paused = False
            elif chr(inp) == 'm':
                method = curses_selection(scrn, 'Select the drawing method (current: ' + method + ')', ['random', 'prog', 'rev-prog'])
            elif chr(inp) == 's':
                if method not in ['prog', 'rev-prog']:
                    curses_selection(scrn, 'Pixel skipping is supported only in progressive and reverse-progressive modes', ['OK'])
                else:
                    if method == 'prog':
                        choice_list = choice_list[1:]
                        element = choice_list[0]
                    elif method == 'rev-prog':
                        choice_list = choice_list[:-1]
                        element = choice_list[-1]
                    scrn.addstr(1, 0, 'Current position: ' + str((tl_x + element[0], tl_y + tl_x + element[1])))
                    curses_status(scrn, 'skipped one pixel. Pause is now enabled')
            elif chr(inp) == 'c':
                # load existing config
                if os.path.exists(cfg_path):
                    with open(cfg_path, 'r') as f:
                        cfg = json.load(f)
                else:
                    cfg = {}
                # ask the user for new options
                cfg['method'] = curses_selection(scrn, 'Select the default drawing method (current: ' + (cfg['method'] if 'method' in cfg else '<none>') + ')',
                                                 ['random', 'prog', 'rev-prog'])
                cfg['paused'] = (curses_selection(scrn, 'Will the drawing be paused by default?', ['YES', 'NO']) == 'YES')
                # save config
                with open(cfg_path, 'w') as f:
                    json.dump(cfg, f)
            elif chr(inp) == 'q':
                exit()
        # print some info
        scrn.addstr(1, 0, 'Current position: ' + str((tl_x + x, tl_y + y)))
        scrn.addstr(2, 0, 'Cooldown        : ' + '{:4.1f}'.format(canv.remaining_cooldown()) + ' seconds')
        scrn.addstr(3, 0, 'Progress        : ' + '{:5.2f}'.format(100 - (100 * len(choice_list) / start_px_cnt)) + '%')
        curses_bar(scrn, 4, 0, 1 - (len(choice_list) / start_px_cnt), t_w)
        scrn.addstr(5, 0, 'Remaining time  : around ' + str(math.ceil(len(choice_list) / 15)) + ' minutes     ')
        scrn.addstr(t_h - 2, 0, 'P - pause',              curses.A_REVERSE); scrn.addstr('    ')
        scrn.addstr(            'R - resume',             curses.A_REVERSE); scrn.addstr('    ')
        scrn.addstr(            'M - change method',      curses.A_REVERSE); scrn.addstr('    ')
        scrn.addstr(            'S - skip pixel',         curses.A_REVERSE); scrn.addstr('    ')
        scrn.addstr(            'C - change default cfg', curses.A_REVERSE); scrn.addstr('    ')
        scrn.addstr(            'Q - quit',               curses.A_REVERSE); scrn.addstr('    ')
        scrn.refresh()
        # some tests
        if canv.remaining_cooldown() >= 50:
            scrn.addstr(2, 0, 'Cooldown        : ' + '{:4.1f}'.format(canv.remaining_cooldown()) + ' seconds')
            curses_status(scrn, 'cooling down')
            continue
        if paused:
            curses_status(scrn, 'paused')
            continue
        # pick a pixel to draw
        if method == 'random':
            element = random.choice(choice_list)
        elif method == 'prog':
            element = choice_list[0]
        elif method == 'rev-prog':
            element = choice_list[-1]
        choice_list.remove(element)
        (x, y) = element
        # get pixel color
        if channels == 4:
            (b, g, r, a) = img[y, x]
        else:
            (b, g, r) = img[y, x]
            a = 255
        # place it
        curses_status(scrn, 'communicating with the server')
        trying = True
        while trying:
            try:
                canv.set_pixel((tl_x + x, tl_y + y), canv.approx_color((r, g, b)))
                trying = False
            except:
                curses_selection(scrn, 'An error occured. Place a pixel manually in your browser, return here and hit enter', ['OK'])
        # make a backup if needed
        bup_cnt = bup_cnt + 1
        if bup_cnt >= 10:
            bup_cnt = 0
            # write the image first
            bup_img = np.zeros(img.shape, np.uint8)
            for point in choice_list:
                (x, y) = point
                bup_img[y, x] = img[y, x]
            path_parts = os.path.splitext(path)
            cv2.imwrite(path_parts[0] + '_bup' + path_parts[1], bup_img)
            # write the coordinates
            with open(path_parts[0] + '_bup.json', 'w') as fp:
                json.dump({'x':tl_x, 'y':tl_y}, fp)
    curses_selection(scrn, 'The art is complete!', ['QUIT'])
    # remove the backup if it exists
    if os.path.exists(path_parts[0] + '_bup' + path_parts[1]):
        os.remove(path_parts[0] + '_bup' + path_parts[1])
        os.remove(path_parts[0] + '_bup.json')

if __name__ == "__main__":
    curses.wrapper(run)