# The conf_tests module

from .helpers import gen_test_image, test_conformance

from .test_lines import (test_horz_line, test_horz_line_width,
                         test_vert_line, test_vert_line_width,
                         test_lines, test_lines_width,
                         test_lines_function)

from .test_transforms import (test_flip, test_scale, test_rotate)
from .test_shapes import (test_rect, test_polygon)


conformance_tests = {
    'horz1': test_horz_line,
    'horz_widths': test_horz_line_width,
    'vert1': test_vert_line,
    'vert_widths': test_vert_line_width,
    'lines': test_lines,
    'lines_width': test_lines_width,
    'lines_func': test_lines_function,
    'scale': test_scale,
    'flip': test_flip,
    'rotate': test_rotate,
    'rect': test_rect,
    'polygon': test_polygon,
}



__all__ = [conformance_tests, gen_test_image, test_conformance]
