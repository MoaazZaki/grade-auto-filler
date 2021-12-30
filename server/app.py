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
import pipeLine 

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/')
@cross_origin()
def main():
    return 'Welcome to the Grades Auto Filler Server!'

def savePhotos(request,functionOnSuccess):
       # check if the post request has the file part
    print(request.files)
    if 'files[]' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
 
    files = request.files.getlist('files[]')
     
    errors = {}
    success = False
     
    for file in files:      
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(app.config['UPLOAD_FOLDER']+ filename)
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
        now = datetime.now().isoformat().replace(".","").replace("-","").replace(":","")
        output_csv_path=app.config['UPLOAD_FOLDER']+now+".xlsx"
        pipeLine.grade_sheet_pipeline(app.config['UPLOAD_FOLDER']+ filename,output_csv_path)
        resp = jsonify({'excelFile' : request.base_url.replace("grades","")+output_csv_path})
        resp.status_code = 201
        return resp
    #call sendCSV if saving the photo is successful
    return savePhotos(request,sendCSV)
 
    
@app.route('/bubble/paper', methods=['POST'])
@cross_origin()
def generate_bubble_sheet():
    data=request.get_json()
    print(data) #TODO generate the image from the info 
    print(data["numberOfQuestions"])
    # ex: {'numberOfChoices': 3, 'numberOfQuestions': 20, 'numberOfIdDigits': 5}
    #TODO: save the phote in pathToImage with a name of imageName
    imageName= "1.jpg" #TODO: change this to be dynamic
    pathToImage=app.config['UPLOAD_FOLDER'] #TODO: change this to a subfolder if you wish
    output_image_path=pathToImage+imageName
    resp = jsonify({'paper' : request.base_url.replace("bubble/paper","")+output_image_path})
    resp.status_code = 201
    return resp
    

@app.route('/bubble/grade', methods=['POST'])
@cross_origin()
def grade_bubble_sheet():
    def sendBubbleSheetGrade(filename):
        data=request.form
        print(data) #TODO calculate the grade from the info 
        print(data["numberOfQuestions"])
        print(json.loads(data['answers'])) #Note: arrays require json decoding
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
        # and the image is found in app.config['UPLOAD_FOLDER']+ filename
        print(app.config['UPLOAD_FOLDER']+ filename)
        resp = jsonify({'grade' : 50})
        resp.status_code = 200
        return resp
    #call sendBubbleSheetGrade if saving the photo is successful
    return savePhotos(request,sendBubbleSheetGrade) 
 
if __name__ == '__main__':
    app.run(debug=True)
