import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
import sys
sys.path.append('../modules')
from modules import HandwrittenDetector
from modules import SymbolDetector
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
hw_model = HandwrittenDetector.classifier()
#pytesseract.pytesseract.tesseract_cmd = "C:\Program Files (x86)\Tesseract-OCR\\tesseract.exe" 

def show_images(images,titles=None):
    #This function is used to show image(s) with titles by sending an array of images and an array of associated titles.
    # images[0] will be drawn with the title titles[0] if exists
    # You aren't required to understand this function, use it as-is.
    n_ims = len(images)
    if titles is None: titles = ['(%d)' % i for i in range(1,n_ims + 1)]
    fig = plt.figure()
    n = 1
    for image,title in zip(images,titles):
        a = fig.add_subplot(1,n_ims,n)
        if image.ndim == 2: 
            plt.gray()
        plt.imshow(image)
        a.set_title(title)
        n += 1
    fig.set_size_inches(np.array(fig.get_size_inches()) * n_ims)
    

# def change_cell_background(x,value='?',color='red'):
#     color = 'background-color: {}'.format(color)
#     df1 = pd.DataFrame('', index=x.index, columns=x.columns)
#     df1[x==value] = color
#     return df1

# cells_image= image returned from the CellDetector, finalboxes= cells,output_path=path of the csv file
def output_csv(original,cells_image,finalboxes,output_path,id_col=0,number_cols=[3],symbol_cols=[4],cols_to_drop=[]): 

    enhance = lambda img: cv2.erode(cv2.dilate(cv2.resize(cv2.copyMakeBorder(img,2,2,2,2, cv2.BORDER_CONSTANT,value=[255,255]), None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC), cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1)),iterations=1), cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1)),iterations=2)
    table = np.empty_like(finalboxes[:,:,0],dtype=object)

    # ID COL
    options = "outputbase digits"

    table[1:,id_col] = out = "1170353"#[pytesseract.image_to_string(erosion,config=options)] 

    # HAND-WRITTEN NUMBERS COL
    for col in number_cols:
        bbs = finalboxes[1:,col]
        table[1:,col] = hw_model.predict([cells_image[bb[1]:bb[1]+bb[3],bb[0]:bb[0]+bb[2]] for bb in bbs])

    # SYMBOL COLS
    class_to_symbol = lambda symbol,count: '5' if symbol == 'tick' else '?' if symbol == 'question_mark' else str(count) if symbol == 'v_line' else str(5-count) if symbol == 'h_line' else '0' if symbol == 'rect' else ' '

    for col in symbol_cols:
        bbs = finalboxes[1:,col]
        table[1:,col] = [class_to_symbol(*SymbolDetector.classify_symbol(original[bb[1]:bb[1]+bb[3],bb[0]:bb[0]+bb[2]])) for bb in bbs]

    #Creating a dataframe of the generated OCR list
    dataframe = pd.DataFrame(table[1:,:], columns=['id' if i == 0 else i for i in range(table.shape[1])])
    dataframe.reset_index(drop=True,inplace=True)
    dataframe.style.applymap(lambda val: 'background-color: {}; color:{}'.format('transparent' if val != '?' else 'red','black' if val != '?' else 'red')).\
            to_excel(output_path, engine='openpyxl')
  
def removeShadow(img):
    rgb_planes = cv2.split(img)
    result_planes = []
    result_norm_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        result_planes.append(diff_img)
        result_norm_planes.append(norm_img)

    result = cv2.merge(result_planes)
    result_norm = cv2.merge(result_norm_planes)
    return result