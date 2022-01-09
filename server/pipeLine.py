from flask import Flask, json, request, jsonify
from modules import CellDetector
from modules.CellDetector import CellDetector
from modules.Scanner import Scanner
from utils import helpers as hlp
import os
import urllib.request
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import cv2
from datetime import datetime
from modules.Grader import Grader
from modules.BubbleParser import BubbleParser

import matplotlib.pyplot as plt

def grade_sheet_pipeline(img_path,output_csv_path,numbers_col=[3],cols_to_drop=[1,2],symbol_cols=[4,5]):
    img = cv2.imread(img_path)
    #remove the shadow
    img=hlp.removeShadow(img)
    #scan the image
    sc = Scanner(img)
    scanned = sc.trnasform(visualize=False)
    #print(scanned.shape)
    fixed_h = 500
    height_percent = float(fixed_h) / scanned.shape[0] # W/H
    scanned = cv2.resize(scanned,(int(scanned.shape[1]*height_percent),fixed_h),interpolation= cv2.INTER_CUBIC)
    #detect the cells
    cellDetector=CellDetector(scanned,visualize=False)
    cells,cells_image=cellDetector.get_table_cells()
    hlp.output_csv(scanned.copy(),cells_image,cells,output_csv_path,number_cols=numbers_col,cols_to_drop=cols_to_drop,symbol_cols=symbol_cols)


def bubble_sheet_pipeline(folder_path,model_answer,answer_grades,ouput_exccel_path,ID_DIGITS_NUM,CHOICES_NUM ,IS_MULTI_ANSWER = True,WRONG_ANSWER_GRADE = 2,ALLOW_NEGATIVE_GRADES=False):
        
    CANNY_L_THRESH=75
    CANNY_H_THRESH=170
    DILATION_SIZE=(5,5)
    DILATION_ITERS=5
    EROSION_SIZE=(5,5)
    EROSION_ITERS=1

    bp = BubbleParser(ID_DIGITS_NUM,CHOICES_NUM,visualize=False)
    gr = Grader(CHOICES_NUM,WRONG_ANSWER_GRADE,IS_MULTI_ANSWER,model_answer,answer_grades,ALLOW_NEGATIVE_GRADES)


    for img_path in os.listdir(folder_path):
        img_path = '{}/{}'.format(folder_path,img_path)
        img = cv2.imread(img_path)
        sc = Scanner(img)

        scanned = sc.trnasform(visualize=False)
        fixed_h = 1500
        height_percent = float(fixed_h) / scanned.shape[0] # W/H
        scanned = cv2.resize(scanned,(int(scanned.shape[1]*height_percent),fixed_h),interpolation= cv2.INTER_CUBIC)
        gray = cv2.cvtColor(scanned, cv2.COLOR_BGR2GRAY)
        edged = cv2.Canny(gray, CANNY_L_THRESH, CANNY_H_THRESH)
        edged = cv2.dilate(edged,DILATION_SIZE,iterations=DILATION_ITERS)
        edged = cv2.erode(edged,EROSION_SIZE,iterations=EROSION_ITERS)

        (ID,answer) = bp.extract(scanned,edged)
        gr.add_grade(ID,answer)

        
    
    gr.save(ouput_exccel_path)
