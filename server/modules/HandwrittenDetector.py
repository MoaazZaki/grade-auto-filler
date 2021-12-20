import numpy as np 
from skimage.feature import hog
import cv2

import imutils
import matplotlib.pyplot as plt


def get_bw_transition_areas(img):
        binary_img = cv2.threshold(img , 20, 255,cv2.THRESH_BINARY_INV)[1].reshape(28,28)
        digit_indecies = np.where(binary_img == 0)
        digit_indecies = np.array([*zip(digit_indecies[0],digit_indecies[1])])
        h_area = np.sum(binary_img[digit_indecies[:,0],digit_indecies[:,1] - 1] == 255)
        v_area = np.sum(binary_img[digit_indecies[:,0] -1,digit_indecies[:,1]] == 255)

        img_area = binary_img.shape[0] * binary_img.shape[1]
        return h_area /  img_area , v_area / img_area

class classifier:

    def __init__(self,K=13,ocrs=[],PEXILS_PER_CELL=(12,12)):

        X_train = np.load('../models/knn/X_train.npy',allow_pickle=True)
        y_train = np.load('../models/knn/y_train.npy',allow_pickle=True)
        self.KNN = cv2.ml.KNearest_create()
        self.KNN.train(X_train.astype(np.float32), cv2.ml.ROW_SAMPLE, y_train)
        self.K = K


        self.preprocess_reshaped = lambda imgs: np.array([ np.hstack([hog(img, orientations=9, pixels_per_cell=PEXILS_PER_CELL,cells_per_block=(2, 2), visualize=False, multichannel=False),get_bw_transition_areas(img)]) for img in imgs])

    

    def predict(self,X,method='knn',ocr_i=None):
        if method.upper() == 'KNN':
            processed = np.array([ (cv2.resize(img, (28, 28))).astype(np.float32).reshape(28,28) for img in X])
            processed = self.preprocess_reshaped(processed)
            
            _,y_pred,_,_ = self.KNN.findNearest(processed.astype(np.float32),k=self.K) 
            return y_pred.reshape(-1)

        elif method.upper() == 'OCR':
            pass


# img = cv2.imread('datasets/digits/2.jpg')
# gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# blur = cv2.GaussianBlur(gray,(5,5),0)
# _,thresh =  cv2.threshold(blur, 150, 255,cv2.THRESH_BINARY_INV)

# # find contours in the thresholded image, then initialize the
# # digit contours lists
# cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
# cnts = imutils.grab_contours(cnts)
# digit_bb = []
# # loop over the digit area candidates
# for c in cnts:
# 	# compute the bounding box of the contour
# 	(x, y, w, h) = cv2.boundingRect(c)
# 	# if the contour is sufficiently large, it must be a digit
# 	if w >= 50 and (h >= 100 and h <= 800):
# 		digit_bb.append([x, y, w, h])

# digits = []
# for bb in digit_bb:
#     x,y,w,h = bb
#     digits.append(gray[y:y+h,x:x+w])