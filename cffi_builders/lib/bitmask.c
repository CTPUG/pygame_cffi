/*
    Bitmask Collision Detection Library 1.5
    Copyright (C) 2002-2005 Ulf Ekstrom except for the bitcount function which
    is copyright (C) Donald W. Gillies, 1992, and the other bitcount function
    which was taken from Jorg Arndt's excellent "Algorithms for Programmers"
    text.

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
 */

#include <stdlib.h>
#include <stddef.h>
#include <string.h>

static inline unsigned int bitcount(BITMASK_W n)
{
  if (BITMASK_W_LEN == 32)
  {
    /* This piece taken from Jorg Arndt's "Algorithms for Programmers" */
    n  = ((n>>1) & 0x55555555) + (n & 0x55555555);  // 0-2 in 2 bits
    n  = ((n>>2) & 0x33333333) + (n & 0x33333333);  // 0-4 in 4 bits
    n  = ((n>>4) + n) & 0x0f0f0f0f;                 // 0-8 in 4 bits
    n +=  n>> 8;                                    // 0-16 in 8 bits
    n +=  n>>16;                                    // 0-32 in 8 bits
    return  n & 0xff;
  }
  else if (BITMASK_W_LEN == 64)
  {
    n  = ((n>>1) & 0x5555555555555555) + (n & 0x5555555555555555);
    n  = ((n>>2) & 0x3333333333333333) + (n & 0x3333333333333333);
    n  = ((n>>4) + n) & 0x0f0f0f0f0f0f0f0f;
    n +=  n>> 8;
    n +=  n>>16;
    n +=  n>>32;
    return  n & 0xff;
  }
  else
  {
    /* Handle non-32 or 64 bit case the slow way */
    unsigned int nbits = 0;
    while (n)
    {
      if (n & 1)
      nbits++;
      n = n >> 1;
    }
    return nbits;
  }
}

bitmask_t *bitmask_create(int w, int h)
{
  bitmask_t *temp;
  temp = malloc(offsetof(bitmask_t,bits) + h*((w - 1)/BITMASK_W_LEN + 1)*sizeof(BITMASK_W));
  if (!temp)
    return 0;
  temp->w = w;
  temp->h = h;
  bitmask_clear(temp);
  return temp;
}

void bitmask_free(bitmask_t *m)
{
  free(m);
}

void bitmask_clear(bitmask_t *m)
{
  memset(m->bits,0,m->h*((m->w - 1)/BITMASK_W_LEN + 1)*sizeof(BITMASK_W));
}

void bitmask_fill(bitmask_t *m)
{
    int len, shift;
    BITMASK_W *pixels, cmask, full;

    len = m->h*((m->w - 1)/BITMASK_W_LEN);
    shift = BITMASK_W_LEN - (m->w % BITMASK_W_LEN);
    full = ~(BITMASK_W)0;
    cmask = (~(BITMASK_W)0) >> shift;
    /* fill all the pixels that aren't in the rightmost BITMASK_Ws */
    for (pixels = m->bits; pixels < (m->bits + len); pixels++) {
        *pixels = full;
    }
    /* for the rightmost BITMASK_Ws, use cmask to ensure we aren't setting
       bits that are outside of the mask */
    for (pixels = m->bits + len; pixels < (m->bits + len + m->h); pixels++) {
        *pixels = cmask;
    }
}

void bitmask_invert(bitmask_t *m)
{
    int len, shift;
    BITMASK_W *pixels, cmask;

    len = m->h*((m->w - 1)/BITMASK_W_LEN);
    shift = BITMASK_W_LEN - (m->w % BITMASK_W_LEN);
    cmask = (~(BITMASK_W)0) >> shift;
    /* flip all the pixels that aren't in the rightmost BITMASK_Ws */
    for (pixels = m->bits; pixels < (m->bits + len); pixels++) {
        *pixels = ~(*pixels);
    }
    /* for the rightmost BITMASK_Ws, & with cmask to ensure we aren't setting
       bits that are outside of the mask */
    for (pixels = m->bits + len; pixels < (m->bits + len + m->h); pixels++) {
        *pixels = cmask & ~(*pixels);
    }
}

unsigned int bitmask_count(bitmask_t *m)
{
    BITMASK_W *pixels;
    unsigned int tot = 0;

    for (pixels=m->bits; pixels<(m->bits+m->h*((m->w-1)/BITMASK_W_LEN + 1)); pixels++) {
        tot += bitcount(*pixels);
    }

    return tot;
}

int bitmask_overlap(const bitmask_t *a, const bitmask_t *b, int xoffset, int yoffset)
{
  const BITMASK_W *a_entry,*a_end;
  const BITMASK_W *b_entry;
  const BITMASK_W *ap,*app,*bp;
  unsigned int shift,rshift,i,astripes,bstripes;

  if ((xoffset >= a->w) || (yoffset >= a->h) || (b->h + yoffset <= 0) || (b->w + xoffset <= 0))
    return 0;

  if (xoffset >= 0)
  {
  swapentry:
    if (yoffset >= 0)
    {
      a_entry = a->bits + a->h*((unsigned int)xoffset/BITMASK_W_LEN) + yoffset;
      a_end = a_entry + MIN(b->h,a->h - yoffset);
      b_entry = b->bits;
    }
    else
    {
      a_entry = a->bits + a->h*((unsigned int)xoffset/BITMASK_W_LEN);
      a_end = a_entry + MIN(b->h + yoffset,a->h);
      b_entry = b->bits - yoffset;
    }
    shift = xoffset & BITMASK_W_MASK;
    if (shift)
    {
      rshift = BITMASK_W_LEN - shift;
      astripes = ((unsigned int)(a->w - 1))/BITMASK_W_LEN - (unsigned int)xoffset/BITMASK_W_LEN;
      bstripes = ((unsigned int)(b->w - 1))/BITMASK_W_LEN + 1;
      if (bstripes > astripes) /* zig-zag .. zig*/
      {
        for (i=0;i<astripes;i++)
        {
          for (ap = a_entry, app = ap + a->h, bp = b_entry;ap < a_end;)
            if ((*ap++ >> shift) & *bp || (*app++ << rshift) & *bp++) return 1;
          a_entry += a->h;
          a_end += a->h;
          b_entry += b->h;
        }
          for (ap = a_entry,bp = b_entry;ap < a_end;)
          if ((*ap++ >> shift) & *bp++) return 1;
          return 0;
      }
      else /* zig-zag */
      {
        for (i=0;i<bstripes;i++)
        {
          for (ap = a_entry, app = ap + a->h, bp = b_entry;ap < a_end;)
            if ((*ap++ >> shift) & *bp || (*app++ << rshift) & *bp++) return 1;
          a_entry += a->h;
          a_end += a->h;
          b_entry += b->h;
        }
        return 0;
      }
    }
    else /* xoffset is a multiple of the stripe width, and the above routines wont work */
    {
      astripes = (MIN(b->w,a->w - xoffset) - 1)/BITMASK_W_LEN + 1;
      for (i=0;i<astripes;i++)
      {
        for (ap = a_entry,bp = b_entry;ap < a_end;)
          if (*ap++ & *bp++) return 1;
        a_entry += a->h;
        a_end += a->h;
        b_entry += b->h;
      }
      return 0;
    }
  }
  else
  {
    const bitmask_t *c = a;
    a = b;
    b = c;
    xoffset *= -1;
    yoffset *= -1;
    goto swapentry;
  }
}

