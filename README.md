# download_sentinel2_images_on_GEE
#======================================================================================

# Description
"""
This repository contains a python code to download sentinel-2 images on GEE. Some images that can be download are :
 `RGB`, `MNDWI`, `NDWI`, `S2cloudless layer`, and the `mask cloud layer` (both for RGB and MNDWI).
"""

# How it works
you need to have `Python (version 3 is preferable)` on your system
- Import the module
`from download_s2_GEE  import *`

-  Download MNDWI
tasks = generate_im1.get_all_mosaic(["mndwi"])
for tsk in tasks:
    tsk.start()


- Download S2CLOUDLESS
tasks = generate_im1.get_all_mosaic(["cloud"])
for tsk in tasks:
    tsk.start()

- Download RGB
tasks = generate_im1.get_all_mosaic(["rgb"])
for tsk in tasks:
    tsk.start()
