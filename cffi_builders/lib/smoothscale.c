
/*
 smooth scale functions.

 This is largely from src/transform.c in pygame

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


/* this function implements an area-averaging shrinking filter in the X-dimension */
static void filter_shrink_X(Uint8 *srcpix, Uint8 *dstpix, int height, int srcpitch, int dstpitch, int srcwidth, int dstwidth)
{
    int srcdiff = srcpitch - (srcwidth * 4);
    int dstdiff = dstpitch - (dstwidth * 4);
    int x, y;

    int xspace = 0x10000 * srcwidth / dstwidth; /* must be > 1 */
    int xrecip = (int) (0x100000000LL / xspace);
    for (y = 0; y < height; y++)
    {
        Uint16 accumulate[4] = {0,0,0,0};
        int xcounter = xspace;
        for (x = 0; x < srcwidth; x++)
        {
            if (xcounter > 0x10000)
            {
                accumulate[0] += (Uint16) *srcpix++;
                accumulate[1] += (Uint16) *srcpix++;
                accumulate[2] += (Uint16) *srcpix++;
                accumulate[3] += (Uint16) *srcpix++;
                xcounter -= 0x10000;
            }
            else
            {
                int xfrac = 0x10000 - xcounter;
                /* write out a destination pixel */
                *dstpix++ = (Uint8) (((accumulate[0] + ((srcpix[0] * xcounter) >> 16)) * xrecip) >> 16);
                *dstpix++ = (Uint8) (((accumulate[1] + ((srcpix[1] * xcounter) >> 16)) * xrecip) >> 16);
                *dstpix++ = (Uint8) (((accumulate[2] + ((srcpix[2] * xcounter) >> 16)) * xrecip) >> 16);
                *dstpix++ = (Uint8) (((accumulate[3] + ((srcpix[3] * xcounter) >> 16)) * xrecip) >> 16);
                /* reload the accumulator with the remainder of this pixel */
                accumulate[0] = (Uint16) ((*srcpix++ * xfrac) >> 16);
                accumulate[1] = (Uint16) ((*srcpix++ * xfrac) >> 16);
                accumulate[2] = (Uint16) ((*srcpix++ * xfrac) >> 16);
                accumulate[3] = (Uint16) ((*srcpix++ * xfrac) >> 16);
                xcounter = xspace - xfrac;
            }
        }
        srcpix += srcdiff;
        dstpix += dstdiff;
    }
}

/* this function implements an area-averaging shrinking filter in the Y-dimension */
static void filter_shrink_Y(Uint8 *srcpix, Uint8 *dstpix, int width, int srcpitch, int dstpitch, int srcheight, int dstheight)
{
    Uint16 *templine;
    int srcdiff = srcpitch - (width * 4);
    int dstdiff = dstpitch - (width * 4);
    int x, y;
    int yspace = 0x10000 * srcheight / dstheight; /* must be > 1 */
    int yrecip = (int) (0x100000000LL / yspace);
    int ycounter = yspace;

    /* allocate and clear a memory area for storing the accumulator line */
    templine = (Uint16 *) malloc(dstpitch * 2);
    if (templine == NULL) return;
    memset(templine, 0, dstpitch * 2);

    for (y = 0; y < srcheight; y++)
    {
        Uint16 *accumulate = templine;
        if (ycounter > 0x10000)
        {
            for (x = 0; x < width; x++)
            {
                *accumulate++ += (Uint16) *srcpix++;
                *accumulate++ += (Uint16) *srcpix++;
                *accumulate++ += (Uint16) *srcpix++;
                *accumulate++ += (Uint16) *srcpix++;
            }
            ycounter -= 0x10000;
        }
        else
        {
            int yfrac = 0x10000 - ycounter;
            /* write out a destination line */
            for (x = 0; x < width; x++)
            {
                *dstpix++ = (Uint8) (((*accumulate++ + ((*srcpix++ * ycounter) >> 16)) * yrecip) >> 16);
                *dstpix++ = (Uint8) (((*accumulate++ + ((*srcpix++ * ycounter) >> 16)) * yrecip) >> 16);
                *dstpix++ = (Uint8) (((*accumulate++ + ((*srcpix++ * ycounter) >> 16)) * yrecip) >> 16);
                *dstpix++ = (Uint8) (((*accumulate++ + ((*srcpix++ * ycounter) >> 16)) * yrecip) >> 16);
            }
            dstpix += dstdiff;
            /* reload the accumulator with the remainder of this line */
            accumulate = templine;
            srcpix -= 4 * width;
            for (x = 0; x < width; x++)
            {
                *accumulate++ = (Uint16) ((*srcpix++ * yfrac) >> 16);
                *accumulate++ = (Uint16) ((*srcpix++ * yfrac) >> 16);
                *accumulate++ = (Uint16) ((*srcpix++ * yfrac) >> 16);
                *accumulate++ = (Uint16) ((*srcpix++ * yfrac) >> 16);
            }
            ycounter = yspace - yfrac;
        }
        srcpix += srcdiff;
    } /* for (int y = 0; y < srcheight; y++) */

    /* free the temporary memory */
    free(templine);
}

