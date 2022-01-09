import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
try:
    from PIL import Image
except ImportError:
    import Image


class CellDetector:
    """
    Class used to take the scanned image and detect the cells of a table

    ...

    Attributes
    ----------
    img : np.ndarray
        scanned image (expected an rgb image)
    
    Methods
    -------
    get_table_cells()
        returns an array of rows where each row has cols and each col consists of [x,y,w,h] 
        where [x,y,w,h] are the bounding boxes of the cells

        len(returnedArray) => number of rows
        len(returnedArray[0]) => number of cols 

    """

    def __init__(self,img,visualize=False):
      self.visualize=visualize
      gray_img=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      self.img=gray_img
      thresh,img_bin = cv2.threshold(gray_img,115,255,cv2.THRESH_BINARY |cv2.THRESH_OTSU)
      #inverting the image 
      img_bin = 255-img_bin
      self.img_bin = img_bin
      # Length(width) of kernel as 100th of total width
      kernel_len = np.array(img).shape[1]//100
      # Defining a vertical kernel to detect all vertical lines of image 
      self.ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len))
      # Defining a horizontal kernel to detect all horizontal lines of image
      self.hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
      # A kernel of 2x2
      self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

      if self.visualize:
        #Plotting the generated image
        plotting = plt.imshow(255-self.img_bin,cmap='gray')
       

    def _get_outlier_bounds(self,values):
      Q1 = np.percentile(values, 25,
                   interpolation = 'midpoint')
 
      Q3 = np.percentile(values, 75,
                   interpolation = 'midpoint')
      IQR = Q3 - Q1

      return (Q3+1.5*IQR) , (Q3-1.5*IQR) # upper,lower

    def _sort_contours(self,cnts):
      boundingBoxes = [cv2.boundingRect(c) for c in cnts]
      (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
      key=lambda b:b[1][1]))

      # return the list of sorted contours and bounding boxes
      return (np.array(cnts,dtype=object), np.array(boundingBoxes))

    def _correct_rows(self,rows,bounds,bounds_critertion=2,RELAXATION_CONSTANT=10):
      correct_rows = [] # To store corrected rows
      for row in rows:
        indecies = [] # To keep track of correct cells in row
        for bound in bounds:
          i = 0
          lower,upper = bound[0],bound[1]
          
          while True:
            # Check if the current cell meets bounds
            if row[i][bounds_critertion] <= upper and row[i][bounds_critertion] >= lower and i not in indecies:
              indecies.append(i)
              break
            
            i+=1

            # If current bound doesn't meet any cell relax the bounds a little
            if i == len(row):
              i = 0
              lower -= RELAXATION_CONSTANT
              upper += RELAXATION_CONSTANT
        correct_rows.append(list(np.array(row)[indecies]))
      return correct_rows



    def get_table_cells(self):
      #Use vertical kernel to detect and save the vertical lines in a jpg
      image_1 = cv2.erode(self.img_bin, self.ver_kernel, iterations=3)
      vertical_lines = cv2.dilate(image_1, self.ver_kernel, iterations=3)

      if self.visualize:
        #Plotting the generated image
        plt.figure()
        plotting = plt.imshow(vertical_lines,cmap='gray')
       

      #Use horizontal kernel to detect and save the horizontal lines in a jpg
      image_2 = cv2.erode(self.img_bin, self.hor_kernel, iterations=3)
      horizontal_lines = cv2.dilate(image_2, self.hor_kernel, iterations=3)

      if self.visualize:
        #Plotting the generated image
        plt.figure()
        plotting = plt.imshow(horizontal_lines,cmap='gray')
       

      # Combine horizontal and vertical lines in a new third image, with both having same weight.
      img_vh = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)

      #Eroding and thesholding the image
      img_vh = cv2.erode(~img_vh, self.kernel, iterations=2)
      thresh, img_vh = cv2.threshold(img_vh,128,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
      
      bitxor = cv2.bitwise_xor( cv2.bitwise_xor(self.img_bin,horizontal_lines),vertical_lines)
      bitnot = cv2.bitwise_not(bitxor)

      if self.visualize:
        #Plotting the generated image
        plt.figure()
        plotting = plt.imshow(img_vh,cmap='gray')
       
      # Detect contours for following box detection
      contours, hierarchy = cv2.findContours(img_vh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
      # Sort all the contours by top to bottom.
      contours, boundingBoxes = self._sort_contours(contours)

      # Filtering the noise lines
      upper_h,lower_h = 500,20
      upper_w = 1000
      mask = ((boundingBoxes[:,-1]<=upper_h) & (boundingBoxes[:,-1]>=lower_h)) & ( boundingBoxes[:,-2]< upper_w)
      boundingBoxes = boundingBoxes[mask]
      contours = contours[mask]
      
      mean = np.mean(boundingBoxes[:,-1])
      #Creating two lists to define row and column in which cell is located
      row=[]
      column=[]
      columns_per_row = []
      for i in range(len(boundingBoxes)):    
              
          if(i==0):
              column.append(boundingBoxes[i])
              previous=boundingBoxes[i]    
          
          else:
              if(boundingBoxes[i][1]<=previous[1]+mean/2):
                  column.append(boundingBoxes[i])
                  previous=boundingBoxes[i]            
                  
                  if(i==len(boundingBoxes)-1):
                      row.append(column)        
                      columns_per_row.append(len(column))
              else:
                  row.append(column)
                  columns_per_row.append(len(column))
                  column=[]
                  previous = boundingBoxes[i]
                  column.append(boundingBoxes[i])

      # Sorting columns from left to right
      row = [sorted(r,key=lambda bb: bb[0]) for r in row]
      
      # Gettign the mode of number of columns for each row
      from scipy.stats import mode
      
      columns_per_row = np.array(columns_per_row)
      row = np.array(row,dtype=object)
      columns_number = mode(columns_per_row)[0][0]

      # Filtering The correct rows
      wrong_rows_mask = columns_per_row != columns_number
      correct_rows = np.array(list(row[~wrong_rows_mask]))


      if np.sum(wrong_rows_mask) != 0:
        # Getting width bounds for each column
        columns_bounds = np.array([ self._get_outlier_bounds(correct_rows[:,j,-2]) for j in range(correct_rows.shape[1])])

        # Correct and append wrong rows
        correct_rows = np.vstack([correct_rows,np.array(self._correct_rows(list(row[wrong_rows_mask]),columns_bounds))])


      return np.hstack([sorted(correct_rows[:,col],key=lambda bb: bb[1]) for col in range(correct_rows.shape[1])]).reshape(correct_rows.shape[0],correct_rows.shape[1],4), bitnot # return the cells and an enhanced image