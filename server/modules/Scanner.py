import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage.filters import threshold_local
import imutils

class Scanner:
    """
    Class used to take captured image and transform it to scanned

    ...

    Attributes
    ----------
    img : np.ndarray
        image to be scanned
    original : np.ndarray
        original copy of the image kept for visualizing
    GAUSSIAN_SIZE : tuple
        Window size of gaussian filter
    CANNY_L_THRESH : int
        Low threshold of canny edge detector
    CANNY_H_THRESH : int
        High threshold of canny edge detector
    DILATION_SIZE : tuple
        Element size of dilation
    DILATION_ITERS : int
        Number of dilations
    EROSION_SIZE : tuple
        Element size of erosion
    EROSION_ITERS : int
        Number of erosions
    
    Methods
    -------
    get_edges()
        return an image wiht edges of original

    get_corners(edged)
        return return the corners of the scanned paper

    order_pts(pts)
        return an ordered version of the corners (top-left,top-right,bottom-right,bottom-left)

    get_dst_pts(rect)
        return the new dimension points for the scanned image
    
    trnasform(visualize=True)
        return the transfomed scanned paper
    """

    def __init__(self,img,GAUSSIAN_SIZE=(9,9),CANNY_L_THRESH=75,CANNY_H_THRESH=170,DILATION_SIZE=(5,5),DILATION_ITERS=5,EROSION_SIZE=(5,5),EROSION_ITERS=1):
        self.img = img.copy()
        self.original = img.copy()
        self.GAUSSIAN_SIZE = GAUSSIAN_SIZE
        self.CANNY_L_THRESH = EROSION_ITERS
        self.CANNY_H_THRESH = CANNY_H_THRESH
        self.DILATION_SIZE = DILATION_SIZE
        self.DILATION_ITERS = DILATION_ITERS
        self.EROSION_SIZE = EROSION_SIZE
        self.EROSION_ITERS = EROSION_ITERS

    def get_edges(self):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, self.GAUSSIAN_SIZE, 0)
        edged = cv2.Canny(gray, self.CANNY_L_THRESH, self.CANNY_H_THRESH)
        edged = cv2.dilate(edged,self.DILATION_SIZE,iterations=self.DILATION_ITERS)
        edged = cv2.erode(edged,self.EROSION_SIZE,iterations=self.EROSION_ITERS)

        return edged

    def get_corners(self,edged):
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

        for c in cnts:

            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            if len(approx) >= 4:
                corners = approx
                break
        
        return corners

    def order_pts(self,pts):
        rect_pts = np.zeros((4, 2), dtype = "float32")
        s = pts.sum(axis = 1)
        rect_pts[0] = pts[np.argmin(s)]
        rect_pts[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis = 1)
        rect_pts[1] = pts[np.argmin(diff)]
        rect_pts[3] = pts[np.argmax(diff)]
        
        return rect_pts

    def get_dst_pts(self,rect):
        (tl, tr, br, bl) = rect

        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype = "float32")

        return dst
    
    def trnasform(self,return_edged=False,visualize=True):
        
        edged = self.get_edges()
        corners = self.get_corners(edged)
        ordered_corners = self.order_pts(corners.reshape(-1,2))
        transformed_corners = self.get_dst_pts(ordered_corners)
        H = cv2.getPerspectiveTransform(ordered_corners, transformed_corners)
        transformed = cv2.warpPerspective(self.original, H, (int(transformed_corners[2][0]+1), int(transformed_corners[2][1]+1)))

        if visualize:
            plt.figure()
            plt.imshow(self.original)
            plt.figure()
            plt.imshow(edged)
            cv2.drawContours(self.img, [corners], -1, (0, 255, 0), 15)
            plt.figure()
            plt.imshow(self.img)
            plt.figure()
            plt.imshow(transformed)
        return transformed if not return_edged else (transformed,edged)
