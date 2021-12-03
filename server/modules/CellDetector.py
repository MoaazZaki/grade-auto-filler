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

    def _sort_contours(self,cnts, method="left-to-right"):
      # initialize the reverse flag and sort index
      reverse = False
      i = 0
      # handle if we need to sort in reverse
      if method == "right-to-left" or method == "bottom-to-top":
          reverse = True
      # handle if we are sorting against the y-coordinate rather than
      # the x-coordinate of the bounding box
      if method == "top-to-bottom" or method == "bottom-to-top":
          i = 1
      # construct the list of bounding boxes and sort them from top to
      # bottom
      boundingBoxes = [cv2.boundingRect(c) for c in cnts]
      (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
      key=lambda b:b[1][i], reverse=reverse))
      # return the list of sorted contours and bounding boxes
      return (cnts, boundingBoxes)


    def get_table_cells(self):
      #Use vertical kernel to detect and save the vertical lines in a jpg
      image_1 = cv2.erode(self.img_bin, self.ver_kernel, iterations=3)
      vertical_lines = cv2.dilate(image_1, self.ver_kernel, iterations=3)

      #Use horizontal kernel to detect and save the horizontal lines in a jpg
      image_2 = cv2.erode(self.img_bin, self.hor_kernel, iterations=3)
      horizontal_lines = cv2.dilate(image_2, self.hor_kernel, iterations=3)

      # Combine horizontal and vertical lines in a new third image, with both having same weight.
      img_vh = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)

      #Eroding and thesholding the image
      img_vh = cv2.erode(~img_vh, self.kernel, iterations=2)
      thresh, img_vh = cv2.threshold(img_vh,128,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
      
      bitxor = cv2.bitwise_xor(self.img,img_vh)
      bitnot = cv2.bitwise_not(bitxor)

      if self.visualize:
        #Plotting the generated image
        plotting = plt.imshow(img_vh,cmap='gray')
        plt.show()

      # Detect contours for following box detection
      contours, hierarchy = cv2.findContours(img_vh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
      # Sort all the contours by top to bottom.
      contours, boundingBoxes = self._sort_contours(contours, method="top-to-bottom")
      
      #Creating a list of heights for all detected boxes
      heights = [boundingBoxes[i][3] for i in range(len(boundingBoxes))]
      #Get mean of heights
      mean = np.mean(heights)
      #Create list box to store all boxes in  
      box = []
      # Get position (x,y), width and height for every contour and show the contour on image
      for c in contours:
          x, y, w, h = cv2.boundingRect(c)
          if (w<1000 and (h<500 and h>10)):
              image = cv2.rectangle(self.img,(x,y),(x+w,y+h),(0,255,0),2)
              box.append([x,y,w,h])

      #Creating two lists to define row and column in which cell is located
      row=[]
      column=[]
      j=0

      #Sorting the boxes to their respective row and column
      for i in range(len(box)):    
              
          if(i==0):
              column.append(box[i])
              previous=box[i]    
          
          else:
              if(box[i][1]<=previous[1]+mean/2):
                  column.append(box[i])
                  previous=box[i]            
                  
                  if(i==len(box)-1):
                      row.append(column)        
                  
              else:
                  row.append(column)
                  column=[]
                  previous = box[i]
                  column.append(box[i])
                  

      #calculating maximum number of cells
      countcol = 0
      for i in range(len(row)):
          countcol = len(row[i])
          if countcol > countcol:
              countcol = countcol

      #Retrieving the center of each column
      center = [int(row[i][j][0]+row[i][j][2]/2) for j in range(len(row[i])) if row[0]]

      center=np.array(center)
      center.sort()
      #Regarding the distance to the columns center, the boxes are arranged in respective order

      finalboxes = []
      for i in range(len(row)):
          lis=[]
          for k in range(countcol):
              lis.append([])
          for j in range(len(row[i])):
              diff = abs(center-(row[i][j][0]+row[i][j][2]/4))
              minimum = min(diff)
              indexing = list(diff).index(minimum)
              lis[indexing].append(row[i][j])
          finalboxes.append(lis)
      return finalboxes, bitnot # return the cells and an enhanced image