from flask import Flask, json, request, jsonify
from modules import CellDetector
from modules.CellDetector import CellDetector
from modules.Scanner import Scanner
from utils import helpers as hlp
import os,glob
import urllib.request
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import cv2
from datetime import datetime
import pipeLine 
import numpy as np
import os


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

print('APP STARTED')

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/', methods=['GET','POST'])
@cross_origin()
def main():
    return 'Welcome to the Grades Auto Filler Server!'

def savePhotos(request,functionOnSuccess,folder=""):
       # check if the post request has the file part
       
    if folder != "":
        files = glob.glob(app.config['UPLOAD_FOLDER']+folder+ '*')
        for f in files:
            os.remove(f)
   
    if 'files[]' not in request.files and 'files[0]' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
 
    errors = {}
    success = False
    
    if 'files[0]' in request.files:
        filesCounter=0
        while len(request.files.getlist('files[{}]'.format(filesCounter))):
            files = request.files.getlist('files[{}]'.format(filesCounter))
            for file in files:      
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(app.config['UPLOAD_FOLDER']+folder+ filename)
                    success = True
                else:
                    errors[file.filename] = 'File type is not allowed'
            filesCounter+=1
            
     
    if 'files[]' in request.files:
        files = request.files.getlist('files[]')
        for file in files:      
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(app.config['UPLOAD_FOLDER']+folder+ filename)
                success = True
            else:
                errors[file.filename] = 'File type is not allowed'
 
    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    if success:
        return functionOnSuccess(filename)
       
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
 
@app.route('/grades', methods=['POST'])
@cross_origin()
def grade_sheets():
    def sendCSV(filename):
        data=request.form
        
        colsToDrop=json.loads(data["colsToDrop"])
        digitsCols=json.loads(data["digitsCols"])
        symbolsCols=json.loads(data["symbolsCols"])
        now = datetime.now().isoformat().replace(".","").replace("-","").replace(":","")
        output_csv_path=app.config['UPLOAD_FOLDER']+now+".xlsx"
        pipeLine.grade_sheet_pipeline(app.config['UPLOAD_FOLDER']+ filename,output_csv_path,digitsCols,colsToDrop,symbolsCols)
        resp = jsonify({'excelFile' : request.base_url.replace("grades","")+output_csv_path})
        resp.status_code = 201
        return resp
    #call sendCSV if saving the photo is successful
    return savePhotos(request,sendCSV)
 
    
@app.route('/bubble/paper', methods=['POST'])
@cross_origin()
def generate_bubble_sheet():
    data=request.get_json()
    print(data)
    # ex: {'numberOfChoices': 3, 'numberOfQuestions': 20, 'numberOfIdDigits': 5}
    now = datetime.now().isoformat().replace(".","").replace("-","").replace(":","")
    pdfName= now+".pdf" #TODO: change this to be dynamic
    pathToImage=app.config['UPLOAD_FOLDER'] #TODO: change this to a subfolder if you wish
    output_pdf_path=pathToImage+pdfName
    hlp.to_pdf(hlp.generate_bubble_sheet('static/assets/MCQ_paper.png',int(data["numberOfIdDigits"]),int(data["numberOfQuestions"]),int(data["numberOfChoices"])),output_pdf_path)
    resp = jsonify({'paper' : request.base_url.replace("bubble/paper","")+output_pdf_path})
    resp.status_code = 201
    return resp
    

@app.route('/bubble/grade', methods=['POST'])
@cross_origin()
def grade_bubble_sheet():
    gradesFolder="grades/"
    def sendBubbleSheetGrade(filename):
        data=request.form
        now = datetime.now().isoformat().replace(".","").replace("-","").replace(":","")
        excelFileName = now+".xlsx"
        outputExcelPath=app.config['UPLOAD_FOLDER'] + excelFileName
        pipeLine.bubble_sheet_pipeline(app.config['UPLOAD_FOLDER'] + gradesFolder[0:-1],
                                       list(json.loads(data['answers'])), #model answer
                                       json.loads(data["questionsQrades"]), #answer grades
                                       outputExcelPath, 
                                       int(data["numberOfIdDigits"]) , 
                                       int(data["numberOfChoices"]),
                                       True if data["allowMultiAnswers"]=="true" else False ,
                                       float(data["wrongAnswerGrade"]),
                                       True if data["allowNegativeGrades"]=="true" else False
                                       )
        '''
        fields in data:
        numberOfChoices: number
        numberOfQuestions: number
        wrongAnswerGrade: number
        allowMultiAnswers: boolean
        allowNegativeGrades: boolean
        answers: Array<Array<'a' | 'b' | 'c' | 'd' | 'e'> | ('a' | 'b' | 'c' | 'd' | 'e') >
        questionsQrades:Array<number>
        '''
        #and the image is found in app.config['UPLOAD_FOLDER']+ filename
        resp = jsonify({'grades' : request.base_url.replace("bubble/grade","")+ outputExcelPath})
        resp.status_code = 200
        return resp
    #call sendBubbleSheetGrade if saving the photo is successful
    return savePhotos(request,sendBubbleSheetGrade,folder=gradesFolder) 
 
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',port=port,debug=True)
