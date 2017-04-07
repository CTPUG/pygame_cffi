import cffi
from helpers import get_inc_dir, get_lib_dir


ffi = cffi.FFI()

ffi.cdef("""

// functions

int write_jpeg (const char *file_name, unsigned char** image_buffer,
    int image_width, int image_height, int quality, char** error);

""")



jpglib = ffi.set_source(
    "pygame._jpg_c",
    libraries=['jpeg'],
    include_dirs=get_inc_dir(),
    library_dirs=get_lib_dir(),
    source="""
    #include <stdlib.h>
    #include <jpeglib.h>
    #include <jerror.h>

    #define NUM_LINES_TO_WRITE 500

    /* Avoid conflicts with the libjpeg libraries C runtime bindings.
     * Adapted from code in the libjpeg file jdatadst.c .
     *
     * Taken form pygame commit 010ef3d8c
     */

    #define OUTPUT_BUF_SIZE  4096   /* choose an efficiently fwrite'able size */

    /* Expanded data destination object for stdio output */
    typedef struct {
        struct jpeg_destination_mgr pub; /* public fields */

        FILE *outfile;    /* target stream */
        JOCTET *buffer;   /* start of buffer */
    } j_outfile_mgr;

    static void
    j_init_destination (j_compress_ptr cinfo)
    {
        j_outfile_mgr *dest = (j_outfile_mgr *) cinfo->dest;

        /* Allocate the output buffer --- it will be released when done with image */
        dest->buffer = (JOCTET *)
            (*cinfo->mem->alloc_small) ((j_common_ptr) cinfo, JPOOL_IMAGE,
                                                OUTPUT_BUF_SIZE * sizeof(JOCTET));

        dest->pub.next_output_byte = dest->buffer;
        dest->pub.free_in_buffer = OUTPUT_BUF_SIZE;
    }

    static boolean
    j_empty_output_buffer (j_compress_ptr cinfo)
    {
        j_outfile_mgr *dest = (j_outfile_mgr *) cinfo->dest;

        if (fwrite(dest->buffer, 1, OUTPUT_BUF_SIZE, dest->outfile) !=
            (size_t) OUTPUT_BUF_SIZE) {
            ERREXIT(cinfo, JERR_FILE_WRITE);
        }
        dest->pub.next_output_byte = dest->buffer;
        dest->pub.free_in_buffer = OUTPUT_BUF_SIZE;

        return TRUE;
    }

    static void
    j_term_destination (j_compress_ptr cinfo)
    {
        j_outfile_mgr *dest = (j_outfile_mgr *) cinfo->dest;
        size_t datacount = OUTPUT_BUF_SIZE - dest->pub.free_in_buffer;

        /* Write any data remaining in the buffer */
        if (datacount > 0) {
            if (fwrite(dest->buffer, 1, datacount, dest->outfile) != datacount) {
                ERREXIT(cinfo, JERR_FILE_WRITE);
            }
        }
        fflush(dest->outfile);
        /* Make sure we wrote the output file OK */
        if (ferror(dest->outfile)) {
            ERREXIT(cinfo, JERR_FILE_WRITE);
        }
    }

    static void
    j_stdio_dest (j_compress_ptr cinfo, FILE *outfile)
    {
        j_outfile_mgr *dest;

      /* The destination object is made permanent so that multiple JPEG images
       * can be written to the same file without re-executing jpeg_stdio_dest.
       * This makes it dangerous to use this manager and a different destination
       * manager serially with the same JPEG object, because their private object
       * sizes may be different.  Caveat programmer.
       */
        if (cinfo->dest == NULL) {  /* first time for this JPEG object? */
            cinfo->dest = (struct jpeg_destination_mgr *)
                (*cinfo->mem->alloc_small) ((j_common_ptr) cinfo, JPOOL_PERMANENT,
                                            sizeof(j_outfile_mgr));
        }

        dest = (j_outfile_mgr *) cinfo->dest;
        dest->pub.init_destination = j_init_destination;
        dest->pub.empty_output_buffer = j_empty_output_buffer;
        dest->pub.term_destination = j_term_destination;
        dest->outfile = outfile;
    }

    /* End borrowed code
     */

    int write_jpeg (const char *file_name, unsigned char** image_buffer,
                int image_width, int image_height, int quality, char** error) {

        struct jpeg_compress_struct cinfo;
        struct jpeg_error_mgr jerr;
        FILE * outfile;
        JSAMPROW row_pointer[NUM_LINES_TO_WRITE];
        int row_stride;
        int num_lines_to_write;
        int lines_written;
        int i;

        row_stride = image_width * 3;

        num_lines_to_write = NUM_LINES_TO_WRITE;


        cinfo.err = jpeg_std_error (&jerr);
        jpeg_create_compress (&cinfo);

        if ((outfile = fopen (file_name, "wb")) == NULL) {
            *error = malloc(100);
            snprintf(*error, 100, "SaveJPEG: could not open %s", file_name);
            return -1;
        }
        j_stdio_dest (&cinfo, outfile);

        cinfo.image_width = image_width;
        cinfo.image_height = image_height;
        cinfo.input_components = 3;
        cinfo.in_color_space = JCS_RGB;
        /* cinfo.optimize_coding = FALSE;
         */
        /* cinfo.optimize_coding = FALSE;
         */

        jpeg_set_defaults (&cinfo);
        jpeg_set_quality (&cinfo, quality, TRUE);

        jpeg_start_compress (&cinfo, TRUE);



        /* try and write many scanlines at once.  */
        while (cinfo.next_scanline < cinfo.image_height) {
            if (num_lines_to_write > (cinfo.image_height - cinfo.next_scanline) -1) {
                num_lines_to_write = (cinfo.image_height - cinfo.next_scanline);
            }
            /* copy the memory from the buffers */
            for(i =0; i < num_lines_to_write; i++) {
                row_pointer[i] = image_buffer[cinfo.next_scanline + i];
            }


            /*
            num_lines_to_write = 1;
            row_pointer[0] = image_buffer[cinfo.next_scanline];
               printf("num_lines_to_write:%d:   cinfo.image_height:%d:  cinfo.next_scanline:%d:\n", num_lines_to_write, cinfo.image_height, cinfo.next_scanline);
            */


            lines_written = jpeg_write_scanlines (&cinfo, row_pointer, num_lines_to_write);

            /*
               printf("lines_written:%d:\n", lines_written);
            */

        }

        jpeg_finish_compress (&cinfo);
        fclose (outfile);
        jpeg_destroy_compress (&cinfo);
        return 0;
    }
    """
)


if __name__ == "__main__":
    ffi.compile()