/* Will hang if there are no bits set in w! */
static inline int firstsetbit(BITMASK_W w)
{
  int i = 0;
  while ((w & 1) == 0)
  {
    i++;
    w/=2;
  }
  return i;
}

/* x and y are given in the coordinates of mask a, and are untouched if there is no overlap */
int bitmask_overlap_pos(const bitmask_t *a, const bitmask_t *b, int xoffset, int yoffset, int *x, int *y)
{
  const BITMASK_W *a_entry,*a_end, *b_entry, *ap, *bp;
  unsigned int shift,rshift,i,astripes,bstripes,xbase;

  if ((xoffset >= a->w) || (yoffset >= a->h) || (yoffset <= - b->h))
    return 0;

  if (xoffset >= 0)
  {
    xbase = xoffset/BITMASK_W_LEN; /* first stripe from mask a */
    if (yoffset >= 0)
    {
      a_entry = a->bits + a->h*xbase + yoffset;
      a_end = a_entry + MIN(b->h,a->h - yoffset);
      b_entry = b->bits;
    }
    else
    {
      a_entry = a->bits + a->h*xbase;
      a_end = a_entry + MIN(b->h + yoffset,a->h);
      b_entry = b->bits - yoffset;
      yoffset = 0; /* relied on below */
    }
    shift = xoffset & BITMASK_W_MASK;
    if (shift)
    {
      rshift = BITMASK_W_LEN - shift;
      astripes = (a->w - 1)/BITMASK_W_LEN - xoffset/BITMASK_W_LEN;
      bstripes = (b->w - 1)/BITMASK_W_LEN + 1;
      if (bstripes > astripes) /* zig-zag .. zig*/
      {
        for (i=0;i<astripes;i++)
        {
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            if (*ap & (*bp << shift))
            {
              *y = ap - a_entry + yoffset;
              *x = (xbase + i)*BITMASK_W_LEN + firstsetbit(*ap & (*bp << shift));
              return 1;
            }
          a_entry += a->h;
          a_end += a->h;
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            if (*ap & (*bp >> rshift))
            {
              *y = ap - a_entry + yoffset;
              *x = (xbase + i + 1)*BITMASK_W_LEN + firstsetbit(*ap & (*bp >> rshift));
              return 1;
            }
          b_entry += b->h;
        }
        for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
          if (*ap & (*bp << shift))
          {
            *y = ap - a_entry + yoffset;
            *x = (xbase + astripes)*BITMASK_W_LEN + firstsetbit(*ap & (*bp << shift));
            return 1;
          }
        return 0;
      }
      else /* zig-zag */
      {
        for (i=0;i<bstripes;i++)
        {
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            if (*ap & (*bp << shift))
            {
              *y = ap - a_entry + yoffset;
              *x = (xbase + i)*BITMASK_W_LEN + firstsetbit(*ap & (*bp << shift));
              return 1;
            }
          a_entry += a->h;
          a_end += a->h;
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            if (*ap & (*bp >> rshift))
            {
              *y = ap - a_entry + yoffset;
              *x = (xbase + i + 1)*BITMASK_W_LEN + firstsetbit(*ap & (*bp >> rshift));
              return 1;
            }
          b_entry += b->h;
        }
        return 0;
      }
    }
    else
/* xoffset is a multiple of the stripe width, and the above routines
 won't work. This way is also slightly faster. */
    {
      astripes = (MIN(b->w,a->w - xoffset) - 1)/BITMASK_W_LEN + 1;
      for (i=0;i<astripes;i++)
      {
        for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
        {
          if (*ap & *bp)
          {
            *y = ap - a_entry + yoffset;
            *x = (xbase + i)*BITMASK_W_LEN + firstsetbit(*ap & *bp);
            return 1;
          }
        }
        a_entry += a->h;
        a_end += a->h;
        b_entry += b->h;
      }
      return 0;
    }
  }
  else
  {
    if (bitmask_overlap_pos(b,a,-xoffset,-yoffset,x,y))
    {
      *x += xoffset;
      *y += yoffset;
      return 1;
    }
    else
      return 0;
  }
}

int bitmask_overlap_area(const bitmask_t *a, const bitmask_t *b, int xoffset, int yoffset)
{
  const BITMASK_W *a_entry,*a_end, *b_entry, *ap,*bp;
  unsigned int shift,rshift,i,astripes,bstripes;
  unsigned int count = 0;

  if ((xoffset >= a->w) || (yoffset >= a->h) || (b->h + yoffset <= 0) || (b->w + xoffset <= 0))
      return 0;

  if (xoffset >= 0)
  {
  swapentry:
    if (yoffset >= 0)
    {
      a_entry = a->bits + a->h*(xoffset/BITMASK_W_LEN) + yoffset;
      a_end = a_entry + MIN(b->h,a->h - yoffset);
      b_entry = b->bits;
    }
    else
    {
      a_entry = a->bits + a->h*(xoffset/BITMASK_W_LEN);
      a_end = a_entry + MIN(b->h + yoffset,a->h);
      b_entry = b->bits - yoffset;
    }
    shift = xoffset & BITMASK_W_MASK;
    if (shift)
    {
      rshift = BITMASK_W_LEN - shift;
      astripes = (a->w - 1)/BITMASK_W_LEN - xoffset/BITMASK_W_LEN;
      bstripes = (b->w - 1)/BITMASK_W_LEN + 1;
      if (bstripes > astripes) /* zig-zag .. zig*/
      {
        for (i=0;i<astripes;i++)
        {
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            count += bitcount(((*ap >> shift) | (*(ap + a->h) << rshift)) & *bp);
          a_entry += a->h;
          a_end += a->h;
          b_entry += b->h;
        }
        for (ap = a_entry,bp = b_entry;ap < a_end;)
          count += bitcount((*ap++ >> shift) & *bp++);
        return count;
      }
      else /* zig-zag */
      {
        for (i=0;i<bstripes;i++)
        {
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            count += bitcount(((*ap >> shift) | (*(ap + a->h) << rshift)) & *bp);
          a_entry += a->h;
          a_end += a->h;
          b_entry += b->h;
        }
        return count;
      }
    }
    else /* xoffset is a multiple of the stripe width, and the above routines wont work */
    {
      astripes = (MIN(b->w,a->w - xoffset) - 1)/BITMASK_W_LEN + 1;
      for (i=0;i<astripes;i++)
      {
        for (ap = a_entry,bp = b_entry;ap < a_end;)
          count += bitcount(*ap++ & *bp++);

        a_entry += a->h;
        a_end += a->h;
        b_entry += b->h;
      }
      return count;
    }
  }
  else
  {
    const bitmask_t *c = a;
    a = b;
    b = c;
    xoffset *= -1;
    yoffset *= -1;
    goto swapentry;
  }
}

