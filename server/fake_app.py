from pipeLine import pipeLine
import cv2
import matplotlib.pyplot as plt

img = cv2.imread('datasets/grade_papers/6.jpg')
pipeLine('datasets/grade_papers/6.jpg','output/2.xlsx')

plt.figure()
plt.imshow(img)
plt.show()