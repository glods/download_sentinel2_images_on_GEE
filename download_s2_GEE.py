""" Remote Sensing  Predictables  - Download Sentinel-2 data V2

Created on May 13, 2022 

#======================================================================================
# Description
#====================================================================================
"""
This file shows how to download sentinel-2 images on GEE. Some images that can be download are :
 RGB, MNDWI, NDWI, S2cloudless layer, and the mask cloud layer (both for RGB and MNDWI).

"""

#========================================================================================
#============================ LOADING PACKAGES 
# =====================================================================================

# import datetime packages
from datetime import datetime, date, timedelta


# Login into GEE
# import ee
# ee.Authenticate()
# ee.Initialize()

#========================================================================================
#==========================  S2 DOOWNLOAD MODULE 
#========================================================================================


class download_s2_images(object):
  """
    Description:
      download sentinel 2 data on Google earth engine based on some criteria
  """          

  #================================================================================================
  #
  #================================================================================================
  def  __init__(self, api, boundaries_path, start_date,end_date, cloud_percentage,function='mosaic', folder = 'earthengine'):
    """
      Description: 
        This method is called when an object is created from the class download_s2_images and it allow the class to initialize the attributes
      Args: 
        @ api : google earth engine API
        @ boundaries_path : path to the GEE asset for the boundary
        @ start_date , end_date : range in which the data will be downloaded
        @ function [mosaic, median] : which method to apply to the image collection
        @ folder : where images will be store on the google drive
      Returns:
        
    """
    if not os.path.exists(folder):
      os.makedirs(folder)

    self.api = api
    self.boundaries_path=boundaries_path 
    self.start_date = start_date 
    self.end_date = end_date 
    self.cloud_percentage = cloud_percentage 
    self.function = function
    self.folder = folder
    

  #================================================================================================
  #  GEOMETRY
  #================================================================================================
  def getGeometry(self):
    """
      Description: 
      Args: 
        @ self : boundary
      Returns:
        - The geomtry   
    """
    
    area = self.api.FeatureCollection(self.boundaries_path);
    return  area.geometry()


  #================================================================================================
  #
  #================================================================================================
  def setImage(self, start_date, end_date):
    """
      Description: 
        Create an image colection from a give date range
      Args: 
        @ self: 
        @ start_date 
        @ end_date  
      Returns:
        - Collection of images  
    """

    s2 = self.api.ImageCollection("COPERNICUS/S2_SR")
    geometry = self.getGeometry()
    filtered = s2.filter(self.api.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', self.cloud_percentage)).filter(self.api.Filter.date(start_date , end_date)).filter(self.api.Filter.bounds(geometry))
    # image = ''
    # if function =='median':
    #   image = filtered.median()
    # elif function =='mosaic':
    #   image = filtered.mosaic()
    return filtered

  #================================================================================================
  #
  #================================================================================================

  def getImages(self):
    """
      Description: 
        Create an image colection from the properties of the class 
      Args: 
        @ self: 
      Returns:
        - Collection of images  
    """

    s2 = self.api.ImageCollection("COPERNICUS/S2_SR")
    geometry = self.getGeometry()
    filtered = s2.filter(self.api.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', self.cloud_percentage)).filter(self.api.Filter.date(self.start_date , self.end_date)).filter(self.api.Filter.bounds(geometry))
    return filtered

  #================================================================================================
  #
  #================================================================================================
# Create a composite and apply cloud mask
  def getMask_images(self, snow_probability=5 , cloud_probability =30):
    """
      Description: 
         masking clouds and cloud shadows in Sentinel-2 (S2) surface reflectance (SR).
          Clouds are identified from the S2 cloud probability dataset (s2cloudless).
      Args: 
        @ self: 
      Returns:
        - Cloud mask image collection 
    """
    # Cloud masking
    def maskCloudAndShadows(image):
      cloudProb = image.select('MSK_CLDPRB')
      snowProb = image.select('MSK_SNWPRB')
      cloud = cloudProb.lt(cloud_probability)
      snow = snowProb.lt(snow_probability)
      scl = image.select('SCL')
      # shadow = scl.eq(3); # 3 = cloud shadow
      # cirrus = scl.eq(30); # 10 = cirrus
      # Cloud probability less than x% or cloud shadow classification
      mask = cloud #.And(snow) #.And(cirrus.neq(1)).And(shadow.neq(1))
      return image.updateMask(mask)

    s2 = self.api.ImageCollection("COPERNICUS/S2_SR")
    geometry = self.getGeometry()
    filtered = s2.filter(self.api.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', self.cloud_percentage)).filter(self.api.Filter.date(self.start_date , self.end_date)).map(maskCloudAndShadows).filter(self.api.Filter.bounds(geometry))
    return filtered

  #================================================================================================
  #
  #================================================================================================
  def setMask_images(self, start_date, end_date,  snow_probability=5 , cloud_probability =40):
    """
      Description: 
         masking clouds and cloud shadows in Sentinel-2 (S2) surface reflectance (SR) 
          Clouds are identified from the S2 cloud probability dataset (s2cloudless).
      Args: 
        
        @ self:
        @ start_date
        @ end_date 
      Returns:
        - Cloud mask image collection 
    """

    # Cloud masking
    def maskCloudAndShadows(image):
      cloudProb = image.select('MSK_CLDPRB')
      snowProb = image.select('MSK_SNWPRB')
      cloud = cloudProb.lt(cloud_probability)
      snow = snowProb.lt(snow_probability)
      scl = image.select('SCL')
      # Cloud probability less than 5% or cloud shadow classification
      mask = cloud #.And(snow) #.And(cirrus.neq(1)).And(shadow.neq(1))
      return image.updateMask(mask)

    s2 = self.api.ImageCollection("COPERNICUS/S2_SR")
    geometry = self.getGeometry()
    filtered = s2.filter(self.api.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', self.cloud_percentage)).filter(self.api.Filter.date(start_date , end_date)).map(maskCloudAndShadows).filter(self.api.Filter.bounds(geometry))
    return filtered




  #================================================================================================
  #  
  #================================================================================================

  def gets2cloudless(self):
      """
        Description: 
          get a cloud probability dataset (s2cloudless).
        Args: 
          @ self:
          @ start_date, end_date : date range
        Returns:
          - cloud probability dataset collection 
      """

      s2_cloudless_col = (self.api.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
          .filterBounds(self.getGeometry())
          .filterDate(self.start_date, self.end_date))
      return s2_cloudless_col

  #================================================================================================
  #
  #================================================================================================
  def collectByDate(self, imgCol, next_date=1):
        '''
        a function that merges images together (mosaic or median) that have the same date if next_date =1 or 
        or merge together images of a given date and the one that come the x (next_date) date after

        @ imgCol: [ee.ImageCollection] mandatory value that specifies the image collection to merge by dates with.

        Returns ee.ImageCollection
        '''
        #Convert the image collection to a list.
        imgList = imgCol.toList(imgCol.size())
        
        # Driver function for mapping the unique dates
        def uniqueDriver(image):
            return self.api.Image(image).date().format("YYYY-MM-dd")
        
        uniqueDates = imgList.map(uniqueDriver).distinct()

        # Driver function for mapping the images
        def collectDriver(date):
            date = self.api.Date(date)
            if self.function == 'mosaic':
              image = (imgCol
                    .filterDate(date, date.advance(next_date, "day"))
                    .mosaic())
            elif self.function== 'median':
              image = (imgCol
                    .filterDate(date, date.advance(next_date, "day"))
                    .median())
            
            return image.set(
                            "system:time_start", date.millis(), 
                            "system:id", date.format("YYYY-MM-dd"))
        
        mosaicImgList = uniqueDates.map(collectDriver)
        
        return self.api.ImageCollection(mosaicImgList)

  #==============================================================================================
  #-----------------------------------MWASK PERMANENT WATER
  #=================================================================================================
  def mask_permanent_water(self, init_image , date_range_ =['2021-01-01' ,'2021-01-10'] ):
          di = date_range_[0] # init_date
          df = date_range_[1] # end_date
          image1 = self.api.ImageCollection("COPERNICUS/S2_SR").filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 15)).filter(ee.Filter.date(di, df)).select('B.*', 'SCL').filter(ee.Filter.bounds(self.getGeometry())).mosaic()

          swi= image1.normalizedDifference(['B3', 'B11']).rename(['swi']); 
          swi_mask = swi.gt(0).updateMask(swi.gt(0));

      #  Include JRC layer on surface water seasonality to mask flood pixels from areas
      #  of "permanent" water (where there is water > 2 months of the year)
          single_img = init_image
          swater = ee.Image('JRC/GSW1_0/GlobalSurfaceWater').select('seasonality');  
          swater_mask = swater.gte(2).updateMask(swater.gte(2));  
          single_img_up = single_img.where(swater_mask,100);  
          
          single_img  = single_img_up .where(swi_mask,100);
          single_img  = single_img .updateMask(single_img.neq(100));
          return single_img

  #================================================================================================
  #    INITIALISE A TASK
  #================================================================================================
  def getTask(self, image, filename):
    """
        Description: 
          a function that generate a task  
        Args: 
          @ self:
          @ image : 
          @ file_name : 
          @ start_date, end_date : date range
        Returns:
          -  a GEE task
    """
    aoi = self.getGeometry()
    task = self.api.batch.Export.image.toDrive(
       **{
                 'image': image,
                 'description':filename,
                 'folder': self.folder,
                 'fileNamePrefix':filename,
                  'region': aoi,
                  'scale': 10,
                  'maxPixels': 1e12,
                  'fileFormat': "GeoTIFF",
         }
       )
    return task
    
  #================================================================================================
  # NDVI TASK
  #================================================================================================
  def getNDVI_task(self, ndvi_name, image):
    """
        Description: 
          a function that generate a task  to download NDVI images
        Args: 
          @ self:
          @ ndvi_name  : name of the images 

        Returns:
          -  a task
    """
    ndvi_name = ndvi_name #+ 'ndvi_'+ self.start_date+'to'+ self.end_date +'_cloudval-'+ str(self.cloud_percentage)
    print(ndvi_name)
    geometry = self.getGeometry()
    image = image 
    #print('image')
    #print(image)
    ndvi = image.normalizedDifference(['B8', 'B4']).rename(['ndvi']);
    #print(ndvi)
    visualized_ndvi = ndvi.clip(geometry)
 
    task = self.getTask(visualized_ndvi, ndvi_name  )
    return  task

  #================================================================================================
  # MNDWI TASK
  #================================================================================================
  def getMNDWI_task(self, mndwi_name, image):
    """
        Description: 
          a function that generate a task  to download MNDWI images
        Args: 
          @ self:
          @ mndwi_name  : name of the images 

        Returns:
          -  a task
    """
    mndwi_name = mndwi_name #+'_mndwi_' #+ self.start_date+'to'+ self.end_date +'_cloudval-'+ str(self.cloud_percentage)
    geometry = self.getGeometry()
    image = image

    mndwiVis = {'min':0, 'max':0.5, 'palette': ['white', 'blue']}
    mndwi = image.normalizedDifference(['B3', 'B11']).rename(['mndwi']);
    
    #==========================MASK PERMANENT WATER===============================

    #========================== MASK PERMANENT WATER===============================

    visualized_mndwi = mndwi.clip(geometry)

    # task = self.getTask(color_mndwi ,mndwi_name)
    task = self.getTask(visualized_mndwi,mndwi_name)
    return task



  #================================================================================================
  #
  #================================================================================================
  def getNDWI_task(self, ndwi_name, image):
    """
        Description: 
          a function that generate a task  to download NDWI images
        Args: 
          @ self:
          @ ndwi_name  : name of the images 

        Returns:
          -  a task
    """
    ndwi_name = ndwi_name # + 'ndwi_' +self.start_date+'to'+ self.end_date +'_cloudval-'+ str(self.cloud_percentage)
    geometry = self.getGeometry()
    image = image

    ndwi = image.normalizedDifference(['B8', 'B11']).rename(['ndwi']); 
    visualized_ndwi = ndwi.clip(geometry)

    task = self.getTask(visualized_ndwi, ndwi_name )
    return task

  #================================================================================================
  #  RGB TASK
  #================================================================================================
  def getrgb_img_task(self, rgb_name, image):
    """
        Description: 
          a function that generate a task  to download RGB images
        Args: 
          @ self:
          @ rgb_name  : name of the images 

        Returns:
          -  a task
    """

    rgb_name = rgb_name 
    geometry = self.getGeometry()
    image = image
    rgbVis = {
      'min': 0.0,
      'max': 3000,
      'bands': ['B4', 'B3', 'B2']
      } 

    visualized_rgb = image.clip(geometry).visualize(**rgbVis); #.visualize(image)

    task1 = self.getTask(visualized_rgb, rgb_name )
    
    return task1

  #================================================================================================
  #  S2CLOUDLESS TASK
  #================================================================================================
  def getS2cloudless_task(self,cloud_name, image):
    """
        Description: 
          a function that generate a task  to download CLOUD PROBABILITY images
        Args: 
          @ self:
          @ cloud_name  : name of the images

        Returns:
          -  a task
    """
    geometry = self.getGeometry()
    image = image
    cloud_img = image.clip(geometry)

    task = self.getTask(cloud_img, cloud_name)
    return task



  #================================================================================================
  # SWI TASK
  #================================================================================================
  def getSWI_task(self, swi_name, image =False):
    """
        Description: 
          a function that generate a task  to download SWI images
        Args: 
          @ self:
          @ swi_name  : name of the images 

        Returns:
          -  a task
    """
    swi_name = swi_name #+'_mndwi_' #+ self.start_date+'to'+ self.end_date +'_cloudval-'+ str(self.cloud_percentage)
    geometry = self.getGeometry()
    if image==False:
      image = self.getImage() 
    else:
      image = image
    swiVis = {'min':0, 'max':0.5, 'palette': ['white', 'blue']}
    swi = image.normalizedDifference(['B5', 'B11']).rename(['swi']);
    visualized_swi = swi.clip(geometry)

    task = self.getTask(visualized_swi,swi_name)
    return task
   #-----------------------------------------------------------------------------------------------
    #                       CALL TASKS
    #-----------------------------------------------------------------------------------------
  def call_task(self, types, image_name, single_img ):
            
        if 'rgb' in types:

          return (self.getrgb_img_task('rgb_'+image_name ,single_img))
          
        if 'mndwi' in types:
          return (self.getMNDWI_task('mndwi_'+image_name ,single_img))

        if 'ndvi' in types:
          return (self.getNDVI_task('ndvi_'+image_name ,single_img))

        if 'swi' in types:
          return (self.getNDVI_task('swi_'+image_name ,single_img))

        if 'ndwi' in types:
          return (self.getNDVI_task('ndwi_'+image_name ,single_img))
  

  def call_viz_image(self, types, single_img ):

      if 'rgb' in types:
            rgbVis = {
              'min': 0.0,
              'max': 3000,
              'bands': ['B4', 'B3', 'B2']
              } 

            visualized_im  = single_img.clip(  self.getGeometry()).visualize(**rgbVis)

            # visualized_im  = visualized_im .updateMask(visualized_im .gt(0))
            return  visualized_im
            # list_images.append(visualized_rgb)
            # list_image_names.append(str(date))

      if 'ndvi' in types:
            ndvim = single_img.normalizedDifference(['B8', 'B4']).rename(['ndvi']);
            Vis = {'min':0, 'max':0.8, 'palette': ['white', 'green']}
            visualized_im = ndvim.clip(  self.getGeometry()).visualize(**Vis)
            return  visualized_im

      if 'mndwi' in types:
            ndvim = single_img.normalizedDifference(['B3', 'B11']).rename(['ndvi']);
            Vis = {'min':0, 'max':0.8, 'palette': ['white', 'blue']}
            visualized_im = ndvim.clip(  self.getGeometry()).visualize(**Vis)
            return  visualized_im

      if 'swi' in types:
            ndvim = single_img.normalizedDifference(['B5', 'B11']).rename(['ndvi']);
            Vis = {'min':0, 'max':0.8, 'palette': ['white', 'blue']}
            visualized_im = ndvim.clip(  self.getGeometry()).visualize(**Vis)
            return  visualized_im

      if 'ndwi' in types:
            ndvim = single_img.normalizedDifference(['B8', 'B11']).rename(['ndvi']);
            Vis = {'min':0, 'max':0.8, 'palette': ['white', 'blue']}
            visualized_im = ndvim.clip(  self.getGeometry()).visualize(**Vis)
            return  visualized_im


#========================================================
# ------------------------USEFULL FUNCTION
#============================================================
  def export_geemap_to_html(self,list_images, list_image_names, output_folder, centerpoint = [0,0,2]):

    i =0
    Map = geemap.Map(toolbar_ctrl=True, layer_ctrl=True)
    aoi = self.getGeometry()
    Map.addLayer(aoi,{},' Contour')

    Vis = {'min':-20, 'max':0, 'palette': ['white', 'grey']}
    for image in list_images:
      # Map.addLayer(image, Vis, list_image_names[i] )
      Map.addLayer(image, {}, list_image_names[i] )
      i+=1

    download_dir = os.path.join(os.path.expanduser(output_folder), 'HTML_MAPS')

    if not os.path.exists(download_dir):
      os.makedirs(download_dir)

    datetime_object = datetime.now()
    html_name ='my_map'+ str(datetime_object).split(' ') [0] + str(datetime_object).split(' ') [1].split(':')[0]  + str(datetime_object).split(' ') [1].split(':')[1] +  str(datetime_object).split(' ') [1].split(':')[2].split('.')[1] +'.html'

    html_file = os.path.join(download_dir, html_name)

    # Map.to_html(filename=html_file, title='My Map', width='100%', height='580px')
    
    
    Map.setCenter(lon=centerpoint[0] , lat=centerpoint [1], zoom= centerpoint [2] )
    Map.to_html(filename=html_file, title='My Map', width='100%', height='580px')
    
              
    return Map

  #================================================================================================
  #
  #================================================================================================

  def getAll_images(self, types=['mndwi','rgb', 'cloud', 'swi'], mask=False, mask_water = False,image_intersect=False,export_image= False, next_date=1, snow_probability=5, cloud_probability =30 ):
    """
        Description: 
          a function to downlaod all images  of a given date range 
        Args: 
          @ self:
          @ types :  type of images to be downloaded
          @ mask : when True the cloud mask image is downloaded
          @ next_date : define the next image to used to the collection when a mosaic / median method will be applied
        Returns:
          -  image 
    """
    # Mask pixels
    if mask == False:
      collection  = self.collectByDate(self.getImages(), next_date=next_date)
      image_list = collection.toList(collection.size())

      img_size =  image_list .size().getInfo()
      # img_size_s2cl = image_s2cloudless_list.size().getInfo()

      print('size collection',image_list.size().getInfo())
      tasks =[]
      list_images = []
      list_image_names = []

      for i in range(img_size):
        single_img = self.api.ImageCollection([image_list .get(i), image_list .get(i)]).mosaic();

        date =  self.api.Image(image_list.get(i)).date().format("YYYY-MM-dd").getInfo()
        image_name = str(date) + '_' + str(date) +'plus'+str(next_date)


        if image_intersect!=False:
          single_img = self.img_intersection(image_intersect, single_img)

        # if mask_water == False :
        #   tasks.append (self.call_task(types, image_name, single_img ))
        if mask_water != False :
          single_img  = self.mask_permanent_water( single_img , date_range_ =[mask_water[0] ,mask_water[1]] )
          
        # tasks.append (self.call_task(types, image_name, single_img ))
#----------------------------------------------
        #=dON T EXPORTIMAGES
        if (export_image == False and 'cloud' not in types):
          tasks.append (self.call_task(types, image_name, single_img ))

        # visualized_im = ''
        if (export_image!=False):
          visualized_im  = self.call_viz_image(types, single_img )
          list_images.append (visualized_im  )
          list_image_names.append(str(date))


      if "cloud" in types:
            # get s2cloudless images
            error = False
            try:
              collection_s2cloudless =self.collectByDate(self.gets2cloudless(), next_date=next_date,)
              image_lists2cloudless = collection_s2cloudless.toList(collection_s2cloudless.size())
            except:
              error = True
              print('No S2 cloudless layer available')
            #print('error', error)
            image_s2cloudless_list = collection_s2cloudless.toList(
                    collection_s2cloudless.size()
                )
            print('size collection cloud ',image_s2cloudless_list.size().getInfo())

            img_size_s2cl = image_s2cloudless_list.size().getInfo()
            for i in range(img_size_s2cl):
                single_img = self.api.ImageCollection(
                    [image_s2cloudless_list.get(i), image_s2cloudless_list.get(i)]
                ).mosaic()

                date_cloudy = (
                    self.api.Image(image_s2cloudless_list.get(i))
                    .date()
                    .format("YYYY-MM-dd")
                    .getInfo()
                )

                image_name_cloudy = str(date_cloudy) + '_' + str(date_cloudy) +'plus'+str(next_date)
                # if "cloud" in types:
                tasks.append(
                        self.getS2cloudless_task(
                            "cloud_" + image_name_cloudy   , single_img
                        )
                    )
      


      # return tasks
      if (export_image == False):
        return tasks
      if (export_image!=False):
        # centerpoint  = [-16,16.3, 9.5]
        # list_images = [image, image]
        res = self.export_geemap_to_html(list_images, list_image_names, self.folder, centerpoint = export_image)
        return res
    #=================================================================================

    else:  # GET IMAGES WITH MASK  PIXELS

    
      collection  = self.collectByDate(self.getMask_images( snow_probability=snow_probability,cloud_probability = snow_probability), next_date=next_date)
      # get s2cloudless images

      image_list = collection.toList(collection.size())
      img_size =  image_list .size().getInfo()

      print('size collection mask',image_list.size().getInfo())
      tasks =[]

      list_images = []
      list_image_names = []

      for i in range(img_size):
        single_img = self.api.ImageCollection([image_list .get(i), image_list .get(i)]).mosaic();
        date =  self.api.Image(image_list.get(i)).date().format("YYYY-MM-dd").getInfo()
        image_name = str(date) + '_' + str(date) +'plus'+str(next_date)

        if image_intersect!=False:
          single_img = self.img_intersection(image_intersect, single_img)

        if mask_water != False :
          single_img  = self.mask_permanent_water( single_img , date_range_ =[mask_water[0] ,mask_water[1]] )
          

        if (export_image == False):
          tasks.append (self.call_task(types, image_name, single_img ))

        # visualized_im = ''
        if (export_image!=False): 

          visualized_im  = self.call_viz_image(types, single_img )

          list_images.append (visualized_im  )
          list_image_names.append(str(date))
        # tasks.append (self.call_task(types, image_name, single_img ))


      # return tasks
      if (export_image == False):
        
        return tasks
      if (export_image!=False):
        # centerpoint  = [-16,16.3, 9.5]
        # list_images = [image, image]
        res = self.export_geemap_to_html(list_images, list_image_names, self.folder, centerpoint = export_image)
        return res
      # return tasks



  #================================================================================================
  #
  #================================================================================================
# Download data by intervals

  def from_date_to_doy(self, x):
      return datetime.strptime(str(x) ,"%Y-%m-%d").timetuple().tm_yday

  def from_doy_to_date(self,doy, year):
      # Initializing start date
      strt_date = date(int(year), 1, 1)
      # converting to date
      res_date = strt_date + timedelta(days=int(doy) - 1)
      res = res_date.strftime("%Y-%m-%d")
      #print(res)
      return res


  def date_range(self,start, end, distance):
      '''
          Given a date range [start,end], the function  break it up into N contiguous
          sub-intervals distant from a value
      '''
      from datetime import datetime
      start_list =[]
      
      start = datetime.strptime(start,"%Y-%m-%d")
      start_list.append(start)
      end = datetime.strptime(end,"%Y-%m-%d")
      j=0
      i = start
      yield start.strftime("%Y-%m-%d")
      while i <= end :

          # print(j)
          # print(start_list[j] )
          result = (start_list[j] + timedelta(days=distance,)).strftime("%Y-%m-%d")
          print(datetime.strptime(result,"%Y-%m-%d"))
          yield result
          start_list.append(  datetime.strptime( (start_list[j] + timedelta(days=distance,)).strftime("%Y-%m-%d")  ,"%Y-%m-%d")     )
          i = datetime.strptime(result,"%Y-%m-%d")
          j=j+1


  #================================================================================================
  #
  #================================================================================================
  def getAll_images_by_interval(self, types=['mndwi','rgb', 'cloud'], mask=False, mask_water=False, export_image = False, image_intersect=False, interval =5):
    """
        Description: 
          a function to downlaod images by setting up the interval range based on the date range   
        Args: 
          @ self:
          @ types :  type of images to be downloaded
          @ mask : when True the cloud mask image is downloaded
          @ interval : distance between 2 dates. The default value is 5 as a single Sentinel-2 satellite
           is able to map the global landmasses once every 5 days
        Returns:
          -  an image 
    """
    # global  date_range_list
    if mask ==False:
      try:
        collection  = self.collectByDate(self.getImages())
        image_list = collection.toList(collection.size())
      except:
        print('No image available - interval ')
      
      
      date1 =  self.api.Image(image_list.get(0)).date().format("YYYY-MM-dd").getInfo()
      datei = self.from_date_to_doy(date1)

      list_interval = [ self.from_date_to_doy(date1) ]
      cpt=1

      while datei < self.from_date_to_doy(self.end_date) + interval :
          datei = datei + interval
          list_interval.append( datei )

      # date_range_list = list(self.date_range(self.start_date, self.end_date, list_interval))[:-1]
      date_range_list = list(self.date_range ( str(date1) , self.end_date, interval) )


      img_size =  image_list .size().getInfo()
    
      print('size collection',image_list.size().getInfo())

      tasks =[]
      list_images=[] 
      list_image_names = []

      print('date_range_list', date_range_list)

      for i in range (len(date_range_list) - 1 ):
        start_date = date_range_list [i]
        end_date =  date_range_list [i+1]

        if self.function == 'mosaic':
          single_img = self.setImage(start_date, end_date).mosaic()
        elif self.function == 'median':
          single_img = self.setImage(start_date, end_date).median()

        date = start_date + '_' +end_date   #self.api.Image(image_list.get(i)).date().format("YYYY-MM-dd").getInfo()
        image_name =date

        if image_intersect!=False:
          single_img = self.img_intersection(image_intersect, single_img)
          
        if mask_water != False :
          single_img  = self.mask_permanent_water( single_img , date_range_ =[mask_water[0] ,mask_water[1]] )
          
        #=dON T EXPORTIMAGES
        if (export_image == False and 'cloud' not in types):
          tasks.append (self.call_task(types, image_name, single_img ))

        # visualized_im = ''
        if (export_image!=False):
          visualized_im  = self.call_viz_image(types, single_img )

          list_images.append (visualized_im  )
          list_image_names.append(str(date))


      if "cloud" in types:
            try:
              collection_s2cloudless = self.gets2cloudless()
              image_lists2cloudless = collection_s2cloudless.toList(collection_s2cloudless.size())
            except:
              print('no S2cloudless images')

            image_s2cloudless_list = collection_s2cloudless.toList(
                          collection_s2cloudless.size()
                      )

            
            date1 =  self.api.Image( image_s2cloudless_list.get(0)).date().format("YYYY-MM-dd").getInfo()
            datei = self.from_date_to_doy(date1)
            list_interval=[ self.from_date_to_doy(date1) ]
            cpt=1
            while datei < self.from_date_to_doy(self.end_date) + interval :
                datei = datei + interval
                list_interval.append( datei )
                
            
            # print('No image available')
              
            img_size_s2cl = image_s2cloudless_list.size().getInfo()

            date_range_list = list(self.date_range(self.start_date, self.end_date, list_interval))[:-1]

            for i in range (len(date_range_list) - 1 ):
              start_date = date_range_list [i]
              end_date =  date_range_list [i+1]

              if self.function == 'mosaic':
                single_img = self.setImage(start_date, end_date).mosaic()
              elif self.function == 'median':
                single_img = self.setImage( start_date, end_date).median()


                date_cloudy = start_date + '_' +end_date 

      
                # if "cloud" in types:
                tasks.append(
                        self.getS2cloudless_task(
                            "cloud_" + str(date_cloudy), single_img
                        )
                    )
      



      # return tasks
      if (export_image == False):
        return tasks
      if (export_image!=False):
        # centerpoint  = [-16,16.3, 9.5]
        # list_images = [image, image]
        res = self.export_geemap_to_html(list_images, list_image_names, self.folder, centerpoint = export_image)
        return res
    #=================================================================================

    else:  # GET IMAGES WITH MASK  PIXELS

      collection  = self.collectByDate(self.getMask_images())
      # get s2cloudless images
      collection_s2cloudless =self.collectByDate(self.gets2cloudless())
      image_list = collection.toList(collection.size())
      img_size =  image_list .size().getInfo()
      print('size collection',image_list.size().getInfo())
    
  
      #try:
      date1 =  self.api.Image(image_list.get(0)).date().format("YYYY-MM-dd").getInfo()
      datei = self.from_date_to_doy(date1)
      list_interval=[ self.from_date_to_doy(date1) ]
      cpt=1
      while datei < self.from_date_to_doy(self.end_date) + 1 :
          datei = datei + interval
          list_interval.append( datei )
          
      #except:
        #print('No image available')
        
      tasks =[]
      list_images= [] 
      list_image_names = []

      # date_range_list = list(self.date_range(self.start_date, self.end_date, list_interval))[:-1]

      date_range_list = list(self.date_range ( str(date1) , self.end_date, interval) )


      for i in range (len(date_range_list) - 1 ):
        start_date = date_range_list [i]
        end_date =  date_range_list [i+1]

        if self.function == 'mosaic':
          single_img = self.setMask_images(start_date, end_date).mosaic()
        elif self.function == 'median':
          single_img = self.setMask_images(start_date, end_date).median()


        date = start_date + '_' +end_date   #self.api.Image(image_list.get(i)).date().format("YYYY-MM-dd").getInfo()
        image_name =date

        if image_intersect!=False:
          single_img = self.img_intersection(image_intersect, single_img)

        if mask_water != False :
          single_img  = self.mask_permanent_water( single_img , date_range_ =[mask_water[0] ,mask_water[1]] )

        if (export_image == False):
          tasks.append (self.call_task(types, image_name, single_img ))

        # visualized_im = ''
        if (export_image!=False): 

          visualized_im  = self.call_viz_image(types, single_img )

          list_images.append (visualized_im  )
          list_image_names.append(str(date))
        # tasks.append (self.call_task(types, image_name, single_img ))


      # return tasks
      if (export_image == False):
        return tasks

      if (export_image!=False):
        # centerpoint  = [-16,16.3, 9.5]
        # list_images = [image, image]
        res = self.export_geemap_to_html(list_images, list_image_names, self.folder, centerpoint = export_image)
        return res    

