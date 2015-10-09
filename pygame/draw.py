from pygame.surface import locked
from pygame.color import create_color
from pygame.compat import xrange_
from pygame.rect import Rect
from pygame._sdl import sdl, ffi
import pygame.surface

import math


def _check_surface(surface):
    if not isinstance(surface, pygame.surface.Surface):
        raise TypeError("First argument must be a Surface.")
    # TODO: depth check.


def _check_point(point, msg="points must be number pairs"):
    if not (hasattr(point, '__iter__') and len(point) == 2
            and all(isinstance(p, int) for p in point)):
        raise TypeError(msg)
    return point


def _check_and_filter_points(points, minlen=1):
    if not hasattr(points, '__iter__'):
        raise TypeError("points argument must be a sequence of number pairs")

    if len(points) < minlen:
        raise ValueError("points argument must contain %s or more points" % (
            minlen,))

    _check_point(points[0])

    filtered = []
    for point in points:
        try:
            x, y = _check_point(point)
        except TypeError:
            # Silently skip over bad points, because pygame does. :-(
            continue
        filtered.append((x, y))
    return filtered


def _make_drawn_rect(points, surface):
    rect = surface.get_clip()
    left = max(rect.left, min(p[0] for p in points))
    right = min(rect.right, max(p[0] for p in points))
    top = max(rect.top, min(p[1] for p in points))
    bottom = min(rect.bottom, max(p[1] for p in points))
    return Rect(left, top, right - left + 1, bottom - top + 1)


_CLIP_LEFT = 1
_CLIP_RIGHT = 2
_CLIP_TOP = 4
_CLIP_BOTTOM = 8


def _outcode(rect, x, y):
    code = 0
    if x < rect.left:
        code |= _CLIP_LEFT
    elif x >= rect.right:
        code |= _CLIP_RIGHT
    if y < rect.top:
        code |= _CLIP_TOP
    elif y >= rect.bottom:
        code |= _CLIP_BOTTOM
    return code


def _clipline(rect, start, end):
    # Cohen-Sutherland algorithm
    x0, y0 = start
    x1, y1 = end

    left = rect.left
    right = rect.right - 1
    top = rect.top
    bottom = rect.bottom - 1

    out0 = _outcode(rect, x0, y0)
    out1 = _outcode(rect, x1, y1)

    while True:
        if not (out0 | out1):
            return (x0, y0), (x1, y1)
        elif (out0 & out1):
            return None, None

        if not out0:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
            out0, out1 = out1, out0

        m = 1.0
        if x0 != x1:
            m = float(y1 - y0) / float(x1 - x0)

        if out0 & _CLIP_LEFT:
            y0 += int(m * (left - x0))
            x0 = left

        elif out0 & _CLIP_RIGHT:
            y0 += int(m * (right - x0))
            x0 = right

        elif out0 & _CLIP_TOP:
            if x0 != x1:
                x0 += int((top - y0) / m)
            y0 = top

        elif out0 & _CLIP_BOTTOM:
            if x0 != x1:
                x0 += int((bottom - y0) / m)
            y0 = bottom

        out0 = _outcode(rect, x0, y0)


def _drawhorizline(surface, c_color, start_x, end_x, y):
    """Draw a horizontal line using SDL_FillRect"""
    sdlrect = ffi.new('SDL_Rect*')
    if start_x > end_x:
        end_x, start_x = start_x, end_x
    sdlrect.x = start_x
    sdlrect.y = y
    sdlrect.w = end_x - start_x + 1
    sdlrect.h = 1
    sdl.SDL_FillRect(surface._c_surface, sdlrect, c_color)


def _drawvertline(surface, c_color, start_y, end_y, x):
    """Draw a vertical line using SDL_FillRect"""
    sdlrect = ffi.new('SDL_Rect*')
    if start_y > end_y:
        end_y, start_y = start_y, end_y
    sdlrect.x = x
    sdlrect.y = start_y
    sdlrect.w = 1
    sdlrect.h = end_y - start_y + 1
    sdl.SDL_FillRect(surface._c_surface, sdlrect, c_color)


