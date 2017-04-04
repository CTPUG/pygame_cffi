# The conf_tests module
# Copyright (C) 2014  Neil Muller
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301  USA

from .helpers import gen_test_image, test_conformance

from .test_lines import (test_horz_line, test_horz_line_width,
                         test_vert_line, test_vert_line_width,
                         test_lines, test_lines_width,
                         test_lines_function)

from .test_transforms import (test_flip, test_scale, test_rotate, test_chop,
                              test_rotozoom, test_flip_subsurface,
                              test_chop_subsurface)
from .test_shapes import (test_rect, test_polygon, test_hollow_circles,
                          test_filled_circles, test_filled_ellipses_1,
                          test_filled_ellipses_2, test_hollow_ellipses,
                          test_filled_circles_limits)
from .test_surface import test_scroll
from .test_blending import (test_rgba_add, test_rgba_sub, test_rgba_min,
                            test_rgba_max, test_rgba_mult, test_rgb_mult,
                            test_blend_mult)
from .test_smoothscale import (test_int_smoothscale, test_x_smoothscale,
                               test_y_smoothscale, test_varied_smoothscale,
                               test_subsurface_smoothscale)

conformance_tests = [
        test_horz_line,
        test_horz_line_width,
        test_vert_line,
        test_vert_line_width,
        test_lines,
        test_lines_width,
        test_lines_function,
        test_subsurface_smoothscale,
        test_varied_smoothscale,
        test_y_smoothscale,
        test_x_smoothscale,
        test_int_smoothscale,
        test_filled_circles_limits,
        test_hollow_ellipses,
        test_filled_ellipses_1,
        test_filled_ellipses_2,
        test_filled_circles,
        test_hollow_circles,
        test_rect,
        test_polygon,
        test_scroll,
        test_rgba_add,
        test_rgba_sub,
        test_rgba_min,
        test_rgba_max,
        test_rgba_mult,
        test_rgb_mult,
        test_blend_mult,
        test_rotozoom,
        test_scale,
        test_flip,
        test_flip_subsurface,
        test_rotate,
        test_chop,
        test_chop_subsurface,
]


__all__ = [conformance_tests, gen_test_image, test_conformance]
