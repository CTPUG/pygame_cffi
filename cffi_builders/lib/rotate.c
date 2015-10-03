/*
 This is cut from src/transform.c in pygame

 Original copyright from pygame:

 pygame - Python Game Library
 Copyright (C) 2000-2001  Pete Shinners
 Copyright (C) 2007  Rene Dudfield, Richard Goedeken

 This library is free software; you can redistribute it and/or
 modify it under the terms of the GNU Library General Public
 License as published by the Free Software Foundation; either
 version 2 of the License, or (at your option) any later version.

 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Library General Public License for more details.

 You should have received a copy of the GNU Library General Public
 License along with this library; if not, write to the Free
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 MA  02110-1301  USA

 Pete Shinners
 pete@shinners.org
*/

static void
rotate90 (SDL_Surface *src, SDL_Surface *dst, int angle)
{
    int numturns = (angle / 90) % 4;
    int dstwidth, dstheight;
    char *srcpix, *dstpix, *srcrow, *dstrow;
    int srcstepx, srcstepy, dststepx, dststepy;
    int loopx, loopy;

    dstwidth = dst->w;
    dstheight = dst->h;

    if (numturns < 0)
        numturns = 4 + numturns;

    srcrow = (char*) src->pixels;
    dstrow = (char*) dst->pixels;
    srcstepx = dststepx = src->format->BytesPerPixel;
    srcstepy = src->pitch;
    dststepy = dst->pitch;

    switch (numturns)
    {
    case 1:
        srcrow += ((src->w - 1) * srcstepx);
        srcstepy = -srcstepx;
        srcstepx = src->pitch;
        break;
    case 2:
        srcrow += ((src->h - 1) * srcstepy) + ((src->w - 1) * srcstepx);
        srcstepx = -srcstepx;
        srcstepy = -srcstepy;
        break;
    case 3:
        srcrow += ((src->h - 1) * srcstepy);
        srcstepx = -srcstepy;
        srcstepy = src->format->BytesPerPixel;
        break;
    }

    switch (src->format->BytesPerPixel)
    {
    case 1:
        for (loopy = 0; loopy < dstheight; ++loopy)
        {
            dstpix = dstrow;
            srcpix = srcrow;
            for (loopx = 0; loopx < dstwidth; ++loopx)
            {
                *dstpix = *srcpix;
                srcpix += srcstepx;
                dstpix += dststepx;
            }
            dstrow += dststepy;
            srcrow += srcstepy;
        }
        break;
    case 2:
        for (loopy = 0; loopy < dstheight; ++loopy)
        {
            dstpix = dstrow;
            srcpix = srcrow;
            for (loopx = 0; loopx < dstwidth; ++loopx)
            {
                *(Uint16*)dstpix = *(Uint16*)srcpix;
                srcpix += srcstepx;
                dstpix += dststepx;
            }
            dstrow += dststepy;
            srcrow += srcstepy;
        }
        break;
    case 3:
        for (loopy = 0; loopy < dstheight; ++loopy)
        {
            dstpix = dstrow;
            srcpix = srcrow;
            for (loopx = 0; loopx < dstwidth; ++loopx)
            {
                dstpix[0] = srcpix[0];
                dstpix[1] = srcpix[1];
                dstpix[2] = srcpix[2];
                srcpix += srcstepx;
                dstpix += dststepx;
            }
            dstrow += dststepy;
            srcrow += srcstepy;
        }
        break;
    case 4:
        for (loopy = 0; loopy < dstheight; ++loopy)
        {
            dstpix = dstrow;
            srcpix = srcrow;
            for (loopx = 0; loopx < dstwidth; ++loopx)
            {
                *(Uint32*)dstpix = *(Uint32*)srcpix;
                srcpix += srcstepx;
                dstpix += dststepx;
            }
            dstrow += dststepy;
            srcrow += srcstepy;
        }
        break;
    }
}


