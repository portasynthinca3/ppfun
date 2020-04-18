# ppfun by portasynthinca3
# distributed under WTFPL

import requests
import json
import datetime

class PPFun_Exception(Exception):
    pass

# the canvas class
class PPFun_canv():
    ident_no = 0
    ident = ''
    title = ''
    colors = []
    desc = ''
    size = 0
    _cooldown = 0
    _cooldown_upd = datetime.datetime.now()

    # class constructor
    def __init__(self, desc, iid):
        self.ident_no = int(iid)
        self.ident = desc['ident']
        self.title = desc['title']
        self.desc = desc['desc']
        self.size = desc['size']
        self.colors = [(c[0], c[1], c[2]) for c in desc['colors']]

    # returns the number of the most similar color
    def approx_color(self, rgb):
        best_color_id = 0
        best_color_diff = 255 * 3
        (r, g, b) = rgb
        # go through the color
        for c in self.colors:
            (cr, cg, cb) = c
            # calculate the difference
            c_diff = abs(cr - r) + abs(cg - g) + abs(cb - b)
            # if that difference is smaller than the current best one, assign the new best color
            if c_diff < best_color_diff:
                best_color_diff = c_diff
                best_color_id = self.colors.index(c)
        return best_color_id

    # sets a pixel on this canvas
    def set_pixel(self, pos, color):
        (x, y) = pos
        # make a request
        r = requests.post('https://pixelplanet.fun/api/pixel', data=json.dumps({
            'cn': self.ident_no,
            'x': x,
            'y': y,
            'clr': color,
            'token': None
        }), headers={
            'Accept': '*/*',
            'Content-Type': 'application/json'
        })
        # parse the response
        response = r.json()
        if 'errors' in response:
            for err in response['errors']:
                raise PPFun_Exception(err['msg'])
            return False
        if 'waitSeconds' in response:
            self._cooldown = response['waitSeconds']
            self._cooldown_upd = datetime.datetime.now()
            return True

    # returns the remaining cooldown time in seconds
    def remaining_cooldown(self):
        adjust = datetime.datetime.now() - self._cooldown_upd
        self._cooldown = self._cooldown - adjust.total_seconds()
        self._cooldown_upd = datetime.datetime.now()
        if self._cooldown < 0:
            self._cooldown = 0
        return self._cooldown

# the main class
class PPFun_api():
    json_canvases = {}
    name = ''

    # class constructor
    def __init__(self):
        # make an initial request
        me = requests.get('https://pixelplanet.fun/api/me').json()
        self.name = me['name']
        self.json_canvases = me['canvases']

    # returns a canvas object by its identifier
    def get_canv(self, ident):
        # go through the JSON canvas descriptions
        for k in self.json_canvases:
            c_json = self.json_canvases[k]
            c_ident = c_json['ident']
            # search for a specific identifier
            if c_ident == ident:
                return PPFun_canv(c_json, k)
        # no such canvases exist
        return None

    # returns a list of canvas identifiers, names, descriptions and sizes
    def list_canv(self):
        result = []
        # go through the JSON canvas descriptions
        for k in self.json_canvases:
            c_json = self.json_canvases[k]
            result.append({'identifier':  c_json['ident'],
                           'title':       c_json['title'],
                           'description': c_json['desc'],
                           'size':        c_json['size']})
        return result