/* Makes a mask of the overlap of two other masks */
void bitmask_overlap_mask(const bitmask_t *a, const bitmask_t *b, bitmask_t *c, int xoffset, int yoffset)
{
  const BITMASK_W *a_entry,*a_end, *ap;
  const BITMASK_W *b_entry, *b_end, *bp;
  BITMASK_W *c_entry, *c_end, *cp;
  int shift,rshift,i,astripes,bstripes;

  if ((xoffset >= a->w) || (yoffset >= a->h) || (yoffset <= - b->h))
    return;

  if (xoffset >= 0)
  {
    if (yoffset >= 0)
    {
      a_entry = a->bits + a->h*(xoffset/BITMASK_W_LEN) + yoffset;
      c_entry = c->bits + c->h*(xoffset/BITMASK_W_LEN) + yoffset;
      a_end = a_entry + MIN(b->h,a->h - yoffset);
      b_entry = b->bits;
    }
    else
    {
      a_entry = a->bits + a->h*(xoffset/BITMASK_W_LEN);
      c_entry = c->bits + c->h*(xoffset/BITMASK_W_LEN);
      a_end = a_entry + MIN(b->h + yoffset,a->h);
      b_entry = b->bits - yoffset;
    }
    shift = xoffset & BITMASK_W_MASK;
    if (shift)
    {
      rshift = BITMASK_W_LEN - shift;
      astripes = (a->w - 1)/BITMASK_W_LEN - xoffset/BITMASK_W_LEN;
      bstripes = (b->w - 1)/BITMASK_W_LEN + 1;
      if (bstripes > astripes) /* zig-zag .. zig*/
        {
        for (i=0;i<astripes;i++)
        {
          for (ap = a_entry,bp = b_entry,cp = c_entry;ap < a_end;ap++,bp++,cp++)
            *cp = *ap & (*bp << shift);
          a_entry += a->h;
          c_entry += c->h;
          a_end += a->h;
          for (ap = a_entry,bp = b_entry,cp = c_entry;ap < a_end;ap++,bp++,cp++)
            *cp = *ap & (*bp >> rshift);
          b_entry += b->h;
        }
        for (ap = a_entry,bp = b_entry,cp = c_entry;ap < a_end;ap++,bp++,cp++)
          *cp = *ap & (*bp << shift);
      }
      else /* zig-zag */
      {
        for (i=0;i<bstripes;i++)
        {
          for (ap = a_entry,bp = b_entry,cp = c_entry;ap < a_end;ap++,bp++,cp++)
            *cp = *ap & (*bp << shift);
          a_entry += a->h;
          c_entry += c->h;
          a_end += a->h;
          for (ap = a_entry,bp = b_entry,cp = c_entry;ap < a_end;ap++,bp++,cp++)
            *cp = *ap & (*bp >> rshift);
          b_entry += b->h;
        }
      }
    }
    else /* xoffset is a multiple of the stripe width,
            and the above routines won't work. */
    {
      astripes = (MIN(b->w,a->w - xoffset) - 1)/BITMASK_W_LEN + 1;
      for (i=0;i<astripes;i++)
      {
        for (ap = a_entry,bp = b_entry,cp = c_entry;ap < a_end;ap++,bp++,cp++)
        {
          *cp = *ap & *bp;
        }
        a_entry += a->h;
        c_entry += c->h;
        a_end += a->h;
        b_entry += b->h;
      }
    }
  }
  else
  {
    xoffset *= -1;
    yoffset *= -1;

    if (yoffset >= 0)
    {
      b_entry = b->bits + b->h*(xoffset/BITMASK_W_LEN) + yoffset;
      b_end = b_entry + MIN(a->h,b->h - yoffset);
      a_entry = a->bits;
      c_entry = c->bits;
    }
    else
    {
      b_entry = b->bits + b->h*(xoffset/BITMASK_W_LEN);
      b_end = b_entry + MIN(a->h + yoffset,b->h);
      a_entry = a->bits - yoffset;
      c_entry = c->bits - yoffset;
    }
    shift = xoffset & BITMASK_W_MASK;
    if (shift)
    {
      rshift = BITMASK_W_LEN - shift;
      astripes = (b->w - 1)/BITMASK_W_LEN - xoffset/BITMASK_W_LEN;
      bstripes = (a->w - 1)/BITMASK_W_LEN + 1;
      if (bstripes > astripes) /* zig-zag .. zig*/
      {
        for (i=0;i<astripes;i++)
        {
          for (bp = b_entry,ap = a_entry,cp = c_entry;bp < b_end;bp++,ap++,cp++)
            *cp = *ap & (*bp >> shift);
          b_entry += b->h;
          b_end += b->h;
          for (bp = b_entry,ap = a_entry,cp = c_entry;bp < b_end;bp++,ap++,cp++)
            *cp = *ap & (*bp <<rshift);
          a_entry += a->h;
          c_entry += c->h;
        }
        for (bp = b_entry,ap = a_entry,cp = c_entry;bp < b_end;bp++,ap++,cp++)
          *cp = *ap & (*bp >> shift);
      }
      else /* zig-zag */
      {
        for (i=0;i<bstripes;i++)
        {
          for (bp = b_entry,ap = a_entry,cp = c_entry;bp < b_end;bp++,ap++,cp++)
            *cp = *ap & (*bp >> shift);
          b_entry += b->h;
          b_end += b->h;
          for (bp = b_entry,ap = a_entry,cp = c_entry;bp < b_end;bp++,ap++,cp++)
            *cp = *ap & (*bp << rshift);
          a_entry += a->h;
          c_entry += c->h;
        }
      }
    }
    else /* xoffset is a multiple of the stripe width, and the above routines won't work. */
    {
      astripes = (MIN(a->w,b->w - xoffset) - 1)/BITMASK_W_LEN + 1;
      for (i=0;i<astripes;i++)
      {
        for (bp = b_entry,ap = a_entry,cp = c_entry;bp < b_end;bp++,ap++,cp++)
        {
          *cp = *ap & *bp;
        }
        b_entry += b->h;
        b_end += b->h;
        a_entry += a->h;
        c_entry += c->h;
      }
    }
    xoffset *= -1;
    yoffset *= -1;
  }
  /* Zero out bits outside the mask rectangle (to the right), if there
   is a chance we were drawing there. */
  if (xoffset + b->w > c->w)
  {
    BITMASK_W edgemask;
    int n = c->w/BITMASK_W_LEN;
    shift = (n + 1)*BITMASK_W_LEN - c->w;
    edgemask = (~(BITMASK_W)0) >> shift;
    c_end = c->bits + n*c->h + MIN(c->h,b->h + yoffset);
    for (cp = c->bits + n*c->h + MAX(yoffset,0);cp<c_end;cp++)
    *cp &= edgemask;
  }
}

