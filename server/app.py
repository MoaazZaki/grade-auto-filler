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
 
@app.route('/grades', methods=['POST'])
@cross_origin()
def grade_sheets():
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
        now = datetime.now().isoformat().replace(".","").replace("-","").replace(":","")
        output_csv_path=app.config['UPLOAD_FOLDER']+now+".xlsx"
        pipeLine.grade_sheet_pipeline(app.config['UPLOAD_FOLDER']+ filename,output_csv_path)
        resp = jsonify({'excelFile' : request.base_url.replace("grades","")+output_csv_path})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
 
if __name__ == '__main__':
    app.run(debug=True)