static void
rotate (SDL_Surface *src, SDL_Surface *dst, Uint32 bgcolor, double sangle,
        double cangle)
{
    int x, y, dx, dy;

    Uint8 *srcpix = (Uint8*) src->pixels;
    Uint8 *dstrow = (Uint8*) dst->pixels;
    int srcpitch = src->pitch;
    int dstpitch = dst->pitch;

    int cy = dst->h / 2;
    int xd = ((src->w - dst->w) << 15);
    int yd = ((src->h - dst->h) << 15);

    int isin = (int)(sangle * 65536);
    int icos = (int)(cangle * 65536);

    int ax = ((dst->w) << 15) - (int)(cangle * ((dst->w - 1) << 15));
    int ay = ((dst->h) << 15) - (int)(sangle * ((dst->w - 1) << 15));

    int xmaxval = ((src->w) << 16) - 1;
    int ymaxval = ((src->h) << 16) - 1;

    switch (src->format->BytesPerPixel)
    {
    case 1:
        for (y = 0; y < dst->h; y++)
        {
            Uint8 *dstpos = (Uint8*)dstrow;
            dx = (ax + (isin * (cy - y))) + xd;
            dy = (ay - (icos * (cy - y))) + yd;
            for (x = 0; x < dst->w; x++)
            {
                if(dx < 0 || dy < 0 || dx > xmaxval || dy > ymaxval)
                    *dstpos++ = bgcolor;
                else
                    *dstpos++ = *(Uint8*)
                        (srcpix + ((dy >> 16) * srcpitch) + (dx >> 16));
                dx += icos;
                dy += isin;
            }
            dstrow += dstpitch;
        }
        break;
    case 2:
        for (y = 0; y < dst->h; y++)
        {
            Uint16 *dstpos = (Uint16*)dstrow;
            dx = (ax + (isin * (cy - y))) + xd;
            dy = (ay - (icos * (cy - y))) + yd;
            for (x = 0; x < dst->w; x++)
            {
                if (dx < 0 || dy < 0 || dx > xmaxval || dy > ymaxval)
                    *dstpos++ = bgcolor;
                else
                    *dstpos++ = *(Uint16*)
                        (srcpix + ((dy >> 16) * srcpitch) + (dx >> 16 << 1));
                dx += icos;
                dy += isin;
            }
            dstrow += dstpitch;
        }
        break;
    case 4:
        for (y = 0; y < dst->h; y++)
        {
            Uint32 *dstpos = (Uint32*)dstrow;
            dx = (ax + (isin * (cy - y))) + xd;
            dy = (ay - (icos * (cy - y))) + yd;
            for (x = 0; x < dst->w; x++)
            {
                if (dx < 0 || dy < 0 || dx > xmaxval || dy > ymaxval)
                    *dstpos++ = bgcolor;
                else
                    *dstpos++ = *(Uint32*)
                        (srcpix + ((dy >> 16) * srcpitch) + (dx >> 16 << 2));
                dx += icos;
                dy += isin;
            }
            dstrow += dstpitch;
        }
        break;
    default: /*case 3:*/
        for (y = 0; y < dst->h; y++)
        {
            Uint8 *dstpos = (Uint8*)dstrow;
            dx = (ax + (isin * (cy - y))) + xd;
            dy = (ay - (icos * (cy - y))) + yd;
            for (x = 0; x < dst->w; x++)
            {
                if (dx < 0 || dy < 0 || dx > xmaxval || dy > ymaxval)
                {
                    dstpos[0] = ((Uint8*) &bgcolor)[0];
                    dstpos[1] = ((Uint8*) &bgcolor)[1];
                    dstpos[2] = ((Uint8*) &bgcolor)[2];
                    dstpos += 3;
                }
                else
                {
                    Uint8* srcpos = (Uint8*)
                        (srcpix + ((dy >> 16) * srcpitch) + ((dx >> 16) * 3));
                    dstpos[0] = srcpos[0];
                    dstpos[1] = srcpos[1];
                    dstpos[2] = srcpos[2];
                    dstpos += 3;
                }
                dx += icos; dy += isin;
            }
            dstrow += dstpitch;
        }
        break;
    }
}
