# download_sentinel2_images_on_GEE
#======================================================================================

# Description

This repository contains a python code to download sentinel-2 images on GEE. Some images that can be download are :
 `RGB`, `MNDWI`, `NDWI`, `S2cloudless layer`, and the `mask cloud layer` (both for RGB and MNDWI).


# How it works

you need to have `Python (version 3 is preferable)` on your system

- Import the module
`from download_s2_GEE  import *`

- VARIABLE SETUP
 - GEE API

   `api = ee`
   
 - The boundary path : an GEE asset
 -  
   `boundaries_path = "PATH_TO_ASSET"`

 - Date range in which the data will be download
  
    `start_date = '2022-09-09'`

    `end_date = '2022-09-18'`

 -  Cloud filter percentage
   
    `cloud_percentage =100`
  
 - The Google drive folder in which the data will be stored
 
   `folder =  'earthengine'`

 -The method to apply to the image collection. There are 2 main method : mosaic and median

   `function= 'mosaic'

    generate_im1 = download_s2_images (api, boundaries_path, start_date,end_date, cloud_percentage=cloud_percentage, function=function, folder=folder)
`

-  Download MNDWI
  
  ` tasks = generate_im1.get_all_mosaic(["mndwi"]) 

    for tsk in tasks:

    tsk.start()
    `

- Download S2CLOUDLESS

`
tasks = generate_im1.get_all_mosaic(["cloud"])

for tsk in tasks:

    tsk.start()
    `

- Download RGB
  `
  tasks = generate_im1.get_all_mosaic(["rgb"])

  for tsk in tasks:

    tsk.start()
  `
