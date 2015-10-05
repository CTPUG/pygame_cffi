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
from pygame import surface, Rect
from pygame.locals import SRCALPHA

import random

def random_mask(size = (100,100)):
    """random_mask(size=(100,100)): return Mask
    Create a mask of the given size, with roughly half the bits set at random."""
    m = mask.Mask(size)
    for i in range(size[0] * size[1] // 2):
        x, y = random.randint(0,size[0] - 1), random.randint(0, size[1] - 1)
        m.set_at((x,y))
    return m

def maskFromSurface(surface, threshold = 127):
    mask = mask.Mask(surface.get_size())
    key = surface.get_colorkey()
    if key:
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                if surface.get_at((x+0.1,y+0.1)) != key:
                    mask.set_at((x,y),1)
    else:
        for y in range(surface.get_height()):
            for x in range (surface.get_width()):
                if surface.get_at((x,y))[3] > threshold:
                    mask.set_at((x,y),1)
    return mask


################################################################################

class MaskObjectModule(unittest.TestCase):

    def assertMaskEquals(self, m1, m2):
        self.assertEquals(m1.get_size(), m2.get_size())
        for i in range(m1.get_size()[0]):
            for j in range(m1.get_size()[1]):
                self.assertEquals(m1.get_at((i,j)), m2.get_at((i,j)))

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

    def test_angle(self):
        M = mask.Mask((5,5))
        M.clear()
        self.assertEqual(M.angle(), 0.0)
        for x in range(5):
            M.set_at((x, x), 1)
        self.assertEqual(M.angle(), -45.0)
        M.clear()
        for x in range(5):
            M.set_at((x, 4 - x), 1)
        self.assertEqual(M.angle(), 45.0)
        M.clear()
        for x in range(5):
            M.set_at((2, x), 1)
        self.assertEqual(M.angle(), -90.0)
        M.clear()
        for x in range(5):
            M.set_at((x, 2), 1)
        self.assertEqual(M.angle(), 0.0)

    def test_mask_access( self ):
        """ do the set_at, and get_at parts work correctly?
        """
        m = mask.Mask((10,10))
        m.set_at((0,0), 1)
        self.assertEqual(m.get_at((0,0)), 1)
        m.set_at((9,0), 1)
        self.assertEqual(m.get_at((9,0)), 1)

        #s = surface.Surface((10,10))
        #s.set_at((1,0), (0, 0, 1, 255))
        #self.assertEqual(s.get_at((1,0)), (0, 0, 1, 255))
        #s.set_at((-1,0), (0, 0, 1, 255))

        # out of bounds, should get IndexError
        self.assertRaises(IndexError, lambda : m.get_at((-1,0)) )
        self.assertRaises(IndexError, lambda : m.set_at((-1,0), 1) )
        self.assertRaises(IndexError, lambda : m.set_at((10,0), 1) )
        self.assertRaises(IndexError, lambda : m.set_at((0,10), 1) )

    def test_drawing(self):
        """ Test fill, clear, invert, draw, erase
        """

        m = mask.Mask((100,100))
        self.assertEqual(m.count(), 0)

        m.fill()
        self.assertEqual(m.count(), 10000)

        m2 = mask.Mask((10,10))
        m2.fill()
        m.erase(m2, (50,50))
        self.assertEqual(m.count(), 9900)

        m.invert()
        self.assertEqual(m.count(), 100)

        m.draw(m2, (0,0))
        self.assertEqual(m.count(), 200)

        m.clear()
        self.assertEqual(m.count(), 0)

    def test_outline(self):
        """
        """

        m = mask.Mask((20,20))
        self.assertEqual(m.outline(), [])

        m.set_at((10,10), 1)
        self.assertEqual(m.outline(), [(10,10)])

        m.set_at((10,12), 1)
        self.assertEqual(m.outline(10), [(10,10)])

        m.set_at((11,11), 1)
        self.assertEqual(m.outline(), [(10,10), (11,11), (10,12), (11,11), (10,10)])
        self.assertEqual(m.outline(2), [(10,10), (10,12), (10,10)])

        m.clear()
        m.set_at((19, 19), 1)
        self.assertEqual(m.outline(), [(19,19)])
        m.clear()

        # square object in the mask
        m2 = mask.Mask((5,5))
        m2.fill()
        m.draw(m2, (5, 5))
        self.assertEqual(m.outline(), [(5, 5), (6, 5), (7, 5), (8, 5), (9, 5),
                                       (9, 6), (9, 7), (9, 8), (9, 9),
                                       (8, 9), (7, 9), (6, 9), (5, 9),
                                       (5, 8), (5, 7), (5, 6), (5, 5)])
        self.assertEqual(m.outline(2), [(5, 5), (7, 5), (9, 5),
                                        (9, 7), (9, 9),
                                        (7, 9), (5, 9),
                                        (5, 7), (5, 5)])

        # Take out some centre pixels, for no effect
        old_outline = m.outline()
        m.set_at((7, 7), 0)
        m.set_at((7, 8), 0)
        m.set_at((8, 7), 0)
        self.assertEqual(m.outline(), old_outline)

        # Take out some edge pixels from the square
        m.set_at((6, 5), 0)
        m.set_at((7, 5), 0)
        m.set_at((8, 5), 0)
        self.assertEqual(m.outline(), [(5, 5), (6, 6), (7, 6), (8, 6), (9, 5),
                                       (9, 6), (9, 7), (9, 8), (9, 9),
                                       (8, 9), (7, 9), (6, 9), (5, 9),
                                       (5, 8), (5, 7), (5, 6), (5, 5)])

        #TODO: Test more corner case outlines.

    def test_convolve__size(self):
        sizes = [(1,1), (31,31), (32,32), (100,100)]
        for s1 in sizes:
            m1 = mask.Mask(s1)
            for s2 in sizes:
                m2 = mask.Mask(s2)
                o = m1.convolve(m2)
                for i in (0,1):
                    self.assertEquals(o.get_size()[i], m1.get_size()[i] + m2.get_size()[i] - 1)

    def test_convolve__point_identities(self):
        """Convolving with a single point is the identity, while convolving a point with something flips it."""
        m = random_mask((100,100))
        k = mask.Mask((1,1))
        k.set_at((0,0))

        self.assertMaskEquals(m,m.convolve(k))
        self.assertMaskEquals(m,k.convolve(k.convolve(m)))

    def test_convolve__with_output(self):
        """checks that convolution modifies only the correct portion of the output"""

        m = random_mask((10,10))
        k = mask.Mask((2,2))
        k.set_at((0,0))

        o = mask.Mask((50,50))
        test = mask.Mask((50,50))

        m.convolve(k,o)
        test.draw(m,(1,1))
        self.assertMaskEquals(o, test)

        o.clear()
        test.clear()

        m.convolve(k,o, (10,10))
        test.draw(m,(11,11))
        self.assertMaskEquals(o, test)

    def test_convolve__out_of_range(self):
        full = mask.Mask((2,2))
        full.fill()

        self.assertEquals(full.convolve(full, None, ( 0,  3)).count(), 0)
        self.assertEquals(full.convolve(full, None, ( 0,  2)).count(), 3)
        self.assertEquals(full.convolve(full, None, (-2, -2)).count(), 1)
        self.assertEquals(full.convolve(full, None, (-3, -3)).count(), 0)

    def test_convolve(self):
        """Tests the definition of convolution"""
        m1 = random_mask((100,100))
        m2 = random_mask((100,100))
        conv = m1.convolve(m2)

        for i in range(conv.get_size()[0]):
            for j in range(conv.get_size()[1]):
                self.assertEquals(conv.get_at((i,j)) == 0,
                                  m1.overlap(m2, (i - 99, j - 99)) is None)

    def test_overlap_area_mask(self):
        M1 = mask.Mask((10, 10))
        M2 = mask.Mask((10, 10))
        M1.fill()
        M2.fill()

        self.assertEqual(M1.overlap_area(M2, (0, 0)), 100)
        self.assertEqual(M1.overlap_mask(M2, (0, 0)).count(), 100)
        self.assertEqual(M1.overlap_area(M2, (3, 3)), 49)
        self.assertEqual(M1.overlap_mask(M2, (3, 3)).count(), 49)
        self.assertEqual(M2.overlap_area(M1, (3, 3)), 49)
        self.assertEqual(M2.overlap_mask(M1, (3, 3)).count(), 49)
        for x in range(5):
            for y in range(10):
                M2.set_at((x, y), 0)
        self.assertEqual(M1.overlap_area(M2, (0, 0)), 50)
        self.assertEqual(M1.overlap_mask(M2, (0, 0)).count(), 50)
        self.assertEqual(M1.overlap_area(M2, (3, 3)), 14)
        self.assertEqual(M1.overlap_mask(M2, (3, 3)).count(), 14)
        for test in range(10):
            M1 = random_mask((20, 20))
            M2 = random_mask((20, 20))
            self.assertEqual(M1.overlap_area(M2, (0, 0)),
                             M1.overlap_mask(M2, (0, 0)).count())
            self.assertEqual(M1.overlap_area(M2, (4, 4)),
                             M1.overlap_mask(M2, (4, 4)).count())

    def test_connected_components(self):
        """
        """

        m = mask.Mask((10,10))
        self.assertEquals(repr(m.connected_components()), "[]")

        comp = m.connected_component()
        self.assertEquals(m.count(), comp.count())

        m.set_at((0,0), 1)
        m.set_at((1,1), 1)
        comp = m.connected_component()
        comps = m.connected_components()
        comps1 = m.connected_components(1)
        comps2 = m.connected_components(2)
        comps3 = m.connected_components(3)
        self.assertEquals(comp.count(), comps[0].count())
        self.assertEquals(comps1[0].count(), 2)
        self.assertEquals(comps2[0].count(), 2)
        self.assertEquals(repr(comps3), "[]")

        m.set_at((9, 9), 1)
        comp = m.connected_component()
        comp1 = m.connected_component((1, 1))
        comp2 = m.connected_component((2, 2))
        comps = m.connected_components()
        comps1 = m.connected_components(1)
        comps2 = m.connected_components(2)
        comps3 = m.connected_components(3)
        self.assertEquals(comp.count(), 2)
        self.assertEquals(comp1.count(), 2)
        self.assertEquals(comp2.count(), 0)
        self.assertEquals(len(comps), 2)
        self.assertEquals(len(comps1), 2)
        self.assertEquals(len(comps2), 1)
        self.assertEquals(len(comps3), 0)


    def test_get_bounding_rects(self):
        """
        """

        m = mask.Mask((10,10))
        m.set_at((0,0), 1)
        m.set_at((1,0), 1)

        m.set_at((0,1), 1)

        m.set_at((0,3), 1)
        m.set_at((3,3), 1)

        r = m.get_bounding_rects()

        self.assertEquals(repr(r), "[<rect(0, 0, 2, 2)>, <rect(0, 3, 1, 1)>, <rect(3, 3, 1, 1)>]")

        #1100
        #1111
        m = mask.Mask((4,2))
        m.set_at((0,0), 1)
        m.set_at((1,0), 1)
        m.set_at((2,0), 0)
        m.set_at((3,0), 0)

        m.set_at((0,1), 1)
        m.set_at((1,1), 1)
        m.set_at((2,1), 1)
        m.set_at((3,1), 1)

        r = m.get_bounding_rects()
        self.assertEquals(repr(r), "[<rect(0, 0, 4, 2)>]")

        #00100
        #01110
        #00100
        m = mask.Mask((5,3))
        m.set_at((0,0), 0)
        m.set_at((1,0), 0)
        m.set_at((2,0), 1)
        m.set_at((3,0), 0)
        m.set_at((4,0), 0)

        m.set_at((0,1), 0)
        m.set_at((1,1), 1)
        m.set_at((2,1), 1)
        m.set_at((3,1), 1)
        m.set_at((4,1), 0)

        m.set_at((0,2), 0)
        m.set_at((1,2), 0)
        m.set_at((2,2), 1)
        m.set_at((3,2), 0)
        m.set_at((4,2), 0)

        r = m.get_bounding_rects()
        self.assertEquals(repr(r), "[<rect(1, 0, 3, 3)>]")



        #00010
        #00100
        #01000
        m = mask.Mask((5,3))
        m.set_at((0,0), 0)
        m.set_at((1,0), 0)
        m.set_at((2,0), 0)
        m.set_at((3,0), 1)
        m.set_at((4,0), 0)

        m.set_at((0,1), 0)
        m.set_at((1,1), 0)
        m.set_at((2,1), 1)
        m.set_at((3,1), 0)
        m.set_at((4,1), 0)

        m.set_at((0,2), 0)
        m.set_at((1,2), 1)
        m.set_at((2,2), 0)
        m.set_at((3,2), 0)
        m.set_at((4,2), 0)

        r = m.get_bounding_rects()
        self.assertEquals(repr(r), "[<rect(1, 0, 3, 3)>]")




        #00011
        #11111
        m = mask.Mask((5,2))
        m.set_at((0,0), 0)
        m.set_at((1,0), 0)
        m.set_at((2,0), 0)
        m.set_at((3,0), 1)
        m.set_at((4,0), 1)

        m.set_at((0,1), 1)
        m.set_at((1,1), 1)
        m.set_at((2,1), 1)
        m.set_at((3,1), 1)
        m.set_at((3,1), 1)

        r = m.get_bounding_rects()
        #TODO: this should really make one bounding rect.
        #self.assertEquals(repr(r), "[<rect(0, 0, 5, 2)>]")

class MaskModuleTest(unittest.TestCase):

    def test_from_surface(self):
        """  Does the mask.from_surface() work correctly?
        """

        mask_from_surface = mask.from_surface

        surf = surface.Surface((70,70), SRCALPHA, 32)

        surf.fill((255,255,255,255))

        amask = mask.from_surface(surf)
        #amask = mask_from_surface(surf)

        self.assertEqual(amask.get_at((0,0)), 1)
        self.assertEqual(amask.get_at((66,1)), 1)
        self.assertEqual(amask.get_at((69,1)), 1)

        surf.set_at((0,0), (255,255,255,127))
        surf.set_at((1,0), (255,255,255,128))
        surf.set_at((2,0), (255,255,255,0))
        surf.set_at((3,0), (255,255,255,255))

        amask = mask_from_surface(surf)
        self.assertEqual(amask.get_at((0,0)), 0)
        self.assertEqual(amask.get_at((1,0)), 1)
        self.assertEqual(amask.get_at((2,0)), 0)
        self.assertEqual(amask.get_at((3,0)), 1)

        surf.fill((255,255,255,0))
        amask = mask_from_surface(surf)
        self.assertEqual(amask.get_at((0,0)), 0)

        #TODO: test a color key surface.

    def test_from_surface_2(self):
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

    def test_from_threshold(self):
        """ Does mask.from_threshold() work correctly?
        """

        a = [16, 24, 32]

        for i in a:
            surf = surface.Surface((70,70), 0, i)
            surf.fill((100,50,200),(20,20,20,20))
            my_mask = mask.from_threshold(surf,(100,50,200,255),(10,10,10,255))

            self.assertEqual(my_mask.count(), 400)
            self.assertEqual(my_mask.get_bounding_rects(), [Rect((20,20,20,20))])

        for i in a:
            surf = surface.Surface((70,70), 0, i)
            surf2 = surface.Surface((70,70), 0, i)
            surf.fill((100,100,100))
            surf2.fill((150,150,150))
            surf2.fill((100,100,100), (40,40,10,10))
            my_mask = mask.from_threshold(surf, (0,0,0,0), (10,10,10,255), surf2)

            self.assertEqual(my_mask.count(), 100)
            self.assertEqual(my_mask.get_bounding_rects(), [Rect((40,40,10,10))])



################################################################################

if __name__ == '__main__':
    unittest.main()