/* this function implements a bilinear filter in the X-dimension */
static void filter_expand_X(Uint8 *srcpix, Uint8 *dstpix, int height, int srcpitch, int dstpitch, int srcwidth, int dstwidth)
{
    int dstdiff = dstpitch - (dstwidth * 4);
    int *xidx0, *xmult0, *xmult1;
    int x, y;
    int factorwidth = 4;

    /* Allocate memory for factors */
    xidx0 = malloc(dstwidth * 4);
    if (xidx0 == NULL) return;
    xmult0 = (int *) malloc(dstwidth * factorwidth);
    xmult1 = (int *) malloc(dstwidth * factorwidth);
    if (xmult0 == NULL || xmult1 == NULL)
    {
        free(xidx0);
        if (xmult0) free(xmult0);
        if (xmult1) free(xmult1);
    }

    /* Create multiplier factors and starting indices and put them in arrays */
    for (x = 0; x < dstwidth; x++)
    {
        xidx0[x] = x * (srcwidth - 1) / dstwidth;
        xmult1[x] = 0x10000 * ((x * (srcwidth - 1)) % dstwidth) / dstwidth;
        xmult0[x] = 0x10000 - xmult1[x];
    }

    /* Do the scaling in raster order so we don't trash the cache */
    for (y = 0; y < height; y++)
    {
        Uint8 *srcrow0 = srcpix + y * srcpitch;
        for (x = 0; x < dstwidth; x++)
        {
            Uint8 *src = srcrow0 + xidx0[x] * 4;
            int xm0 = xmult0[x];
            int xm1 = xmult1[x];
            *dstpix++ = (Uint8) (((src[0] * xm0) + (src[4] * xm1)) >> 16);
            *dstpix++ = (Uint8) (((src[1] * xm0) + (src[5] * xm1)) >> 16);
            *dstpix++ = (Uint8) (((src[2] * xm0) + (src[6] * xm1)) >> 16);
            *dstpix++ = (Uint8) (((src[3] * xm0) + (src[7] * xm1)) >> 16);
        }
        dstpix += dstdiff;
    }

    /* free memory */
    free(xidx0);
    free(xmult0);
    free(xmult1);
}

/* this function implements a bilinear filter in the Y-dimension */
static void filter_expand_Y(Uint8 *srcpix, Uint8 *dstpix, int width, int srcpitch, int dstpitch, int srcheight, int dstheight)
{
    int x, y;

    for (y = 0; y < dstheight; y++)
    {
        int yidx0 = y * (srcheight - 1) / dstheight;
        Uint8 *srcrow0 = srcpix + yidx0 * srcpitch;
        Uint8 *srcrow1 = srcrow0 + srcpitch;
        int ymult1 = 0x10000 * ((y * (srcheight - 1)) % dstheight) / dstheight;
        int ymult0 = 0x10000 - ymult1;
        for (x = 0; x < width; x++)
        {
            *dstpix++ = (Uint8) (((*srcrow0++ * ymult0) + (*srcrow1++ * ymult1)) >> 16);
            *dstpix++ = (Uint8) (((*srcrow0++ * ymult0) + (*srcrow1++ * ymult1)) >> 16);
            *dstpix++ = (Uint8) (((*srcrow0++ * ymult0) + (*srcrow1++ * ymult1)) >> 16);
            *dstpix++ = (Uint8) (((*srcrow0++ * ymult0) + (*srcrow1++ * ymult1)) >> 16);
        }
    }
}


static void convert_24_32(Uint8 *srcpix, int srcpitch, Uint8 *dstpix, int dstpitch, int width, int height)
{
    int srcdiff = srcpitch - (width * 3);
    int dstdiff = dstpitch - (width * 4);
    int x, y;

    for (y = 0; y < height; y++)
    {
        for (x = 0; x < width; x++)
        {
            *dstpix++ = *srcpix++;
            *dstpix++ = *srcpix++;
            *dstpix++ = *srcpix++;
            *dstpix++ = 0xff;
        }
        srcpix += srcdiff;
        dstpix += dstdiff;
    }
}

