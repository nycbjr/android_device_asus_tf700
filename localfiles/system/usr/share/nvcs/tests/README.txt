The purpose of these scripts is to test NVCS (Nvidia Camera Scripting) interface.
NVCS is a python scripting interface for camera. We can either run group of sanity
tests or pick and choose tests that we want to run. The usage and the description
of the tests and scripts are given below.

Usage: nvcstestmain.py <options>

Options:
  -h, --help    show this help message and exit
  -s            Run Sanity tests
  -t TEST_NAME  Test name to execute
  -d TEST_NAME  Disable the test
  -i IMAGER_ID  set imager id. 0 for rear facing, 1 for front facing


==============================================
options description:

-s
    runs the sanity tests
        "jpeg_capture"
        "raw_capture"
        "concurrent_raw"
        "exposuretime"
        "iso"
        "focuspos"

-t TEST_NAME

    runs the TEST_NAME. Multiple -t arguments are supported.

-d TEST_NAME

    disables the TEST_NAME. multiple -d arguments are supported.

==============================================
Result:
    Result images and logs are stored under /data/NVCSTest directory.

    Each test will have directory under /data/NVCSTest, which should have
    result images for that test

    Summary log is saved at /data/NVCSTest/summarylog.txt


==============================================
List of tests:

"jpeg_capture"
    captures a jpeg image

"raw_capture"
    captures a raw image and checks for the existence of the raw image.

"concurrent_raw"
    captures a jpeg+raw image concurrently. Checks the max pixel value (should be <= 1023)

"exposuretime"
    captures concurrent jpeg+raw images, setting the exposuretime in the range [10, 100]ms in the 10ms intervals. Checks the exposure value in the header
    and value returned from the get attribute function

"gain"
    captures concurrent jpeg+raw images, setting the gain in the range [1, 10] in the intervals of 1. Checks the sensor gains value in the raw header
    and value returned from the get attribute function.

"focuspos"
    captures  concurrent jpeg+raw images, setting the focuspos in the range [0, 1000] in the intervals of 100. Checks the focuspos in the raw header
    and value returned from the get attribute function.

"multiple_raw"
    captures 100 concurrent jpeg+raw images. Checks for the existence of raw images and the max pixel value (should be <= 1023)

