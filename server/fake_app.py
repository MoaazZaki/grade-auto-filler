from pipeLine import pipeLine

pipeLine('datasets/grade_papers/6.jpg','output/2.xlsx')


img = cv2.imread('datasets/grade_papers/6.jpg')
plt.figure()
plt.imshow(img)
plt.show()