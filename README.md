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