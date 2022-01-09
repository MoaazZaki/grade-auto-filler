import pipeLine
import cv2
import matplotlib.pyplot as plt
from modules.Scanner import Scanner
import numpy as np
from utils.helpers import (generate_bubble_sheet,to_pdf)
#img = cv2.imread('datasets/MCQ/3.jpg')
pipeLine.grade_sheet_pipeline('../../gradesheet-20220106T190105Z-001/gradesheet/6.JPG','../output/2.xlsx')
# sc = Scanner(img)
# scanned = sc.trnasform()
# plt.figure()
# plt.imshow(img)
# plt.show()
#model_answer =['A','E','B','C','D','B','D','B','C','D','B','C','B','D','B','A',['B','D'],'E','B','A']
#model_answer = ['A'] * 45
#answer_grades = np.ones_like(model_answer)
#answer_grades[0] = 20
#pipeLine.bubble_sheet_pipeline('../../ID7Q45CH4-20220106T190108Z-001/ID7Q45CH4',model_answer,answer_grades,'../output/bb1.xlsx',7,4)


#to_pdf(generate_bubble_sheet('../datasets/MCQ/MCQ_paper.png',5,40),'../output/1.pdf')