/* Draws mask b onto mask a (bitwise OR) */
void bitmask_draw(bitmask_t *a, const bitmask_t *b, int xoffset, int yoffset)
{
  BITMASK_W *a_entry,*a_end, *ap;
  const BITMASK_W *b_entry, *b_end, *bp;
  int shift,rshift,i,astripes,bstripes;

  if ((xoffset >= a->w) || (yoffset >= a->h) || (yoffset <= - b->h))
      return;

  if (xoffset >= 0)
  {
    if (yoffset >= 0)
    {
      a_entry = a->bits + a->h*(xoffset/BITMASK_W_LEN) + yoffset;
      a_end = a_entry + MIN(b->h,a->h - yoffset);
      b_entry = b->bits;
    }
    else
    {
      a_entry = a->bits + a->h*(xoffset/BITMASK_W_LEN);
      a_end = a_entry + MIN(b->h + yoffset,a->h);
      b_entry = b->bits - yoffset;
    }
    shift = xoffset & BITMASK_W_MASK;
    if (shift)
    {
      rshift = BITMASK_W_LEN - shift;
      astripes = (a->w - 1)/BITMASK_W_LEN - xoffset/BITMASK_W_LEN;
      bstripes = (b->w - 1)/BITMASK_W_LEN + 1;
      if (bstripes > astripes) /* zig-zag .. zig*/
      {
        for (i=0;i<astripes;i++)
        {
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            *ap |= (*bp << shift);
          a_entry += a->h;
          a_end += a->h;
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            *ap |= (*bp >> rshift);
          b_entry += b->h;
        }
        for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
        *ap |= (*bp << shift);
      }
      else /* zig-zag */
      {
        for (i=0;i<bstripes;i++)
        {
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            *ap |= (*bp << shift);
          a_entry += a->h;
          a_end += a->h;
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            *ap |= (*bp >> rshift);
          b_entry += b->h;
        }
      }
    }
    else /* xoffset is a multiple of the stripe width,
            and the above routines won't work. */
    {
      astripes = (MIN(b->w,a->w - xoffset) - 1)/BITMASK_W_LEN + 1;
      for (i=0;i<astripes;i++)
      {
        for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
        {
          *ap |= *bp;
        }
        a_entry += a->h;
        a_end += a->h;
        b_entry += b->h;
      }
    }
  }
  else
  {
    xoffset *= -1;
    yoffset *= -1;

    if (yoffset >= 0)
    {
      b_entry = b->bits + b->h*(xoffset/BITMASK_W_LEN) + yoffset;
      b_end = b_entry + MIN(a->h,b->h - yoffset);
      a_entry = a->bits;
    }
    else
    {
      b_entry = b->bits + b->h*(xoffset/BITMASK_W_LEN);
      b_end = b_entry + MIN(a->h + yoffset,b->h);
      a_entry = a->bits - yoffset;
    }
    shift = xoffset & BITMASK_W_MASK;
    if (shift)
    {
      rshift = BITMASK_W_LEN - shift;
      astripes = (b->w - 1)/BITMASK_W_LEN - xoffset/BITMASK_W_LEN;
      bstripes = (a->w - 1)/BITMASK_W_LEN + 1;
      if (bstripes > astripes) /* zig-zag .. zig*/
      {
        for (i=0;i<astripes;i++)
        {
          for (bp = b_entry,ap = a_entry;bp < b_end;bp++,ap++)
            *ap |= (*bp >> shift);
          b_entry += b->h;
          b_end += b->h;
          for (bp = b_entry,ap = a_entry;bp < b_end;bp++,ap++)
            *ap |= (*bp <<rshift);
          a_entry += a->h;
        }
        for (bp = b_entry,ap = a_entry;bp < b_end;bp++,ap++)
          *ap |= (*bp >> shift);
      }
      else /* zig-zag */
      {
        for (i=0;i<bstripes;i++)
        {
          for (bp = b_entry,ap = a_entry;bp < b_end;bp++,ap++)
            *ap |= (*bp >> shift);
          b_entry += b->h;
          b_end += b->h;
          for (bp = b_entry,ap = a_entry;bp < b_end;bp++,ap++)
            *ap |= (*bp << rshift);
          a_entry += a->h;
        }
      }
    }
    else /* xoffset is a multiple of the stripe width, and the above routines won't work. */
    {
      astripes = (MIN(a->w,b->w - xoffset) - 1)/BITMASK_W_LEN + 1;
      for (i=0;i<astripes;i++)
      {
        for (bp = b_entry,ap = a_entry;bp < b_end;bp++,ap++)
        {
          *ap |= *bp;
        }
        b_entry += b->h;
        b_end += b->h;
        a_entry += a->h;
      }
    }
    xoffset *= -1;
    yoffset *= -1;
  }
  /* Zero out bits outside the mask rectangle (to the right), if there
   is a chance we were drawing there. */
  if (xoffset + b->w > a->w)
  {
    BITMASK_W edgemask;
    int n = a->w/BITMASK_W_LEN;
    shift = (n + 1)*BITMASK_W_LEN - a->w;
    edgemask = (~(BITMASK_W)0) >> shift;
    a_end = a->bits + n*a->h + MIN(a->h,b->h + yoffset);
    for (ap = a->bits + n*a->h + MAX(yoffset,0);ap<a_end;ap++)
    *ap &= edgemask;
  }
}

