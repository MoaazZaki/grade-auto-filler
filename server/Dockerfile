FROM ubuntu:20.04
RUN mkdir /app
WORKDIR /app
COPY . /app

RUN apt-get update -y
RUN apt install -y software-properties-common 
RUN apt install -y python3.9
RUN apt install -y python3-pip
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt install -y tesseract-ocr
RUN pip3 install numpy opencv-contrib-python
RUN pip3 install -r requirements.txt
RUN pip3 install pytesseract
RUN pip3 install openpyxl

EXPOSE 5000

CMD ["python3", "app.py"]