def _drawline(surface, c_color, start, end):
    # Bresenham algorithm (more or less as approximated by pygame)
    x0, y0 = start
    x1, y1 = end

    if x0 == x1:
        _drawvertline(surface, c_color, y0, y1, x0)
        return
    if y0 == y1:
        _drawhorizline(surface, c_color, x0, x1, y0)
        return

    # Because of how we approximate pygame's pointer
    # arthimetic, we don't handle the ends of the lines
    # the same way - this fakes it
    surface._set_at(x0, y0, c_color)
    surface._set_at(x1, y1, c_color)
    steep = False
    if abs(y1 - y0) > abs(x1 - x0):
        steep = True
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    dx = abs(x1 - x0) + 1
    dy = abs(y1 - y0) + 1
    ystep = 1 if y0 < y1 else -1
    xstep = 1 if x0 < x1 else -1
    y = y0
    error = 0
    for x in range(x0, x1, xstep):
        if steep:
            surface._set_at(y, x, c_color)
        else:
            surface._set_at(x, y, c_color)
        error = error + dy
        if error >= dx:
            y += ystep
            error -= dx


def _clip_and_draw_line(surface, c_color, start, end):
    # rect = surface.get_clip().inflate(-60, -60)
    # start, end = _clipline(rect, start, end)
    start, end = _clipline(surface.get_clip(), start, end)
    if start is None:
        return False

    _drawline(surface, c_color, start, end)
    return True


