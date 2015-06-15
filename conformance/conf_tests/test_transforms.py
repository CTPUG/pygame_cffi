# Simple transform tests

from pygame import transform, surface, draw


def _make_object():
   """Create a vaguely interesting object to transform."""
   obj = surface.Surface((40, 80), depth=32)
   draw.line(obj, (255, 0, 0, 255), (10, 10), (10, 40), 3)
   draw.line(obj, (255, 255, 0, 255), (10, 10), (40, 10), 3)
   draw.line(obj, (255, 128, 128, 255), (40, 10), (40, 40), 2)
   draw.lines(obj, (255, 255, 255, 255), 1, [(20, 20), (20, 30), (30, 30)])
   return obj


def test_flip(surface):
   """Simple flip tests"""
   obj = _make_object()

   surface.blit(obj, (20, 20))
   obj1 = transform.flip(obj, True, False)
   surface.blit(obj1, (80, 80))
   obj1 = transform.flip(obj, False, True)
   surface.blit(obj1, (160, 160))
   obj1 = transform.flip(obj, True, True)
   surface.blit(obj1, (320, 320))


def test_scale(surface):
   """Simple scale tests"""
   obj = _make_object()

   surface.blit(obj, (20, 20))
   obj1 = transform.scale(obj, (100, 100))
   surface.blit(obj1, (80, 80))
   obj2 = transform.scale(obj1, (60, 60))
   surface.blit(obj2, (160, 160))
   obj3 = transform.scale(obj, (60, 60))
   surface.blit(obj3, (240, 160))
   obj1 = transform.scale2x(obj)
   surface.blit(obj1, (240, 240))
   obj1 = transform.scale2x(obj2)
   surface.blit(obj1, (320, 320))


def test_rotate(surface):
   """Simple rotation tests"""
   obj = _make_object()

   surface.blit(obj, (20, 20))
   obj1 = transform.rotate(obj, 90)
   surface.blit(obj1, (80, 20))
   obj1 = transform.rotate(obj, 180)
   surface.blit(obj1, (160, 20))
   obj1 = transform.rotate(obj, 270)
   surface.blit(obj1, (240, 20))
   obj1 = transform.rotate(obj, -90)
   surface.blit(obj1, (320, 20))
   obj1 = transform.rotate(obj, -180)
   surface.blit(obj1, (480, 20))
   x = 20
   y = 100
   for angle in range(1, 200, 7):
      obj1 = transform.rotate(obj, angle)
      surface.blit(obj1, (x, y))
      x += obj1.get_width() + 5
      if x > 650:
         y += 2*obj.get_height() + 5
         x = 20


def test_chop(surface):
    """Simple tests of transform.chop"""
    obj = _make_object()
    obj1 = transform.chop(obj, (10, 10, 10, 10))
    obj2 = transform.chop(obj, (10, 10, 20, 20))
    obj3 = transform.chop(obj, (0, 0, 100, 100))
    obj4 = transform.chop(obj, (5, 5, 50, 50))

    surface.blit(obj, (20, 20))
    surface.blit(obj1, (80, 20))
    surface.blit(obj2, (160, 20))
    surface.blit(obj3, (240, 20))
    surface.blit(obj4, (320, 20))

def test_rotozoom(surface):
    obj = _make_object()
    x = 20
    y = 20
    space = obj.get_height()
    for angle in range(1, 200, 14):
        for scale in range(5, 20, 3):
            obj1 = transform.rotozoom(obj, angle, scale / 10.0)
            surface.blit(obj1, (x, y))
            x += obj1.get_width() + 5
            space = max(space, obj1.get_height())
            if x > 650:
                y += space + 5
                x = 20
