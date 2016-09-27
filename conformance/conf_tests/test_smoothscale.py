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


def test_subsurface_smoothscale(surface):
    """Test scaling a small subsurface"""
    obj = _make_object()

    transform.set_smoothscale_backend('GENERIC')

    obj_sub = obj.subsurface((20, 20, 20, 25))

    surface.blit(obj, (20, 20))
    surface.blit(obj_sub, (60, 20))
    obj1 = transform.smoothscale(obj_sub, (obj_sub.get_width(), obj_sub.get_height()))
    surface.blit(obj1, (120, 20))
    obj1 = transform.smoothscale(obj_sub, (20, 20))
    surface.blit(obj1, (60, 60))
    obj1 = transform.smoothscale(obj_sub, (40, 40))
    surface.blit(obj1, (80, 80))
    obj1 = transform.smoothscale(obj_sub, (60, 60))
    surface.blit(obj1, (160, 160))
    obj1 = transform.smoothscale(obj_sub, (120, 120))
    surface.blit(obj1, (220, 220))


def test_int_smoothscale(surface):
    """Simple integer scaling tests"""
    obj = _make_object()

    transform.set_smoothscale_backend('GENERIC')

    surface.blit(obj, (20, 20))
    obj1 = transform.smoothscale(obj, (obj.get_width(), obj.get_height()))
    surface.blit(obj1, (120, 20))
    obj1 = transform.smoothscale(obj, (20, 20))
    surface.blit(obj1, (60, 60))
    obj1 = transform.smoothscale(obj, (40, 40))
    surface.blit(obj1, (80, 80))
    obj1 = transform.smoothscale(obj, (60, 60))
    surface.blit(obj1, (160, 160))
    obj1 = transform.smoothscale(obj, (120, 120))
    surface.blit(obj1, (320, 320))


def test_x_smoothscale(surface):
    """Scale x axis only"""
    obj = _make_object()

    transform.set_smoothscale_backend('GENERIC')

    surface.blit(obj, (20, 20))
    obj1 = transform.smoothscale(obj, (25, 20))
    surface.blit(obj1, (80, 80))
    obj2 = transform.smoothscale(obj, (35, 20))
    surface.blit(obj2, (160, 160))
    obj3 = transform.smoothscale(obj, (55, 20))
    surface.blit(obj3, (240, 160))
    obj4 = transform.smoothscale(obj, (15, 20))
    surface.blit(obj4, (240, 240))
    obj5 = transform.smoothscale(obj, (100, 20))
    surface.blit(obj5, (320, 320))


def test_y_smoothscale(surface):
    """Scale y axis only"""
    obj = _make_object()

    transform.set_smoothscale_backend('GENERIC')

    surface.blit(obj, (20, 20))
    obj1 = transform.smoothscale(obj, (20, 25))
    surface.blit(obj1, (80, 80))
    obj2 = transform.smoothscale(obj, (20, 35))
    surface.blit(obj2, (160, 160))
    obj3 = transform.smoothscale(obj, (20, 55))
    surface.blit(obj3, (240, 160))
    obj4 = transform.smoothscale(obj, (20, 15))
    surface.blit(obj4, (240, 240))
    obj5 = transform.smoothscale(obj, (20, 100))
    surface.blit(obj5, (320, 320))


def test_varied_smoothscale(surface):
    """Scale with more varies factors"""
    obj = _make_object()

    transform.set_smoothscale_backend('GENERIC')

    surface.blit(obj, (20, 20))
    obj1 = transform.smoothscale(obj, (25, 55))
    surface.blit(obj1, (80, 80))
    obj1 = transform.smoothscale(obj, (14, 13))
    surface.blit(obj1, (160, 160))
    obj1 = transform.smoothscale(obj, (72, 68))
    surface.blit(obj1, (320, 320))
