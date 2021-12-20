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

import matplotlib.pyplot as plt

def pipeLine(img_path,output_csv_path):
    cols_to_drop=[1,2]
    img = cv2.imread(img_path)
    #remove the shadow
    img=hlp.removeShadow(img)
    #scan the image
    sc = Scanner(img)
    scanned = sc.trnasform(visualize=False)
    #detect the cells
    cellDetector=CellDetector(scanned,visualize=False)
    cells,cells_image=cellDetector.get_table_cells()
    hlp.output_csv(scanned.copy(),cells_image,cells,output_csv_path,cols_to_drop=cols_to_drop,symbol_cols=[4,5])


pipeLine('datasets/grade_papers/6.jpg','output/2.xlsx')


img = cv2.imread('datasets/grade_papers/6.jpg')
plt.figure()
plt.imshow(img)
plt.show()