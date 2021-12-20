import numpy as np 
import cv2
import imutils
from skimage.transform import (hough_line, hough_line_peaks)
from skimage.feature import canny
from skimage.transform import hough_ellipse


import matplotlib.pyplot as plt

  
  
  
  
def classify_symbol(symbol,  LINE_DISTANCE_THRESHOLD = 15,  LINE_ANGLE_THRESHOLD = 30,LINE_ANGLE_ALLOWANCE = 35,RECTANLE_BB_RATIO_ALLOWANCE = 0.4,TICK_MAX_AREA = 0.5,TICK_MIN_DISTANCE = 10,TICK_ANGLE_ALLOWANCE = 25):
  detect_value = lambda inp,value,allowance: inp >= value-allowance and inp <= value+allowance 

 # print(symbol.shape)
  gray = cv2.cvtColor(symbol,cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(gray,(5,5),0)
  _,thresh =  cv2.threshold(blur, 150, 255,cv2.THRESH_BINARY_INV)
  #thresh =  (symbol/255).astype(np.uint8)

  # find contours in the thresholded image, then initialize the
  # symbol contours lists
  cnts = cv2.findContours(thresh.copy()[5:-4,5:-4], cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)
  if len(cnts) == 0:
    return 'empty',0 

  cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  #print(cnts)
  cnts = imutils.grab_contours(cnts)
  
  vertical_angles = 0
  horizontal_angles = 0
  tick_angles = 0
  tick_distances = 0
  tick_area = 0
  rectangles = 0
  #horizontal_bb = 0
  vertical_bb = 0
  elipses = 0
  

  roi_cnts = 0
  
  # loop over the symbol area candidates
  for c in cnts:
    # compute the bounding box of the contour
    (x, y, w, h) = cv2.boundingRect(c)
    # if the contour is sufficiently large, it must be a symbol
    if w >= 2 and (h >= 2 and h <= 800) and w*h >= 50:
      roi_cnts += 1
      symbol_part = thresh[y:y+h,x:x+w].copy() 
      edged_symbol_part = canny(symbol_part.copy())
      houghSpace,angles, dists = hough_line(edged_symbol_part)
      houghSpace,angles, dists = hough_line_peaks(houghSpace,angles, dists, threshold=0.45*np.max(houghSpace))

      line_angles = angles
      line_dists = dists
      if len(dists) > 1:
        if np.max(dists) - np.min(dists) <= LINE_DISTANCE_THRESHOLD and np.max(angles) - np.min(angles) <= LINE_ANGLE_THRESHOLD:
          line_dists = [dists[0]]
          line_angles = [angles[0]]

      vertical_angles += np.sum([detect_value(180*angle/np.pi,0,LINE_ANGLE_ALLOWANCE) for angle in line_angles])
      horizontal_angles += np.sum([detect_value(180*angle/np.pi,90,LINE_ANGLE_ALLOWANCE) for angle in line_angles])
      rectangles += 1 if detect_value(w/h,1,RECTANLE_BB_RATIO_ALLOWANCE) else 0
      vertical_bb += 1 if (w/h) < 1-RECTANLE_BB_RATIO_ALLOWANCE else 0
      
      if len(dists) > 1 :
        tick_index = np.argmax(dists)
        tick_angles += 1 if detect_value(180*angles[tick_index]/np.pi,45,TICK_ANGLE_ALLOWANCE) else 0
        tick_distances += 1 if dists[tick_index] >= TICK_MIN_DISTANCE else 0

      elipses += len(hough_ellipse(edged_symbol_part, accuracy=20, threshold=100,min_size=0, max_size=20))

      #print(edged_symbol_part.shape)
      
      # tick_area += np.sum(symbol_part>0) / (symbol_part.shape[0]*symbol_part.shape[1])
      # print(tick_area)
      #horizontal_bb += 1 if (w/h) > 1+RECTANLE_BB_RATIO_ALLOWANCE else 0
      



  if  roi_cnts == 1  and tick_angles == 1 and tick_distances == 1 and rectangles == 1:
    return 'tick',1
  elif roi_cnts == 1 and len(cnts) >= 1 and vertical_bb >= 1 and elipses > 0:
    return 'question_mark',1
  elif vertical_angles != 0 and vertical_angles == roi_cnts and rectangles == 0:
    return 'v_line',roi_cnts
  elif horizontal_angles != 0 and horizontal_angles == roi_cnts and rectangles == 0:
    return 'h_line',roi_cnts
  elif vertical_angles >= 2 and horizontal_angles >= 2 and (roi_cnts >= 1 or (roi_cnts == 1 and rectangles == 1)):
    return 'rect',1

  return 'empty',0




# img = cv2.imread('datasets/symbols/1.jpeg')[100:190,260:320]
# plt.figure()
# plt.imshow(img)
# print(classify_symbol(img))
# plt.show()