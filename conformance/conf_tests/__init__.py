# The conf_tests module

from .helpers import gen_test_image, test_conformance

from .test_lines import (test_horz_line, test_horz_line_width,
                         test_vert_line, test_vert_line_width,
                         test_lines, test_lines_width,
                         test_lines_function)

from .test_transforms import (test_flip, test_scale, test_rotate)
from .test_shapes import (test_rect, test_polygon)
from .test_surface import test_scroll
from .test_blending import (test_rgba_add, test_rgba_sub, test_rgba_min,
                            test_rgba_max, test_rgba_mult, test_rgb_mult,
                            test_blend_mult)
from .test_smoothscale import (test_int_smoothscale, test_x_smoothscale,
                               test_y_smoothscale, test_varied_smoothscale)

conformance_tests = {
    'test_rgba_add': test_rgba_add,
    'test_rgba_sub': test_rgba_sub,
    'test_rgba_min': test_rgba_min,
    'test_rgba_max': test_rgba_max,
    'test_rgba_mult': test_rgba_mult,
    'test_rgb_mult': test_rgb_mult,
    'test_blend_mult': test_blend_mult,
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
    'scroll': test_scroll,
    'smooth_int': test_int_smoothscale,
    'smooth_x': test_x_smoothscale,
    'smooth_y': test_y_smoothscale,
    'smooth_varies': test_varied_smoothscale,
}



__all__ = [conformance_tests, gen_test_image, test_conformance]