/* Erases mask b from mask a (a &= ~b) */
void bitmask_erase(bitmask_t *a, const bitmask_t *b, int xoffset, int yoffset)
{
  BITMASK_W *a_entry,*a_end, *ap;
  const BITMASK_W *b_entry, *b_end, *bp;
  int shift,rshift,i,astripes,bstripes;

  if ((xoffset >= a->w) || (yoffset >= a->h) || (yoffset <= - b->h))
    return;

  if (xoffset >= 0)
  {
    if (yoffset >= 0)
    {
      a_entry = a->bits + a->h*(xoffset/BITMASK_W_LEN) + yoffset;
      a_end = a_entry + MIN(b->h,a->h - yoffset);
      b_entry = b->bits;
    }
    else
    {
      a_entry = a->bits + a->h*(xoffset/BITMASK_W_LEN);
      a_end = a_entry + MIN(b->h + yoffset,a->h);
      b_entry = b->bits - yoffset;
    }
    shift = xoffset & BITMASK_W_MASK;
    if (shift)
    {
      rshift = BITMASK_W_LEN - shift;
      astripes = (a->w - 1)/BITMASK_W_LEN - xoffset/BITMASK_W_LEN;
      bstripes = (b->w - 1)/BITMASK_W_LEN + 1;
      if (bstripes > astripes) /* zig-zag .. zig*/
      {
        for (i=0;i<astripes;i++)
        {
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            *ap &= ~(*bp << shift);
          a_entry += a->h;
          a_end += a->h;
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            *ap &= ~(*bp >> rshift);
          b_entry += b->h;
        }
        for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
          *ap &= ~(*bp << shift);
      }
      else /* zig-zag */
      {
        for (i=0;i<bstripes;i++)
        {
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            *ap &= ~(*bp << shift);
          a_entry += a->h;
          a_end += a->h;
          for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
            *ap &= ~(*bp >> rshift);
          b_entry += b->h;
        }
      }
    }
    else /* xoffset is a multiple of the stripe width,
          and the above routines won't work. */
    {
      astripes = (MIN(b->w,a->w - xoffset) - 1)/BITMASK_W_LEN + 1;
      for (i=0;i<astripes;i++)
      {
        for (ap = a_entry,bp = b_entry;ap < a_end;ap++,bp++)
        {
          *ap &= ~*bp;
        }
        a_entry += a->h;
        a_end += a->h;
        b_entry += b->h;
      }
    }
  }
  else
  {
    xoffset *= -1;
    yoffset *= -1;

    if (yoffset >= 0)
    {
      b_entry = b->bits + b->h*(xoffset/BITMASK_W_LEN) + yoffset;
      b_end = b_entry + MIN(a->h,b->h - yoffset);
      a_entry = a->bits;
    }
    else
    {
      b_entry = b->bits + b->h*(xoffset/BITMASK_W_LEN);
      b_end = b_entry + MIN(a->h + yoffset,b->h);
      a_entry = a->bits - yoffset;
    }
    shift = xoffset & BITMASK_W_MASK;
    if (shift)
    {
      rshift = BITMASK_W_LEN - shift;
      astripes = (b->w - 1)/BITMASK_W_LEN - xoffset/BITMASK_W_LEN;
      bstripes = (a->w - 1)/BITMASK_W_LEN + 1;
      if (bstripes > astripes) /* zig-zag .. zig*/
      {
        for (i=0;i<astripes;i++)
        {
          for (bp = b_entry,ap = a_entry;bp < b_end;bp++,ap++)
            *ap &= ~(*bp >> shift);
          b_entry += b->h;
          b_end += b->h;
          for (bp = b_entry,ap = a_entry;bp < b_end;bp++,ap++)
            *ap &= ~(*bp <<rshift);
          a_entry += a->h;
        }
        for (bp = b_entry,ap = a_entry;bp < b_end;bp++,ap++)
          *ap |= (*bp >> shift);
      }
      else /* zig-zag */
      {
        for (i=0;i<bstripes;i++)
        {
          for (bp = b_entry,ap = a_entry;bp < b_end;bp++,ap++)
            *ap &= ~(*bp >> shift);
          b_entry += b->h;
          b_end += b->h;
          for (bp = b_entry,ap = a_entry;bp < b_end;bp++,ap++)
            *ap &= ~(*bp << rshift);
          a_entry += a->h;
        }
      }
    }
    else /* xoffset is a multiple of the stripe width, and the above routines won't work. */
    {
      astripes = (MIN(a->w,b->w - xoffset) - 1)/BITMASK_W_LEN + 1;
      for (i=0;i<astripes;i++)
      {
        for (bp = b_entry,ap = a_entry;bp < b_end;bp++,ap++)
          *ap &= ~*bp;
        b_entry += b->h;
        b_end += b->h;
        a_entry += a->h;
      }
    }
  }
}



bitmask_t *bitmask_scale(const bitmask_t *m, int w, int h)
{
  bitmask_t *nm;
  int x,y,nx,ny,dx,dy,dnx,dny;

  if (w < 1 || h < 1)
  {
    nm = bitmask_create(1,1);
    return nm;
  }

  nm = bitmask_create(w,h);
  if (!nm)
    return NULL;
  ny = dny = 0;
  for (y=0,dy=h; y<m->h; y++,dy+=h)
  {
    while (dny < dy)
    {
      nx = dnx = 0;
      for (x=0,dx=w; x < m->w; x++, dx+=w)
      {
        if (bitmask_getbit(m,x,y))
        {
          while (dnx < dx)
          {
            bitmask_setbit(nm,nx,ny);
            nx++;
            dnx += m->w;
          }
        }
        else
        {
          while (dnx < dx)
          {
            nx++;
            dnx += m->w;
          }
        }
      }
      ny++;
      dny+=m->h;
    }
  }
  return nm;
}

void bitmask_convolve(const bitmask_t *a, const bitmask_t *b, bitmask_t *o, int xoffset, int yoffset)
{
  int x, y;

  xoffset += b->w - 1;
  yoffset += b->h - 1;
  for (y = 0; y < b->h; y++)
    for (x = 0; x < b->w; x++)
      if (bitmask_getbit(b, x, y))
        bitmask_draw(o, a, xoffset - x, yoffset - y);
}