def _clip_and_draw_line_width(surface, c_color, width, start, end):
    x0, y0 = start
    x1, y1 = end

    xinc = yinc = 0
    if abs(x1 - x0) > abs(y1 - y0):
        yinc = 1
    else:
        xinc = 1

    # XXX: Instead of getting the minimum and maximum for each direction (which
    #      we do here), pygame gets the minimum of the start coords and the
    #      maximum of the end coords. I think we're right, but we should maybe
    #      match what pygame does instead even though it's more of a pain to
    #      implement.

    points = set()
    p0 = (x0, y0)
    p1 = (x1, y1)
    if _clip_and_draw_line(surface, c_color, p0, p1):
        points.update((p0, p1))

    for i in xrange_(width // 2):
        p0 = (x0 + xinc * (i + 1), y0 + yinc * (i + 1))
        p1 = (x1 + xinc * (i + 1), y1 + yinc * (i + 1))
        if _clip_and_draw_line(surface, c_color, p0, p1):
            points.update((p0, p1))
        # When the width is odd, we only draw the +xinc case
        # on the last pass through the loop
        if (2 * i + 2 < width):
            p0 = (x0 - xinc * (i + 1), y0 - yinc * (i + 1))
            p1 = (x1 - xinc * (i + 1), y1 - yinc * (i + 1))
            if _clip_and_draw_line(surface, c_color, p0, p1):
                points.update((p0, p1))

    if points:
        # points would be empty if nothing was drawn
        return _make_drawn_rect(points, surface)
    return None


def line(surface, color, start, end, width=1):
    _check_surface(surface)
    c_color = create_color(color, surface._format)

    _check_point(start, "Invalid start position argument")
    _check_point(end, "Invalid end position argument")

    [start] = _check_and_filter_points([start])
    [end] = _check_and_filter_points([end])

    if width < 1:
        return Rect(start, (0, 0))

    with locked(surface._c_surface):
        drawn = _clip_and_draw_line_width(surface, c_color, width, start, end)

    if drawn is None:
        return Rect(start, (0, 0))
    return drawn


def lines(surface, color, closed, points, width=1):
    _check_surface(surface)
    c_color = create_color(color, surface._format)
    points = _check_and_filter_points(points, 2)
    drawn_points = set()

    with locked(surface._c_surface):
        start_point = points[0]
        for point in points[1:]:
            drawn = _clip_and_draw_line_width(
                surface, c_color, width, start_point, point)
            if drawn is not None:
                drawn_points.add(drawn.topleft)
                drawn_points.add(drawn.bottomright)
            start_point = point

        if closed and len(points) > 2:
            _clip_and_draw_line_width(
                surface, c_color, width, points[-1], points[0])

    if drawn_points:
        # points would be empty if nothing was drawn
        return _make_drawn_rect(drawn_points, surface)
    return None


def _draw_fillpoly(surface, points, c_color):
    # Very traditional scanline fill approach
    # (also the approach used by pygame)
    ys = [p[1] for p in points]
    miny = min(ys)
    maxy = max(ys)
    times = []
    # For speed reasons, we integrate clipping into the calculations,
    # rather than calling _clip_and_draw_line
    clip_rect = surface.get_clip()
    all_points = list(zip(points, points[-1:] + points[:-1]))
    for y in range(miny, maxy + 1):
        if y < clip_rect.top or y >= clip_rect.bottom:
            continue
        intercepts = []
        for p1, p2 in all_points:
            if p1[1] == p2[1]:
                # Edge of the polygon, so skip (due to division by 0)
                continue
            elif p1[1] < p2[1]:
                x1, y1 = p1
                x2, y2 = p2
            else:
                x1, y1 = p2
                x2, y2 = p1

            if not (y1 <= y < y2) and not (y == maxy and y1 < y <= y2):
                continue
            # XXX: Here be dragons with very sharp teeth
            # C99 specifies truncates integer division towards zero always,
            # python integer division takes the floor, so they differ
            # on negatives
            numerator = (y - y1) * (x2 - x1)
            if numerator < 0:
                # N.B. order matters - force the postive division before
                # multiplication by -1
                x = -1 * (-numerator // (y2 - y1)) + x1
            else:
                x = numerator // (y2 - y1) + x1
            # This works because we're drawing horizontal lines
            if x < clip_rect.left:
                x = clip_rect.left
            elif x >= clip_rect.right:
                x = clip_rect.right - 1
            intercepts.append(x)
        intercepts.sort()
        for x1, x2 in zip(intercepts[::2], intercepts[1::2]):
            _drawhorizline(surface, c_color, x1, x2, y)


def polygon(surface, color, points, width=0):
    _check_surface(surface)

    if width != 0:
        return lines(surface, color, 1, points, width)

    c_color = create_color(color, surface._format)
    points = _check_and_filter_points(points, 3)

    with locked(surface._c_surface):
        _draw_fillpoly(surface, points, c_color)

    return _make_drawn_rect(points, surface)


def rect(surface, color, rect, width=0):
    if not isinstance(surface, pygame.surface.Surface):
        raise TypeError("First argument must be a Surface.")

    rect = Rect(rect)
    l = rect.x
    r = rect.x + rect.w - 1
    t = rect.y
    b = rect.y + rect.h - 1

    points = ((l, t), (r, t), (r, b), (l, b))
    return polygon(surface, color, points, width)


def circle(surface, color, pos, radius, width=0):
    """pygame.draw.circle(Surface, color, pos, radius, width=0): return Rect

       draw a circle around a point"""
    if radius < 0:
        raise ValueError("negative radius")
    if width < 0:
        raise ValueError("negative width")
    if radius < width:
        raise ValueError("width greater than radius")

    if not width:
        _fillellipse(surface, pos, radius, radius, color)
    else:
        for loop in range(0, width):
            _ellipse(surface, pos, radius - loop, radius - loop, color)

    corners = ((pos[0] + radius, pos[1] + radius),
               (pos[0] - radius, pos[1] + radius),
               (pos[0] + radius, pos[1] - radius),
               (pos[0] - radius, pos[1] - radius))

    return _make_drawn_rect(corners, surface)


def ellipse(surface, color, rect, width=0):
    """pygame.draw.ellipse(Surface, color, Rect, width=0): return Rect

       draw a round shape inside a rectangle"""
    rect = Rect(rect)

    pos = (rect.x + rect.w // 2, rect.y + rect.h // 2)
    radius_x = rect.w // 2
    radius_y = rect.h // 2

    if not width:
        _fillellipse(surface, pos, radius_x, radius_y, color)
    else:
        width = min(width, rect.w // 2, rect.h // 2)
        for loop in range(0, width):
            _ellipse(surface, pos, radius_x - loop, radius_y - loop, color)

    corners = (rect.topleft, rect.topright, rect.bottomleft, rect.bottomright)
    return _make_drawn_rect(corners, surface)


def _c_div(x, y):
    """Fake C division semantics"""
    if x < 0:
        return int(math.ceil(float(x) / y))
    else:
        return x // y


def _ellipse(surface, pos, radius_x, radius_y, color):
    """Internal helper function

       draw a ellipse with line thickness 1 on surface."""
    c_surf = surface._c_surface
    c_x, c_y = pos
    c_color = create_color(color, surface._format)
    if _check_special_ellipse(surface, c_x, c_y, radius_x, radius_y, c_color):
        return
    # Draw the ellipse
    # Pygame's ellipse drawing algorithm appears to come from allegro, via sge
    # and SDL_gfxPrimitives. It's known to be non-optimal, but we're aiming
    # for pygame compatibility, so we're doing the same thing, much as
    # it grates me to do so.
    # We assume suitable diligence in terms of the licensing, but allegro's
    # zlib'ish license should mean we're OK anyway.

    stop_h = stop_i = stop_j = stop_k = -1
    bounds = surface.get_bounding_rect()

    with locked(c_surf):
        i = 1
        h = 0
        if radius_x > radius_y:
            ix = 0
            iy = radius_x * 64
            while i > h:
                h = (ix + 16) // 64
                i = (iy + 16) // 64
                j = (h * radius_y) // radius_x
                k = (i * radius_y) // radius_x

                if (stop_k != k and stop_j != k) or (stop_j != j and stop_k != k) or (k != j):
                    plus_x = c_x + h - 1
                    minus_x = c_x - h
                    if k > 0:
                        plus_y = c_y + k - 1
                        minus_y = c_y - k
                        if h > 0:
                            if bounds.collidepoint(minus_x, plus_y):
                                surface._set_at(minus_x, plus_y, c_color)
                            if bounds.collidepoint(minus_x, minus_y):
                                surface._set_at(minus_x, minus_y, c_color)
                        if bounds.collidepoint(plus_x, plus_y):
                            surface._set_at(plus_x, plus_y, c_color)
                        if bounds.collidepoint(plus_x, minus_y):
                            surface._set_at(plus_x, minus_y, c_color)
                    stop_k = k
                    plus_x = c_x + i - 1
                    minus_x = c_x - i
                    if j > 0:
                        plus_y = c_y + j - 1
                        minus_y = c_y - j
                        if bounds.collidepoint(plus_x, plus_y):
                            surface._set_at(plus_x, plus_y, c_color)
                        if bounds.collidepoint(plus_x, minus_y):
                            surface._set_at(plus_x, minus_y, c_color)
                        if bounds.collidepoint(minus_x, plus_y):
                            surface._set_at(minus_x, plus_y, c_color)
                        if bounds.collidepoint(minus_x, minus_y):
                            surface._set_at(minus_x, minus_y, c_color)
                    stop_j = j
                ix = ix + _c_div(iy, radius_x)
                iy = iy - _c_div(ix, radius_x)
        else:
            ix = 0
            iy = radius_y * 64
            while i > h:
                h = (ix + 32) // 64
                i = (iy + 32) // 64
                j = (h * radius_x) // radius_y
                k = (i * radius_x) // radius_y

                if (stop_i != i and stop_h != i) or (stop_i != h and stop_h != h) or (h != i):
                    plus_x = c_x + j - 1
                    minus_x = c_x - j
                    if i > 0:
                        plus_y = c_y + i - 1
                        minus_y = c_y - i
                        if j > 0:
                            if bounds.collidepoint(minus_x, plus_y):
                                surface._set_at(minus_x, plus_y, c_color)
                            if bounds.collidepoint(minus_x, minus_y):
                                surface._set_at(minus_x, minus_y, c_color)
                        if bounds.collidepoint(plus_x, plus_y):
                            surface._set_at(plus_x, plus_y, c_color)
                        if bounds.collidepoint(plus_x, minus_y):
                            surface._set_at(plus_x, minus_y, c_color)
                    stop_i = i
                    plus_x = c_x + k - 1
                    minus_x = c_x - k
                    if h > 0:
                        plus_y = c_y + h - 1
                        minus_y = c_y - h
                        if bounds.collidepoint(plus_x, plus_y):
                            surface._set_at(plus_x, plus_y, c_color)
                        if bounds.collidepoint(plus_x, minus_y):
                            surface._set_at(plus_x, minus_y, c_color)
                        if bounds.collidepoint(minus_x, plus_y):
                            surface._set_at(minus_x, plus_y, c_color)
                        if bounds.collidepoint(minus_x, minus_y):
                            surface._set_at(minus_x, minus_y, c_color)
                    stop_h = h
                ix = ix + _c_div(iy, radius_y)
                iy = iy - _c_div(ix, radius_y)


def _fillellipse(surface, pos, radius_x, radius_y, color):
    """Internal helper function

       draw a filled ellipse on surface."""
    c_surf = surface._c_surface
    c_x, c_y = pos
    c_color = create_color(color, surface._format)
    if _check_special_ellipse(surface, c_x, c_y, radius_x, radius_y, c_color):
        return
    # Draw the filled ellipse
    # We inherit this structure from pygame
    # We draw by drawing horizontal lines between points, while _ellipse
    # is orientated towards creating vertical pairs.
    # There are also some annoying other differences between how
    # the filled ellipse and hollow ellipse are constructed that makes it
    # hard to do both in a single function
    # Why, pygame, why?

    stop_h = stop_i = stop_j = stop_k = -1

    with locked(c_surf):
        i = 1
        h = 0
        if radius_x > radius_y:
            ix = 0
            iy = radius_x * 64
            while i > h:
                h = (ix + 8) // 64
                i = (iy + 8) // 64
                j = (h * radius_y) // radius_x
                k = (i * radius_y) // radius_x

                if stop_k != k and stop_j != k and k < radius_y:
                    _drawhorizline(surface, c_color,
                                   c_x - h, c_x + h - 1, c_y - k - 1)
                    _drawhorizline(surface, c_color,
                                   c_x - h, c_x + h - 1, c_y + k)
                    stop_k = k
                if stop_j != j and stop_k != j and k != j:
                    _drawhorizline(surface, c_color,
                                   c_x - i, c_x + i - 1, c_y - j - 1)
                    _drawhorizline(surface, c_color,
                                   c_x - i, c_x + i - 1, c_y + j)
                    stop_j = j
                ix = ix + _c_div(iy, radius_x)
                iy = iy - _c_div(ix, radius_x)
        else:
            ix = 0
            iy = radius_y * 64
            while i > h:
                h = (ix + 8) // 64
                i = (iy + 8) // 64
                j = (h * radius_x) // radius_y
                k = (i * radius_x) // radius_y

                if stop_i != i and stop_h != i and i < radius_y:
                    _drawhorizline(surface, c_color,
                                   c_x - j, c_x + j - 1, c_y - i - 1)
                    _drawhorizline(surface, c_color,
                                   c_x - j, c_x + j - 1, c_y + i)
                    stop_i = i
                if stop_h != h and stop_i != h and i != h:
                    _drawhorizline(surface, c_color,
                                   c_x - k, c_x + k - 1, c_y - h - 1)
                    _drawhorizline(surface, c_color,
                                   c_x - k, c_x + k - 1, c_y + h)
                    stop_h = h

                ix = ix + _c_div(iy, radius_y)
                iy = iy - _c_div(ix, radius_y)


def _check_special_ellipse(surface, c_x, c_y, radius_x, radius_y, c_color):
    if radius_x == 0 and radius_y == 0:
        with locked(surface._c_surface):
            surface._set_at(c_x, c_y, c_color)
        return True
    elif radius_x == 0:
        # vertical line
        _drawvertline(surface, c_color, c_y - radius_y, c_y + radius_y, c_x)
        return True
    elif radius_y == 0:
        _drawhorizline(surface, c_color, c_x - radius_x, c_x + radius_x, c_y)
        return True
    return False
