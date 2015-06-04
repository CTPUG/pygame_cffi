
import cffi

ffi = cffi.FFI()

ffi.cdef("""

// functions

int write_jpeg (const char *file_name, unsigned char** image_buffer,
    int image_width, int image_height, int quality, char** error);

""")

jpglib = ffi.set_source(
    "pygame._jpg_c",
    libraries=['jpeg'],
    source="""
    #include <stdlib.h>
    #include <jpeglib.h>

    #define NUM_LINES_TO_WRITE 500


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
        jpeg_stdio_dest (&cinfo, outfile);

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