static void convert_32_24(Uint8 *srcpix, int srcpitch, Uint8 *dstpix, int dstpitch, int width, int height)
{
    int srcdiff = srcpitch - (width * 4);
    int dstdiff = dstpitch - (width * 3);
    int x, y;

    for (y = 0; y < height; y++)
    {
        for (x = 0; x < width; x++)
        {
            *dstpix++ = *srcpix++;
            *dstpix++ = *srcpix++;
            *dstpix++ = *srcpix++;
            srcpix++;
        }
        srcpix += srcdiff;
        dstpix += dstdiff;
    }
}

static void
scalesmooth(SDL_Surface *src, SDL_Surface *dst)
{
    Uint8* srcpix = (Uint8*)src->pixels;
    Uint8* dstpix = (Uint8*)dst->pixels;
    Uint8* dst32 = NULL;
    int srcpitch = src->pitch;
    int dstpitch = dst->pitch;

    int srcwidth = src->w;
    int srcheight = src->h;
    int dstwidth = dst->w;
    int dstheight = dst->h;

    int bpp = src->format->BytesPerPixel;

    Uint8 *temppix = NULL;
    int tempwidth=0, temppitch=0, tempheight=0;

    /* convert to 32-bit if necessary */
    if (bpp == 3)
    {
        int newpitch = srcwidth * 4;
        Uint8 *newsrc = (Uint8 *) malloc(newpitch * srcheight);
        if (!newsrc)
            return;
        convert_24_32(srcpix, srcpitch, newsrc, newpitch, srcwidth, srcheight);
        srcpix = newsrc;
        srcpitch = newpitch;
        /* create a destination buffer for the 32-bit result */
        dstpitch = dstwidth << 2;
        dst32 = (Uint8 *) malloc(dstpitch * dstheight);
        if (dst32 == NULL)
        {
            free(srcpix);
            return;
        }
        dstpix = dst32;
    }

    /* Create a temporary processing buffer if we will be scaling both X and Y */
    if (srcwidth != dstwidth && srcheight != dstheight)
    {
        tempwidth = dstwidth;
        temppitch = tempwidth << 2;
        tempheight = srcheight;
        temppix = (Uint8 *) malloc(temppitch * tempheight);
        if (temppix == NULL)
        {
            if (bpp == 3)
            {
                free(srcpix);
                free(dstpix);
            }
            return;
        }
    }

    /* Start the filter by doing X-scaling */
    if (dstwidth < srcwidth) /* shrink */
    {
        if (srcheight != dstheight)
            filter_shrink_X(srcpix, temppix, srcheight, srcpitch, temppitch, srcwidth, dstwidth);
        else
            filter_shrink_X(srcpix, dstpix, srcheight, srcpitch, dstpitch, srcwidth, dstwidth);
    }
    else if (dstwidth > srcwidth) /* expand */
    {
        if (srcheight != dstheight)
            filter_expand_X(srcpix, temppix, srcheight, srcpitch, temppitch, srcwidth, dstwidth);
        else
            filter_expand_X(srcpix, dstpix, srcheight, srcpitch, dstpitch, srcwidth, dstwidth);
    }
    /* Now do the Y scale */
    if (dstheight < srcheight) /* shrink */
    {
        if (srcwidth != dstwidth)
            filter_shrink_Y(temppix, dstpix, tempwidth, temppitch, dstpitch, srcheight, dstheight);
        else
            filter_shrink_Y(srcpix, dstpix, srcwidth, srcpitch, dstpitch, srcheight, dstheight);
    }
    else if (dstheight > srcheight)  /* expand */
    {
        if (srcwidth != dstwidth)
            filter_expand_Y(temppix, dstpix, tempwidth, temppitch, dstpitch, srcheight, dstheight);
        else
            filter_expand_Y(srcpix, dstpix, srcwidth, srcpitch, dstpitch, srcheight, dstheight);
    }

    /* Convert back to 24-bit if necessary */
    if (bpp == 3)
    {
        convert_32_24(dst32, dstpitch, (Uint8*)dst->pixels, dst->pitch, dstwidth, dstheight);
        free(dst32);
        dst32 = NULL;
        free(srcpix);
        srcpix = NULL;
    }
    /* free temporary buffer if necessary */
    if (temppix != NULL)
        free(temppix);

}
