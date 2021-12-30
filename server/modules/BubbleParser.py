import numpy as np
import cv2
import matplotlib.pyplot as plt

def iou(boxA, boxB):
  xA = max(boxA[0], boxB[0])
  yA = max(boxA[1], boxB[1])
  xB = min(boxA[0]+boxA[2], boxB[0]+boxB[2])
  yB = min(boxA[1]+boxA[3], boxB[1]+boxB[3])


  interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

  boxAArea = (boxA[2]+ 1) * (boxA[3]+1)
  boxBArea = (boxB[2]+ 1) * (boxB[3]+ 1)

  iou = interArea / float(boxAArea + boxBArea - interArea)

  return iou

class BubbleParser:
  """
    Class used to take the scanned bubble sheet and detect ID and answers in it

    ...

    Attributes
    ----------
    ID_DIGITS_NUM : int
        number of digits in ID.

    CHOICES_NUM : int
        number of possible choices in question.
    
    ROW_Y_ALLOWANCE : int
        the empty margin between ID and ANSWERS.
    
    X_START_ALLOWANCE : int
        the minimum alloawance to consider a bounding box the start of row.
    
    MIN_RADIUS : int
        minimum radius of circules to detect.
    
    MAX_RADIUS : int
        maximum radius of circles to detect.

    ANSWER_AREA_RATIO : float
        ratio range between 0-1 corresponds to the area of ones over the image area.
    
    ANSWER_THRESHOLD : int
        threshold range between 0-255 corresponds to the threshold to convert the image to binary.
    
    IOU_MIN_RATIO : float
        minimum itersection over uniuon value to consider two bounding boxes not overlapped.

    visualize : boolean
        show the detected circles in the image for debugging.
    Methods
    -------
    remove_overlapped_bbs(bbs)
        return all non-overlapped bounding boxes from list of bounding boxes

    detect_circles(scanned,edged)
        return array of detected circles in the form of (cx,cy,r), where:
        cx => x value of circle center 
        cy => y value of circle center 
        r  => radius of circle
    
    circles_to_bbs(detected_circles)
        return id_rows and answer_rows in the form of bounding boxes (x,y,w,h) sorted from top to bottom and left to right.
    
    arrange_answers_wrapper(rows)
        return arrange the answers from question 1 to k, where k is the number of questions on paper.
    
    extract_filled(thresh,id_rows,answer_rows)
        return the filled bubbles values from the binary image "thresh" in the form of ID and answers ('A','B','C',..)

        when mutliple id bubbles are filled in at least one row, ID will be 'COULD NOT DETECT'
        when no filled bubbles in at least on row, ID will be 'NOT FILLED'

        when a question has multiple answers, the returned value is list of the answers. Ex: ['A','E']
        when a question has no filled bubble, the returned value is 'NOT ANSWERED'
    
    extract(img,edged)
        return ID and answers in the paper after perfoming the extraction pipeline
    """
  def __init__(self,ID_DIGITS_NUM,CHOICES_NUM,ROW_Y_ALLOWANCE = 20,X_START_ALLOWANCE = 7,HOUGH_THRESHOLD=25,MIN_RADIUS =10,MAX_RADIUS=50,ANSWER_AREA_RATIO=0.85,ANSWER_THRESHOLD=165,IOU_MIN_RATIO=0.05,visualize=False):
    self.ID_DIGITS_NUM = ID_DIGITS_NUM
    self.CHOICES_NUM = CHOICES_NUM
    self.ROW_Y_ALLOWANCE = ROW_Y_ALLOWANCE
    self.X_START_ALLOWANCE = X_START_ALLOWANCE
    self.MIN_RADIUS = MIN_RADIUS
    self.MAX_RADIUS = MAX_RADIUS
    self.ANSWER_AREA_RATIO = ANSWER_AREA_RATIO
    self.ANSWER_THRESHOLD = ANSWER_THRESHOLD
    self.IOU_MIN_RATIO = IOU_MIN_RATIO
    self.HOUGH_THRESHOLD =HOUGH_THRESHOLD
    self.visualize = visualize

  def remove_overlapped_bbs(self,bbs):
    # No more overlapped bbs
    if len(bbs) <= 1:
      return bbs
    # Get the intersection over union value of the first two bbs
    iou_val = iou(bbs[0],bbs[1])
    if iou_val > self.IOU_MIN_RATIO:
      # If the two bbs are overlapped, take one with larger area
      return [bbs[0]] + self.remove_overlapped_bbs(bbs[2:]) if bbs[0][-2] * bbs[0][-1] >= bbs[1][-2] * bbs[1][-1] else [bbs[1]] + self.remove_overlapped_bbs(bbs[2:])
    else:
      # If no overlapped detected, take the first bb
      return [bbs[0]] + self.remove_overlapped_bbs(bbs[1:])
  
  def detect_circles(self,scanned,edged):
    img_vis = None
    if self.visualize:
      img_vis = scanned.copy()

    # Get the circles using hough transform
    detected_circles = cv2.HoughCircles(edged, 
                      cv2.HOUGH_GRADIENT, 1, 20, param1 = 100,
                  param2 = self.HOUGH_THRESHOLD, minRadius = self.MIN_RADIUS, maxRadius = self.MAX_RADIUS)
      

    # Draw circles (for debugging only)
    if detected_circles is not None:
      
        
        detected_circles = np.uint16(np.around(detected_circles))
        
        if img_vis is not None:
          for pt in detected_circles[0, :]:
              a, b, r = pt[0], pt[1], pt[2]
              cv2.circle(img_vis, (a, b), r, (0, 255, 0), 6)

          plt.figure(figsize=(20,20))
          plt.imshow(img_vis)
          
    return detected_circles


  def circles_to_bbs(self,detected_circles):
    # Function to check if value is in range [b1,b2]
    check_in_range = lambda value,b1,b2: value >= b1 and value <= b2

    # Extract cx,cy,r of each circle and sort them from top to bottom
    centers = detected_circles[0]
    centers = np.array(sorted(centers,key= lambda c: c[1]))

    # Calculate average circles radius
    avg_circle_radii = centers[:,2].mean()
    #print(avg_circle_radii)
    current_row = []
    current_cy = []
    rows = []
    i = 0

    for cx,cy,r in centers:
      
      # if the circle belongs to the current row
      if len(current_cy) == 0 or (cy <= np.mean(current_cy) + avg_circle_radii):
        current_row.append([cx-r,cy-r,2*r,2*r]) # convert the circle to bb (x,y,w,h)
        current_cy.append(cy)
      else:
        rows.append(sorted(current_row,key= lambda bb: bb[0])) # when end of row is reached, insert the row sorted from left right
        current_row = [[cx-r,cy-r,2*r,2*r]]
        current_cy = [cy]

      i+=1

      if i == len(centers):
        rows.append(sorted(current_row,key= lambda bb: bb[0]))


    rows = np.array(rows,dtype=object)

    # Get the number of circles in each row
    rows_cirecles_num = np.array([len(row) for row in rows])
    # If circles in row is greater than the minimum number of circles (the number of choices in question), then it is a correct row
    correct_rows_mask = rows_cirecles_num >= self.CHOICES_NUM
    # Exculde rows that has only noise
    rows = rows[correct_rows_mask]
    rows_cirecles_num = rows_cirecles_num[correct_rows_mask]

    # Get the ID rows
    id_rows_mask =  rows_cirecles_num >= 10
    id_rows = rows[id_rows_mask][:self.ID_DIGITS_NUM]
    id_rows_cirecles_num = rows_cirecles_num[id_rows_mask][:self.ID_DIGITS_NUM]

    # Get the average x value of the start of each correctly detected id row
    id_x_start = [row[0][0] for row in id_rows if len(row) == 10]
    avg_id_x_start = np.mean([row[0][0] for row in id_rows if len(row) == 10]) if len(id_x_start) != 0 else 0
    # Remove overelapped circles in each row
    id_rows = [row if len(row) == 10 else self.remove_overlapped_bbs(row) for row in id_rows]
    # Remove noisy circles in each row
    id_rows = [row if len(row) == 10 else row[:10] if check_in_range(row[0][0],avg_id_x_start- self.X_START_ALLOWANCE,avg_id_x_start+ self.X_START_ALLOWANCE) or avg_id_x_start == 0 else row[1:11] for row in id_rows]
    id_rows = np.array(id_rows)

    # Calculate the last y value for id rows
    id_last_y = id_rows[-1,-1,1] + id_rows[-1,-1,-1] + self.ROW_Y_ALLOWANCE
    
    # Get the first asnwers row
    first_answer_i = self.ID_DIGITS_NUM
    for i in range(self.ID_DIGITS_NUM,len(rows)):
      if rows[i][0][1] > id_last_y:
        first_answer_i = i
        break

    answer_rows = rows[first_answer_i:]
    rows_cirecles_num = rows_cirecles_num[first_answer_i:]
    # Remove overlapped circles
    answer_rows = [self.remove_overlapped_bbs(row) for row in answer_rows]
    # Get the number of circles in each row
    rows_cirecles_num = np.array([len(row) for row in answer_rows])
    # Get the rows that have wrong number of circles (every row should has circle number divisible by number of choices in question)
    answers_wrong_rows_mask = rows_cirecles_num%self.CHOICES_NUM != 0
    
    # Calculating the average x value of each column start
    correct_answer_rows = []
    for i in np.where(~answers_wrong_rows_mask)[0]:
      correct_answer_rows.append(np.array(answer_rows[i]))

    col_x_start =  [[bb[0] for bb in row] for row in correct_answer_rows]
    avgs_list = []
    col_i = 0
    for row in col_x_start:
      while col_i < len(row):
        avgs_list.append([])
        col_i += 1
      for i in range(len(row)):
        avgs_list[i].append(row[i])
    

    avg_cols_x_start = [np.mean(col) for col in avgs_list]
    # Removing noisy bounding boxes by excluding the k largest differences from the closest column  (x value of bb - x value of the closest column) 
    for i in np.where(answers_wrong_rows_mask)[0]:
      bbs = np.array(answer_rows[i])
      target_length = int(len(bbs) / self.CHOICES_NUM) * self.CHOICES_NUM 
      best_inds = np.argpartition([np.min(np.abs(x - avg_cols_x_start)) for x  in bbs[:,0]],target_length)[:target_length]
      best_inds = sorted(best_inds)
      answer_rows[i]= bbs[best_inds]
    
    return id_rows,answer_rows

  def arrange_asnwers(self,rows,a,col=0):
    finished_rows = 0 # Rows that no more have columns to iterate on
    for row in rows:
      # If the currect row has more questions in it
      if len(row) > col*self.CHOICES_NUM:
        a.append(row[col*self.CHOICES_NUM:col*self.CHOICES_NUM+self.CHOICES_NUM])
      else:
        finished_rows += 1

    if finished_rows != len(rows):
      self.arrange_asnwers(rows,a,col+1)
  
  def arrange_answers_wrapper(self,rows):
    a = []
    self.arrange_asnwers(rows,a)
    return a
  
  def extract_filled(self,thresh,id_rows,answer_rows):
    bubble_area_ratios = []
    for row in id_rows:
      # Append the number of ones / area of image in a cropped version of bubble  
      bubble_area_ratios.append([np.sum(thresh[bb[1]+int(bb[3]/4):bb[1]+int(0.75*bb[3]),bb[0]+int(bb[2]/4):bb[0]+int(0.75*bb[2])])/(0.25*bb[2]*bb[3]) for bb in row])

    ID = ''
    bubble_area_ratios = np.array(bubble_area_ratios)
    detected_bubbles = np.sum(bubble_area_ratios >= self.ANSWER_AREA_RATIO)
    if detected_bubbles > self.ID_DIGITS_NUM:
      ID = 'COULD NOT DETECT'
    elif detected_bubbles < self.ID_DIGITS_NUM:
      ID = 'NOT FILLED'
    else:
      max_inds = np.argmax(bubble_area_ratios,axis=1).astype(str)
      ID = ''.join(max_inds)
    

    answers = []
    answers_mapper = {i:chr(ord('A') + i) for i in range(self.CHOICES_NUM)}
    for row in answer_rows:
      # Append the number of ones / area of image in a cropped version of bubble  
      row_bubbles_area_raito = np.array([np.sum(thresh[bb[1]+int(bb[3]/4):bb[1]+int(0.75*bb[3]),bb[0]+int(bb[2]/4):bb[0]+int(0.75*bb[2])])/(0.25*bb[2]*bb[3]) for bb in row])
      # if question has only one answer
      if np.sum(row_bubbles_area_raito >= self.ANSWER_AREA_RATIO) == 1:
        answers.append(answers_mapper[row_bubbles_area_raito.argmax()])
      # if question has multiple answers
      elif np.sum(row_bubbles_area_raito >= self.ANSWER_AREA_RATIO) > 1:
        answers.append([answers_mapper[ind] for ind in np.where(row_bubbles_area_raito >= self.ANSWER_AREA_RATIO)[0]])
      else:
        answers.append('NOT ANSWERED')


    return ID,answers
  
  def extract(self,img,edged):
    # Get the binary image
    _, thresh = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), self.ANSWER_THRESHOLD , 1,cv2.THRESH_BINARY_INV)
    # Get the bubbles (cx,cx,r)
    detected_bubbles = self.detect_circles(img,edged)
    # Sort bubbles to id_rows and answer_rows
    # and Extract ID and answers in the paper
    id_rows,answer_rows = self.circles_to_bbs(detected_bubbles)
    
    # arrange answer rows to be in the form 1..k where k is the number of questions
    answer_rows = self.arrange_answers_wrapper(answer_rows)
   
    
    return self.extract_filled(thresh,id_rows,answer_rows)
