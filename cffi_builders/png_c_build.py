import cffi
from helpers import get_inc_dir, get_lib_dir


ffi = cffi.FFI()

ffi.cdef("""

// constants

#define PNG_COLOR_TYPE_RGB_ALPHA ...
#define PNG_COLOR_TYPE_RGB ...

// functions

static int write_png(const char *file_name, unsigned char **rows, int w, int h,
    int colortype, int bitdepth, char** error);

""")

pnglib = ffi.set_source(
    "pygame._png_c",
    libraries=['png'],
    include_dirs=get_inc_dir(),
    library_dirs=get_lib_dir(),
    source="""
    #define PNG_SKIP_SETJMP_CHECK 1
    #include <stdlib.h>
    #include <png.h>

    static void
    png_write_fn (png_structp png_ptr, png_bytep data, png_size_t length)
    {
        FILE *fp = (FILE *)png_get_io_ptr(png_ptr);
        if (fwrite(data, 1, length, fp) != length) {
            fclose(fp);
            png_error(png_ptr, "Error while writing to the PNG file (fwrite)");
        }
    }

    static void
    png_flush_fn (png_structp png_ptr)
    {
        FILE *fp = (FILE *)png_get_io_ptr(png_ptr);
        if (fflush(fp) == EOF) {
            fclose(fp);
            png_error(png_ptr, "Error while writing to PNG file (fflush)");
        }
    }

    static int write_png(const char *file_name,
                         png_bytep *rows,
                         int w,
                         int h,
                         int colortype,
                         int bitdepth,
                         char** error)
    {
        png_structp png_ptr = NULL;
        png_infop info_ptr =  NULL;
        FILE *fp = NULL;
        char *doing = "open for writing";

        if (!(fp = fopen (file_name, "wb")))
            goto fail;

        doing = "create png write struct";
        if (!(png_ptr = png_create_write_struct
              (PNG_LIBPNG_VER_STRING, NULL, NULL, NULL)))
            goto fail;

        doing = "create png info struct";
        if (!(info_ptr = png_create_info_struct (png_ptr)))
            goto fail;
        if (setjmp (png_jmpbuf (png_ptr)))
            goto fail;

        doing = "init IO";
        png_set_write_fn (png_ptr, fp, png_write_fn, png_flush_fn);

        doing = "write header";
        png_set_IHDR (png_ptr, info_ptr, w, h, bitdepth, colortype,
                      PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_BASE,
                      PNG_FILTER_TYPE_BASE);

        doing = "write info";
        png_write_info (png_ptr, info_ptr);

        doing = "write image";
        png_write_image (png_ptr, rows);

        doing = "write end";
        png_write_end (png_ptr, NULL);

        doing = "closing file";
        if(0 != fclose (fp))
            goto fail;
        png_destroy_write_struct(&png_ptr, &info_ptr);
        return 0;

    fail:
        /*
         * I don't see how to handle the case where png_ptr
         * was allocated but info_ptr was not. However, those
         * calls should only fail if memory is out and you are
         * probably screwed regardless then. The resulting memory
         * leak is the least of your concerns.
         */
        if( png_ptr && info_ptr ) {
            png_destroy_write_struct(&png_ptr, &info_ptr);
        }
        *error = malloc(50);
        sprintf(*error, "SavePNG: could not %s", doing);
        return -1;
    }
    """
)


if __name__ == "__main__":
    ffi.compile()
