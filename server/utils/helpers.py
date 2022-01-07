import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
import sys
sys.path.append('../modules')
from modules import HandwrittenDetector
from modules import SymbolDetector
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

    table[1:,id_col] = out = pytesseract.image_to_string(enhance(original),config=options)

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
    dataframe = dataframe.applymap(lambda x: x.encode('unicode_escape').
                 decode('utf-8') if isinstance(x, str) else x)
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


# bb y1 y2 x1 x2
def generate_bubble_sheet(path_to_template,ID_DIGITS_NUM,QUESTIONS_NUMBER,CHOICES_NUM):

    img = cv2.imread(path_to_template)

    id_bbs = [[295,400,220,1300],
            [400,500,220,1300],
            [500,600,220,1300],
            [600,700,220,1300],
            [700,800,220,1300],
            [800,900,220,1300],
            [900,1000,220,1300]]

    answer_bbs = [[1220,1300,180,800],
                [1350,1450,180,800],
                [1500,1600,180,800],
                [1650,1750,180,800],
                [1780,1880,180,800],
                [1940,2020,180,800],
                [2070,2170,180,800],
                [2220,2320,180,800],
                [2370,2470,180,800],
                [2500,2600,180,800],
                [2650,2750,180,800],
                [2800,2900,180,800],
                [2940,3030,180,800],
                [3080,3180,180,800],
                [3230,3330,180,800],
                
                [1220,1300,890,1550],
                [1350,1450,890,1550],
                [1500,1600,890,1550],
                [1650,1750,890,1550],
                [1780,1880,890,1550],
                [1940,2020,890,1550],
                [2070,2170,890,1550],
                [2220,2320,890,1550],
                [2370,2470,890,1550],
                [2500,2600,890,1550],
                [2650,2750,890,1550],
                [2800,2900,890,1550],
                [2940,3030,890,1550],
                [3080,3180,890,1550],
                [3230,3330,890,1550],

                [1220,1300,1610,2310],
                [1350,1450,1610,2310],
                [1500,1600,1610,2310],
                [1650,1750,1610,2310],
                [1780,1880,1610,2310],
                [1940,2020,1610,2310],
                [2070,2170,1610,2310],
                [2220,2320,1610,2310],
                [2370,2470,1610,2310],
                [2500,2600,1610,2310],
                [2650,2750,1610,2310],
                [2800,2900,1610,2310],
                [2940,3030,1610,2310],
                [3080,3180,1610,2310],
                [3230,3330,1610,2310],
                ]

    choices_bbs = [
                    [[1200,3350,515,700],[1200,3350,1230,1540],[1200,3350,1950,2270]],
                    [[1200,3350,600,740],[1200,3350,1320,1540],[1200,3350,2050,2270]],
                    [[1200,3350,700,840],[1200,3350,1410,1540],[1200,3350,2150,2270]]
    ]

    print("ID_DIGITS_NUM: ",ID_DIGITS_NUM)
    for i in range(-1,6 - ID_DIGITS_NUM,1):
        img[id_bbs[5-i][0]:id_bbs[5-i][1],id_bbs[5-i][2]:id_bbs[5-i][3]] = 255

    print("QUESTIONS_NUMBER: ",QUESTIONS_NUMBER)
    for i in range(-1,44 - QUESTIONS_NUMBER,1):
        img[answer_bbs[43-i][0]:answer_bbs[43-i][1],answer_bbs[43-i][2]:answer_bbs[43-i][3]] = 255

    print("CHOICES_NUM: ",CHOICES_NUM)
    for i in range(-1,4 - CHOICES_NUM,1):
        for bb in choices_bbs[1-i]:
            img[bb[0]:bb[1],bb[2]:bb[3]] = 255
  
    return img




def to_pdf(img,path_to_output):
    from PIL import Image
    Image.fromarray(img).save(path_to_output, "PDF" ,resolution=100.0, save_all=True)