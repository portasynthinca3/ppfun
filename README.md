# ppfun
ppfun allows you to use the PixelPlanet.Fun's (hence the name) API in your Python code. I personally didn't come up with any use case besides auto-drawing bots. But you may. Please e-mail me if you come up with any idea, I will truly be interested.

Example code:
```python
# import the library
import ppfun

# create an API object
pp = ppfun.PPFun_api()
# print the list of available canvases
print('---------')
print('Canvases:')
for c in pp.list_canv():
    print(c['title'] + '\t\t' +
          c['description'] + '\t\t' +
          str(c['size']) + 'x' + str(c['size']) + '\t\t' +
          '(' + c['identifier'] + ')')
print('---------')
# get the main canvas (Earth)
canv = pp.get_canv('d')
# print the approximation of the lime color for this canvas
print('Lime color ID: ' + str(canv.approx_color((0, 255, 0))))
# set a pixel at (-1532, -550) and print the cooldown time
canv.set_pixel((-1532, -550), canv.approx_color((0, 255, 0)))
print('Cooldown after setting the pixel: ' + str(canv.remaining_cooldown()))
```
# installation
`pip install ppfun`

# documentation
## PPFun_api class
This is where the journey starts. You create a client by creating an instance of this class. The library then fetches some data from the server.
It is available through these functions:
* `list_canv()` - returns a list of canvas descriptors. Each descriptor is a dictionary that contains the `title`, `description`, `size` and `identifier` keys
* `get_canv(ident)` - returns a canvas object of the canvas with a specific identifier
## PPFun_canv class
This class contains all the functions you need to create your masterpiece. Here they are:
* `approx_color(rgb_tuple)` - returns a color index that approximates the given color the most
* `set_pixel(pos_tuple, color_index)` - places a pixel on the map. Throws an exception on error, returns True on success
* `remaining_cooldown()` - returns the remaining cooldown in seconds