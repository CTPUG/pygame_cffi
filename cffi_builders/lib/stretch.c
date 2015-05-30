static void
stretch (SDL_Surface *src, SDL_Surface *dst)
{
    int looph, loopw;

    Uint8* srcrow = (Uint8*) src->pixels;
    Uint8* dstrow = (Uint8*) dst->pixels;

    int srcpitch = src->pitch;
    int dstpitch = dst->pitch;

    int dstwidth = dst->w;
    int dstheight = dst->h;
    int dstwidth2 = dst->w << 1;
    int dstheight2 = dst->h << 1;

    int srcwidth2 = src->w << 1;
    int srcheight2 = src->h << 1;

    int w_err, h_err = srcheight2 - dstheight2;


    switch (src->format->BytesPerPixel)
    {
    case 1:
        for (looph = 0; looph < dstheight; ++looph)
        {
            Uint8 *srcpix = (Uint8*)srcrow, *dstpix = (Uint8*)dstrow;
            w_err = srcwidth2 - dstwidth2;
            for (loopw = 0; loopw < dstwidth; ++ loopw)
            {
                *dstpix++ = *srcpix;
                while (w_err >= 0)
                {
                    ++srcpix;
                    w_err -= dstwidth2;
                }
                w_err += srcwidth2;
            }
            while (h_err >= 0)
            {
                srcrow += srcpitch;
                h_err -= dstheight2;
            }
            dstrow += dstpitch;
            h_err += srcheight2;
        }
        break;
    case 2:
        for (looph = 0; looph < dstheight; ++looph)
        {
            Uint16 *srcpix = (Uint16*)srcrow, *dstpix = (Uint16*)dstrow;
            w_err = srcwidth2 - dstwidth2;
            for (loopw = 0; loopw < dstwidth; ++ loopw)
            {
                *dstpix++ = *srcpix;
                while (w_err >= 0)
                {
                    ++srcpix;
                    w_err -= dstwidth2;
                }
                w_err += srcwidth2;
            }
            while (h_err >= 0)
            {
                srcrow += srcpitch;
                h_err -= dstheight2;
            }
            dstrow += dstpitch;
            h_err += srcheight2;
        }
        break;
    case 3:
        for (looph = 0; looph < dstheight; ++looph)
        {
            Uint8 *srcpix = (Uint8*)srcrow, *dstpix = (Uint8*)dstrow;
            w_err = srcwidth2 - dstwidth2;
            for (loopw = 0; loopw < dstwidth; ++ loopw)
            {
                dstpix[0] = srcpix[0];
                dstpix[1] = srcpix[1];
                dstpix[2] = srcpix[2];
                dstpix += 3;
                while (w_err >= 0)
                {
                    srcpix+=3;
                    w_err -= dstwidth2;
                }
                w_err += srcwidth2;
            }
            while (h_err >= 0)
            {
                srcrow += srcpitch;
                h_err -= dstheight2;
            }
            dstrow += dstpitch;
            h_err += srcheight2;
        }
        break;
    default: /*case 4:*/
        for (looph = 0; looph < dstheight; ++looph)
        {
            Uint32 *srcpix = (Uint32*)srcrow, *dstpix = (Uint32*)dstrow;
            w_err = srcwidth2 - dstwidth2;
            for (loopw = 0; loopw < dstwidth; ++ loopw)
            {
                *dstpix++ = *srcpix;
                while (w_err >= 0)
                {
                    ++srcpix;
                    w_err -= dstwidth2;
                }
                w_err += srcwidth2;
            }
            while (h_err >= 0)
            {
                srcrow += srcpitch;
                h_err -= dstheight2;
            }
            dstrow += dstpitch;
            h_err += srcheight2;
        }
        break;
    }
}
