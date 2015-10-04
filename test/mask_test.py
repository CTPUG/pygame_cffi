#################################### IMPORTS ###################################

if __name__ == '__main__':
    import sys
    import os
    pkg_dir = os.path.split(os.path.abspath(__file__))[0]
    parent_dir, pkg_name = os.path.split(pkg_dir)
    is_pygame_pkg = (pkg_name == 'tests' and
                     os.path.split(parent_dir)[1] == 'pygame')
    if not is_pygame_pkg:
        sys.path.insert(0, parent_dir)
else:
    is_pygame_pkg = __name__.startswith('pygame.tests.')

if is_pygame_pkg:
    from pygame.tests.test_utils import test_not_implemented, unittest
else:
    from test.test_utils import test_not_implemented, unittest

from pygame import mask
# Stuff needed for tests
from pygame import surface
from pygame.locals import SRCALPHA

################################################################################

class MaskTestModule(unittest.TestCase):

    def test_from_surface(self):
        surf = surface.Surface((300, 100), depth=32, flags=SRCALPHA)
        surf.fill((0, 0, 0, 0xff))
        for x in range(200):
            surf.set_at((x, 20), (0, 0, 0, x))
        M = mask.from_surface(surf)
        self.assertEqual(M.get_at((0, 0)), 1)
        self.assertEqual(M.get_at((20, 20)), 0)
        self.assertEqual(M.get_at((21, 20)), 0)
        self.assertEqual(M.get_at((50, 20)), 0)
        self.assertEqual(M.get_at((127, 20)), 0)
        self.assertEqual(M.get_at((128, 20)), 1)
        self.assertEqual(M.get_at((129, 20)), 1)
        self.assertEqual(M.get_at((200, 20)), 1)
        self.assertEqual(M.get_at((21, 21)), 1)
        # Different threshold

        M = mask.from_surface(surf, 50)
        self.assertEqual(M.get_at((50, 20)), 0)
        self.assertEqual(M.get_at((51, 20)), 1)
        self.assertEqual(M.get_at((127, 20)), 1)
        self.assertEqual(M.get_at((128, 20)), 1)
        self.assertEqual(M.get_at((129, 20)), 1)

    def test_fill_clear(self):
        M = mask.Mask((10, 10))
        M.fill()
        for x in range(10):
            for y in range(10):
                self.assertEqual(M.get_at((x, y)), 1)
        self.assertEqual(M.count(), 100)
        M.clear()
        for x in range(10):
            for y in range(10):
                self.assertEqual(M.get_at((x, y)), 0)
        self.assertEqual(M.count(), 0)
        M.fill()
        for x in range(10):
            for y in range(10):
                self.assertEqual(M.get_at((x, y)), 1)

    def test_count(self):
        # More complex count test
        M = mask.Mask((10, 10))
        M.fill()
        self.assertEqual(M.count(), 100)
        # set half the pixels to 0
        for x in range(10):
            for y in range(5):
                M.set_at((x, y), 0)
        self.assertEqual(M.count(), 50)
        for x in range(5):
            for y in range(10):
                M.set_at((x, y), 0)
        self.assertEqual(M.count(), 25)

    def test_centroid(self):
        M = mask.Mask((10, 10))
        M.fill()
        self.assertEqual(M.centroid(), (4,4))
        # set half the pixels to 0
        for x in range(10):
            for y in range(5):
                M.set_at((x, y), 0)
        self.assertEqual(M.centroid(), (4, 7))
        for x in range(5):
            for y in range(10):
                M.set_at((x, y), 0)
        self.assertEqual(M.centroid(), (7, 7))


################################################################################

if __name__ == '__main__':
    unittest.main()