/*
 bitmask_threshold, cc_label,  get_connected_components, largest_connected_comp
 and internal_get_bounding_rects
 come from pygame/src/mask.c
 */

/*

palette_colors - this only affects surfaces with a palette
    if true we look at the colors from the palette,
    otherwise we threshold the pixel values.  This is useful if
    the surface is actually greyscale colors, and not palette colors.

*/

void bitmask_threshold (bitmask_t *m,
                        SDL_Surface *surf,
                        SDL_Surface *surf2,
                        Uint32 color,
                        Uint32 threshold,
                        int palette_colors)
{
    int x, y, rshift, gshift, bshift, rshift2, gshift2, bshift2;
    int rloss, gloss, bloss, rloss2, gloss2, bloss2;
    Uint8 *pixels, *pixels2;
    SDL_PixelFormat *format, *format2;
    Uint32 the_color, the_color2, rmask, gmask, bmask, rmask2, gmask2, bmask2;
    Uint8 *pix;
    Uint8 r, g, b, a;
    Uint8 tr, tg, tb, ta;
    int bpp1, bpp2;


    pixels = (Uint8 *) surf->pixels;
    format = surf->format;
    rmask = format->Rmask;
    gmask = format->Gmask;
    bmask = format->Bmask;
    rshift = format->Rshift;
    gshift = format->Gshift;
    bshift = format->Bshift;
    rloss = format->Rloss;
    gloss = format->Gloss;
    bloss = format->Bloss;
    bpp1 = surf->format->BytesPerPixel;

    if(surf2) {
        format2 = surf2->format;
        rmask2 = format2->Rmask;
        gmask2 = format2->Gmask;
        bmask2 = format2->Bmask;
        rshift2 = format2->Rshift;
        gshift2 = format2->Gshift;
        bshift2 = format2->Bshift;
        rloss2 = format2->Rloss;
        gloss2 = format2->Gloss;
        bloss2 = format2->Bloss;
        pixels2 = (Uint8 *) surf2->pixels;
        bpp2 = surf->format->BytesPerPixel;
    } else { /* make gcc stop complaining */
        rmask2 = gmask2 = bmask2 = 0;
        rshift2 = gshift2 = bshift2 = 0;
        rloss2 = gloss2 = bloss2 = 0;
        format2 = NULL;
        pixels2 = NULL;
        bpp2 = 0;
    }


    SDL_GetRGBA (color, format, &r, &g, &b, &a);
    SDL_GetRGBA (threshold, format, &tr, &tg, &tb, &ta);

    for(y=0; y < surf->h; y++) {
        pixels = (Uint8 *) surf->pixels + y*surf->pitch;
        if (surf2) {
            pixels2 = (Uint8 *) surf2->pixels + y*surf2->pitch;
        }
        for(x=0; x < surf->w; x++) {
            /* the_color = surf->get_at(x,y) */
            switch (bpp1)
            {
            case 1:
                the_color = (Uint32)*((Uint8 *) pixels);
                pixels++;
                break;
            case 2:
                the_color = (Uint32)*((Uint16 *) pixels);
                pixels += 2;
                break;
            case 3:
                pix = ((Uint8 *) pixels);
                pixels += 3;
#if SDL_BYTEORDER == SDL_LIL_ENDIAN
                the_color = (pix[0]) + (pix[1] << 8) + (pix[2] << 16);
#else
                the_color = (pix[2]) + (pix[1] << 8) + (pix[0] << 16);
#endif
                break;
            default:                  /* case 4: */
                the_color = *((Uint32 *) pixels);
                pixels += 4;
                break;
            }

            if (surf2) {
                switch (bpp2) {
                    case 1:
                        the_color2 = (Uint32)*((Uint8 *) pixels2);
                        pixels2++;
                        break;
                    case 2:
                        the_color2 = (Uint32)*((Uint16 *) pixels2);
                        pixels2 += 2;
                        break;
                    case 3:
                        pix = ((Uint8 *) pixels2);
                        pixels2 += 3;
#if SDL_BYTEORDER == SDL_LIL_ENDIAN
                        the_color2 = (pix[0]) + (pix[1] << 8) + (pix[2] << 16);
#else
                        the_color2 = (pix[2]) + (pix[1] << 8) + (pix[0] << 16);
#endif
                        break;
                    default:                  /* case 4: */
                        the_color2 = *((Uint32 *) pixels2);
                        pixels2 += 4;
                        break;
                }
                /* TODO: will need to handle surfaces with palette colors.
                */
                if((bpp2 == 1) && (bpp1 == 1) && (!palette_colors)) {
                    /* Don't look at the color of the surface, just use the
                       value. This is useful for 8bit images that aren't
                       actually using the palette.
                    */
                    if (  (abs( (the_color2) - (the_color)) < tr )  ) {

                        /* this pixel is within the threshold of othersurface. */
                        bitmask_setbit(m, x, y);
                    }

                } else if ((abs((((the_color2 & rmask2) >> rshift2) << rloss2) - (((the_color & rmask) >> rshift) << rloss)) < tr) &
                    (abs((((the_color2 & gmask2) >> gshift2) << gloss2) - (((the_color & gmask) >> gshift) << gloss)) < tg) &
                    (abs((((the_color2 & bmask2) >> bshift2) << bloss2) - (((the_color & bmask) >> bshift) << bloss)) < tb)) {
                    /* this pixel is within the threshold of othersurface. */
                    bitmask_setbit(m, x, y);
                }

            /* TODO: will need to handle surfaces with palette colors.
               TODO: will need to handle the case where palette_colors == 0
            */

            } else if ((abs((((the_color & rmask) >> rshift) << rloss) - r) < tr) &
                       (abs((((the_color & gmask) >> gshift) << gloss) - g) < tg) &
                       (abs((((the_color & bmask) >> bshift) << bloss) - b) < tb)) {
                /* this pixel is within the threshold of the color. */
                bitmask_setbit(m, x, y);
            }
        }
    }
}

