import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:\Program Files (x86)\Tesseract-OCR\\tesseract.exe" 

def show_images(images,figure,titles=None):
    #This function is used to show image(s) with titles by sending an array of images and an array of associated titles.
    # images[0] will be drawn with the title titles[0] if exists
    # You aren't required to understand this function, use it as-is.
    n_ims = len(images)
    if titles is None: titles = ['(%d)' % i for i in range(1,n_ims + 1)]
    fig = plt.figure(figure)
    n = 1
    for image,title in zip(images,titles):
        a = fig.add_subplot(1,n_ims,n)
        if image.ndim == 2: 
            plt.gray()
        plt.imshow(image)
        a.set_title(title)
        n += 1
    fig.set_size_inches(np.array(fig.get_size_inches()) * n_ims)
    

# cells_image= image returned from the CellDetector, finalboxes= cells,output_path=path of the csv file
def output_csv(cells_image,finalboxes,output_path): 
  #from every single image-based cell/box the strings are extracted via pytesseract and stored in a list
  outer=[]
  for i in range(len(finalboxes)):
      for j in range(len(finalboxes[i])):
          inner=''
          if(len(finalboxes[i][j])==0):
              outer.append(' ')
          else:
              for k in range(len(finalboxes[i][j])):
                  x,y,w,h = finalboxes[i][j][k][0],finalboxes[i][j][k][1], finalboxes[i][j][k][2],finalboxes[i][j][k][3]
                  finalimg = cells_image[ y:y+h,x:x +w]
                  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
                  border = cv2.copyMakeBorder(finalimg,2,2,2,2, cv2.BORDER_CONSTANT,value=[255,255])
                  resizing = cv2.resize(border, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                  dilation = cv2.dilate(resizing, kernel,iterations=1)
                  erosion = cv2.erode(dilation, kernel,iterations=2)
                  
                  out = pytesseract.image_to_string(erosion) if  not(j==1) else ""
                  out=out.replace("\n","").replace("|","").replace("_","").replace("[","").strip()
                  if(len(out)==0):
                      out = pytesseract.image_to_string(erosion, config='--psm 3') if  not(j==1) else ""
                      out=out.replace("\n","").replace("|","").replace("_","").replace("[","").strip()

                  inner = inner +" "+ out
              outer.append(inner)

  #Creating a dataframe of the generated OCR list
  arr = np.array(outer)
  dataframe = pd.DataFrame(arr.reshape(len(finalboxes), len(finalboxes[0])))
  dataframe.reset_index(drop=True, inplace=True)
  data = dataframe.style.set_properties(align="left")
  data.to_excel(output_path, index=False)

def removeShadow(img):
    rgb_planes = cv2.split(img)
    result_planes = []
    result_norm_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        result_planes.append(diff_img)
        result_norm_planes.append(norm_img)

    result = cv2.merge(result_planes)
    result_norm = cv2.merge(result_norm_planes)
    return result