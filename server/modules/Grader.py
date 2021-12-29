import numpy as np
import pandas as pd


class Grader:
  """
    Class used to take the scanned bubble sheet and detect ID and answers in it

    ...

    Attributes
    ----------
    CHOICES_NUM : int
        number of possible choices in question.
    
    WRONG_ANSWER_GRADE : float
        Penalty for each non-empty wrong answer.
    
    IS_MULTI_ANSWER : bool
        If the exam allow multiple answers for one question.
    
    answers : list
        list of strings describes model answer.
    
    questions_grade : list
        list of numbers describes the grade of each question.

    ALLOW_NEGATIVE_GRADES : bool (default=False)
        Indicates if the exam grade can be negative.
        If True, then Total = max(0,total grade).

    Methods
    -------
    calculate_grade(answers)
        return array contains the points for each question, total penalty and final grade.

    add_grade(ID,answers)
        Add new student answers to the Grader.
        return None.
    
    save(path)
        Save generated exccel report for student grades.
        return Dataframe of the generated table.
    """
  def __init__(self,CHOICES_NUM,WRONG_ANSWER_GRADE,IS_MULTI_ANSWER,answers,questions_grade,ALLOW_NEGATIVE_GRADES=False):
    self.CHOICES_NUM = CHOICES_NUM
    self.WRONG_ANSWER_GRADE = np.abs(WRONG_ANSWER_GRADE)
    self.IS_MULTI_ANSWER = IS_MULTI_ANSWER
    self.ALLOW_NEGATIVE_GRADES = ALLOW_NEGATIVE_GRADES
    self.model_answers = np.array(answers,dtype=object)
    self.questions_grade = np.array(questions_grade)
    self.QUESTIONS_NUMBER = len(answers)
    self.unknown_counter = 0
    self.students = {}
  
  def calculate_grade(self,answers):   
    # Assign 1 for each correct answer 
    points = (self.model_answers == np.array(answers,dtype=object)).astype(int)
    # Assign each correct answer its grade
    grades = points * self.questions_grade

    penalty_mask = np.array([False])
    if self.WRONG_ANSWER_GRADE != 0 :
        # Get the indecies of penalty    
        penalty_mask = (np.array(answers,dtype=object) != 'NOT ANSWERED') & (points == 0)
        # Assign the penalty to the question grade
        grades[penalty_mask] = -1 * self.WRONG_ANSWER_GRADE 
    # Calculate total grade with penalty
    total = np.sum(grades)
    # Return vector contains each points collected from each point, total penalty and total grade
    return np.hstack([grades,np.sum(penalty_mask.astype(int) * self.WRONG_ANSWER_GRADE) ,total if self.ALLOW_NEGATIVE_GRADES else np.max([total,0]) ])

  def add_grade(self,ID,answer):
    if ID not in self.students:
      self.students[ID] = self.calculate_grade(answer)
    elif ID == 'COULD NOT DETECT' or ID == 'NOT FILLED':
      self.students['{}: {}'.format(ID,self.unknown_counter)] = self.calculate_grade(answer)
      self.unknown_counter+=1

  def save(self,path):
    table = pd.DataFrame.from_dict(self.students).T.rename(columns={i:label  for i,label in enumerate(['Q({})'.format(i+1) if i < self.QUESTIONS_NUMBER else 'Penalty' if i == self.QUESTIONS_NUMBER else'Total'  for i in range(self.QUESTIONS_NUMBER+2)])})
    table.to_excel(path)
    return table
