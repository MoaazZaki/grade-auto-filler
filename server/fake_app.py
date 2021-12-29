import pipeLine
import cv2
import matplotlib.pyplot as plt
from modules.Scanner import Scanner
import numpy as np
# img = cv2.imread('datasets/MCQ/3.jpg')
# #pipeLine.grade_sheet_pipeline('datasets/grade_papers/6.jpg','output/2.xlsx')
# sc = Scanner(img)
# scanned = sc.trnasform()
# plt.figure()
# plt.imshow(img)
# plt.show()
model_answer =['A','E','B','C','D','B','D','B','C','D','B','C','B','D','B','A',['B','D'],'E','B','A']
model_answer += ['A'] * (45-len(model_answer))
answer_grades = np.ones_like(model_answer)
answer_grades[0] = 20
pipeLine.bubble_sheet_pipeline('static/uploads/answers',model_answer,answer_grades,'../output/bb1.xlsx')