/* the initial labelling phase of the connected components algorithm

Returns: The highest label in the labelled image

input - The input Mask
image - An array to store labelled pixels
ufind - The union-find label equivalence array
largest - An array to store the number of pixels for each label

*/
unsigned int cc_label(bitmask_t *input, unsigned int* image, unsigned int* ufind, unsigned int* largest)
{
    unsigned int *buf;
    unsigned int x, y, w, h, root, aroot, croot, temp, label;

    label = 0;
    w = input->w;
    h = input->h;

    ufind[0] = 0;
    buf = image;

    /* special case for first pixel */
    if(bitmask_getbit(input, 0, 0)) { /* process for a new connected comp: */
        label++;              /* create a new label */
        *buf = label;         /* give the pixel the label */
        ufind[label] = label; /* put the label in the equivalence array */
        largest[label] = 1;   /* the label has 1 pixel associated with it */
    } else {
        *buf = 0;
    }
    buf++;



    /* special case for first row.
           Go over the first row except the first pixel.
    */
    for(x = 1; x < w; x++) {
        if (bitmask_getbit(input, x, 0)) {
            if (*(buf-1)) {                    /* d label */
                *buf = *(buf-1);
            } else {                           /* create label */
                label++;
                *buf = label;
                ufind[label] = label;
                largest[label] = 0;
            }
            largest[*buf]++;
        } else {
            *buf = 0;
        }
        buf++;
    }



    /* the rest of the image */
    for(y = 1; y < h; y++) {
        /* first pixel of the row */
        if (bitmask_getbit(input, 0, y)) {
            if (*(buf-w)) {                    /* b label */
                *buf = *(buf-w);
            } else if (*(buf-w+1)) {           /* c label */
                *buf = *(buf-w+1);
            } else {                           /* create label */
                label++;
                *buf = label;
                ufind[label] = label;
                largest[label] = 0;
            }
            largest[*buf]++;
        } else {
            *buf = 0;
        }
        buf++;
        /* middle pixels of the row */
        for(x = 1; x < (w-1); x++) {
            if (bitmask_getbit(input, x, y)) {
                if (*(buf-w)) {                /* b label */
                    *buf = *(buf-w);
                } else if (*(buf-w+1)) {       /* c branch of tree */
                    if (*(buf-w-1)) {                      /* union(c, a) */
                        croot = root = *(buf-w+1);
                        while (ufind[root] < root) {       /* find root */
                            root = ufind[root];
                        }
                        if (croot != *(buf-w-1)) {
                            temp = aroot = *(buf-w-1);
                            while (ufind[aroot] < aroot) { /* find root */
                                aroot = ufind[aroot];
                            }
                            if (root > aroot) {
                                root = aroot;
                            }
                            while (ufind[temp] > root) {   /* set root */
                                aroot = ufind[temp];
                                ufind[temp] = root;
                                temp = aroot;
                            }
                        }
                        while (ufind[croot] > root) {      /* set root */
                            temp = ufind[croot];
                            ufind[croot] = root;
                            croot = temp;
                        }
                        *buf = root;
                    } else if (*(buf-1)) {                 /* union(c, d) */
                        croot = root = *(buf-w+1);
                        while (ufind[root] < root) {       /* find root */
                            root = ufind[root];
                        }
                        if (croot != *(buf-1)) {
                            temp = aroot = *(buf-1);
                            while (ufind[aroot] < aroot) { /* find root */
                                aroot = ufind[aroot];
                            }
                            if (root > aroot) {
                                root = aroot;
                            }
                            while (ufind[temp] > root) {   /* set root */
                                aroot = ufind[temp];
                                ufind[temp] = root;
                                temp = aroot;
                            }
                        }
                        while (ufind[croot] > root) {      /* set root */
                            temp = ufind[croot];
                            ufind[croot] = root;
                            croot = temp;
                        }
                        *buf = root;
                    } else {                   /* c label */
                        *buf = *(buf-w+1);
                    }
                } else if (*(buf-w-1)) {       /* a label */
                    *buf = *(buf-w-1);
                } else if (*(buf-1)) {         /* d label */
                    *buf = *(buf-1);
                } else {                       /* create label */
                    label++;
                    *buf = label;
                    ufind[label] = label;
                    largest[label] = 0;
                }
                largest[*buf]++;
            } else {
                *buf = 0;
            }
            buf++;
        }
        /* last pixel of the row, if its not also the first pixel of the row */
        if (w > 1) {
            if (bitmask_getbit(input, x, y)) {
                if (*(buf-w)) {                /* b label */
                    *buf = *(buf-w);
                } else if (*(buf-w-1)) {       /* a label */
                    *buf = *(buf-w-1);
                } else if (*(buf-1)) {         /* d label */
                    *buf = *(buf-1);
                } else {                       /* create label */
                    label++;
                    *buf = label;
                    ufind[label] = label;
                    largest[label] = 0;
                }
                largest[*buf]++;
            } else {
                *buf = 0;
            }
            buf++;
        }
    }

    return label;
}

/* Connected component labeling based on the SAUF algorithm by Kesheng Wu,
   Ekow Otoo, and Kenji Suzuki.  The algorithm is best explained by their paper,
   "Two Strategies to Speed up Connected Component Labeling Algorithms", but in
   summary, it is a very efficient two pass method for 8-connected components.
   It uses a decision tree to minimize the number of neighbors that need to be
   checked.  It stores equivalence information in an array based union-find.
   This implementation also has a final step of finding bounding boxes. */

