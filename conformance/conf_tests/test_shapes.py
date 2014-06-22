# Test lines

from pygame import draw, rect

def test_rect(test_surf):
   """Draw several rectangles."""
   for y in range(10, 200, 45):
       x = 10
       for width in range(10, 30, 3):
           for height in range(10, 40, 7):
               r = rect.Rect(x, y, width, height)
               x += width + 2
               draw.rect(test_surf, (255, 255, 255, 255), r)


def test_polygon(test_surf):
   """Draw several polygons."""
   # triangle
   draw.polygon(test_surf, (255, 255, 255, 255), [(10, 10), (30, 30),
                                                  (45, 30)])
   draw.polygon(test_surf, (255, 0, 255, 255), [(50, 10), (80, 30), (95, 20)],
                3)
   # overlap
   draw.polygon(test_surf, (255, 0, 128, 255), [(50, 15), (80, 25), (105, 25)],
                0)
   # square
   draw.polygon(test_surf, (255, 255, 255, 255), [(150, 10), (150, 50),
                                                  (190, 50), (190, 10)])
   draw.polygon(test_surf, (0, 255, 255, 255), [(220, 10), (220, 50),
                                                (260, 50), (260, 10)], 1)
   # hexagon
   draw.polygon(test_surf, (0, 0, 255, 255), [(310, 10), (320, 25), (320, 50),
                                              (310, 65), (300, 50), (300, 25)])
   # Funky
   draw.polygon(test_surf, (255, 255, 255, 255), [(246,134), (268, 146),
                                                  (262, 144), (271, 81),
                                                  (204, 116), (243, 102),
                                                  (275, 150), (234, 82),
                                                  (231, 94), (217, 134),
                                                  (212, 99), (237, 96)], 2)
   draw.polygon(test_surf, (255, 255, 255, 255), [(369, 158), (342, 193),
                                                  (319, 205), (316, 217),
                                                  (356, 183), (312, 169),
                                                  (333, 212), (358, 200),
                                                  (310, 168), (301, 151),
                                                  (300, 145), (307, 214)], 0)
