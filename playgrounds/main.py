import cv2
from scanner import Scanner
import matplotlib.pyplot as plt
import cellDetector


if __name__ == '__main__':
    img = cv2.imread('datasets/grade_papers/3.jpg')
    sc = Scanner(img)
    scanned = sc.trnasform(visualize=False)

    #thresholding the image to a binary image
    img_bin = (scanned >= 115).astype(float)
    plt.figure(4)
    plt.imshow(img_bin)

    cellDetector.convertImageToCsv(scanned)
    plt.show()