/*
returns -2 on memory allocation error, otherwise 0 on success.

input - the input mask.
num_bounding_boxes - returns the number of bounding rects found.
rects - returns the rects that are found.  Allocates the memory for the rects.

*/
int internal_get_bounding_rects(bitmask_t *input, int *num_bounding_boxes, SDL_Rect** ret_rects)
{
    unsigned int *image, *ufind, *largest, *buf;
    int x, y, w, h, temp, label, relabel;
    SDL_Rect* rects;

    rects = NULL;
    label = 0;

    w = input->w;
    h = input->h;

    /* a temporary image to assign labels to each bit of the mask */
    image = (unsigned int *) malloc(sizeof(int)*w*h);
    if(!image) { return -2; }

    /* allocate enough space for the maximum possible connected components */
    /* the union-find array. see wikipedia for info on union find */
    ufind = (unsigned int *) malloc(sizeof(int)*(w/2 + 1)*(h/2 + 1));
    if(!ufind) { return -2; }

    largest = (unsigned int *) malloc(sizeof(int)*(w/2 + 1)*(h/2 + 1));
    if(!largest) { return -2; }


    /* do the initial labelling */
    label = cc_label(input, image, ufind, largest);

    relabel = 0;
    /* flatten and relabel the union-find equivalence array.  Start at label 1
       because label 0 indicates an unset pixel.  For this reason, we also use
       <= label rather than < label. */
    for (x = 1; x <= label; x++) {
         if (ufind[x] < x) {             /* is it a union find root? */
             ufind[x] = ufind[ufind[x]]; /* relabel it to its root */
         } else {                 /* its a root */
             relabel++;
             ufind[x] = relabel;  /* assign the lowest label available */
         }
    }

    *num_bounding_boxes = relabel;

    if (relabel == 0) {
    /* early out, as we didn't find anything. */
        free(image);
        free(ufind);
        free(largest);
        *ret_rects = rects;
        return 0;
    }

    /* the bounding rects, need enough space for the number of labels */
    rects = (SDL_Rect *) malloc(sizeof(SDL_Rect) * (relabel +1));
    if(!rects) { return -2; }

    for (temp = 0; temp <= relabel; temp++) {
        rects[temp].h = 0;        /* so we know if its a new rect or not */
    }

    /* find the bounding rect of each connected component */
    buf = image;
    for (y = 0; y < h; y++) {
        for (x = 0; x < w; x++) {
            if (ufind[*buf]) {         /* if the pixel is part of a component */
                if (rects[ufind[*buf]].h) {   /* the component has a rect */
                    temp = rects[ufind[*buf]].x;
                    rects[ufind[*buf]].x = MIN(x, temp);
                    rects[ufind[*buf]].y = MIN(y, rects[ufind[*buf]].y);
                    rects[ufind[*buf]].w = MAX(rects[ufind[*buf]].w + temp, x + 1) - rects[ufind[*buf]].x;
                    rects[ufind[*buf]].h = MAX(rects[ufind[*buf]].h, y - rects[ufind[*buf]].y + 1);
                } else {                      /* otherwise, start the rect */
                    rects[ufind[*buf]].x = x;
                    rects[ufind[*buf]].y = y;
                    rects[ufind[*buf]].w = 1;
                    rects[ufind[*buf]].h = 1;
                }
            }
            buf++;
        }
    }

    free(image);
    free(ufind);
    free(largest);
    *ret_rects = rects;

    return 0;
}

int get_connected_components(bitmask_t *mask, bitmask_t ***components, int min)
{
    unsigned int *image, *ufind, *largest, *buf;
    int x, y, w, h, label, relabel;
    bitmask_t** comps;

    label = 0;

    w = mask->w;
    h = mask->h;

    /* a temporary image to assign labels to each bit of the mask */
    image = (unsigned int *) malloc(sizeof(int)*w*h);
    if(!image) { return -2; }

    /* allocate enough space for the maximum possible connected components */
    /* the union-find array. see wikipedia for info on union find */
    ufind = (unsigned int *) malloc(sizeof(int)*(w/2 + 1)*(h/2 + 1));
    if(!ufind) {
        free(image);
        return -2;
    }

    largest = (unsigned int *) malloc(sizeof(int)*(w/2 + 1)*(h/2 + 1));
    if(!largest) {
        free(image);
        free(ufind);
        return -2;
    }

    /* do the initial labelling */
    label = cc_label(mask, image, ufind, largest);

    for (x = 1; x <= label; x++) {
        if (ufind[x] < x) {
            largest[ufind[x]] += largest[x];
        }
    }

    relabel = 0;
    /* flatten and relabel the union-find equivalence array.  Start at label 1
       because label 0 indicates an unset pixel.  For this reason, we also use
       <= label rather than < label. */
    for (x = 1; x <= label; x++) {
        if (ufind[x] < x) {             /* is it a union find root? */
            ufind[x] = ufind[ufind[x]]; /* relabel it to its root */
        } else {                 /* its a root */
            if (largest[x] >= min) {
                relabel++;
                ufind[x] = relabel;  /* assign the lowest label available */
            } else {
                ufind[x] = 0;
            }
        }
    }

    if (relabel == 0) {
    /* early out, as we didn't find anything. */
        free(image);
        free(ufind);
        free(largest);
        return 0;
    }

    /* allocate space for the mask array */
    comps = (bitmask_t **) malloc(sizeof(bitmask_t *) * (relabel +1));
    if(!comps) {
        free(image);
        free(ufind);
        free(largest);
        return -2;
    }

    /* create the empty masks */
    for (x = 1; x <= relabel; x++) {
        comps[x] = bitmask_create(w, h);
    }

    /* set the bits in each mask */
    buf = image;
    for (y = 0; y < h; y++) {
        for (x = 0; x < w; x++) {
            if (ufind[*buf]) {         /* if the pixel is part of a component */
                bitmask_setbit(comps[ufind[*buf]], x, y);
            }
            buf++;
        }
    }

    free(image);
    free(ufind);
    free(largest);

    *components = comps;

    return relabel;
}

int largest_connected_comp(bitmask_t* input, bitmask_t* output, int ccx, int ccy)
{
    unsigned int *image, *ufind, *largest, *buf;
    unsigned int max, x, y, w, h, label;

    w = input->w;
    h = input->h;

    /* a temporary image to assign labels to each bit of the mask */
    image = (unsigned int *) malloc(sizeof(int)*w*h);
    if(!image) { return -2; }
    /* allocate enough space for the maximum possible connected components */
    /* the union-find array. see wikipedia for info on union find */
    ufind = (unsigned int *) malloc(sizeof(int)*(w/2 + 1)*(h/2 + 1));
    if(!ufind) {
        free(image);
        return -2;
    }
    /* an array to track the number of pixels associated with each label */
    largest = (unsigned int *) malloc(sizeof(int)*(w/2 + 1)*(h/2 + 1));
    if(!largest) {
        free(image);
        free(ufind);
        return -2;
    }

    /* do the initial labelling */
    label = cc_label(input, image, ufind, largest);

    max = 1;
    /* flatten the union-find equivalence array */
    for (x = 2; x <= label; x++) {
         if (ufind[x] != x) {                 /* is it a union find root? */
             largest[ufind[x]] += largest[x]; /* add its pixels to its root */
             ufind[x] = ufind[ufind[x]];      /* relabel it to its root */
         }
         if (largest[ufind[x]] > largest[max]) { /* is it the new biggest? */
             max = ufind[x];
         }
    }

    /* write out the final image */
    buf = image;
    if (ccx >= 0)
        max = ufind[*(buf+ccy*w+ccx)];
    for (y = 0; y < h; y++) {
        for (x = 0; x < w; x++) {
            if (ufind[*buf] == max) {         /* if the label is the max one */
                bitmask_setbit(output, x, y); /* set the bit in the mask */
            }
            buf++;
        }
    }

    free(image);
    free(ufind);
    free(largest);

    return 0;
}

