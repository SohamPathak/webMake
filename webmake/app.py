import os
from flask import Flask, request, redirect, url_for ,render_template,flash,Response
from werkzeug.utils import secure_filename
try:
    from PIL import Image
except ImportError:
    import Image
import requests

import cv2
#from IPython.display import clear_output
import pytesseract
pytesseract.pytesseract.tesseract_cmd ='D:/Tesseract-OCR/tesseract'

#useful links
#https://gist.github.com/hosackm/289814198f43976aff9b :: audio
#https://stackoverflow.com/questions/24892035/how-can-i-get-the-named-parameters-from-a-url-using-flask :: get parameter route capturing
#

UPLOAD_FOLDER = 'C:/Users/KIIT_Intern/Desktop/image enhencer/Medi-Help-master/new medihelp/static/images'
UPLOAD_FOLDER2 = 'C:/Users/KIIT_Intern/Desktop/image enhencer/Medi-Help-master/new medihelp/static'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

global summary
summary = ''


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def page_maker(divs):
    count = 0
    f= open("C:/Users/KIIT_Intern/Desktop/image enhencer/Medi-Help-master/new medihelp/templates/webit.html","w+")
    f.write("<!DOCTYPE html>")
    f.write("<html>")
    f.write("<head>")
    f.write("</head>")
    f.write('<body style="background-color: powderblue;">')
    for d in divs:

        f.write("<div id='thediv'"+'style="position: absolute;left:'+str(d[0])+'px;top:'+str(d[1])+'px;width:'+str(d[2])+'px;height:'+str(d[3])+'px;border-style: solid">'+'DivNo._'+str(count)+'</div>')
        count = count+1
    
    f.write("</body>")
    f.write("</html>")
    
    f.close() 


def process(filena):
    
    print(filena)

    path = 'C:/Users/KIIT_Intern/Desktop/image enhencer/Medi-Help-master/new medihelp/static/images/'
    filee = str(filename)
    image = cv2.imread(path+filee)
    blur = cv2.pyrMeanShiftFiltering(image, 11, 21)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    count =0
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # for c in cnts:
    #     peri = cv2.arcLength(c, True)
    #     approx = cv2.approxPolyDP(c, 0.015 * peri, True)
    #     if len(approx) == 4:
    #         count = count+1
    #         x,y,w,h = cv2.boundingRect(approx)
    #         cv2.rectangle(image,(x,y),(x+w,y+h),(36,255,12),2)
    #         iii = cv2.rectangle(image,(x,y),(x+w,y+h),(36,255,12),2)
    #         cv2.imwrite('image'+str(count)+'.png',iii)
    l = []        
    ROI_number = 0
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.015 * peri, True)  
        if len(approx) == 4:
            x,y,w,h = cv2.boundingRect(approx)
            if ((w > 50)and(h>50)):
                ROI = image[y:y+h, x:x+w]
                j = [x,y,w,h]
                l.append(j)
                cv2.imwrite('ROI_{}.png'.format(ROI_number), ROI)
                cv2.rectangle(image,(x,y),(x+w,y+h),(36,255,12),2)
                iii = cv2.rectangle(image,(x,y),(x+w,y+h),(36,255,12),2)
                cv2.imwrite(path+'image'+str(ROI_number)+'.png',iii)
                txt =pytesseract.image_to_string('ROI_{}.png'.format(ROI_number))
                print(txt)
                ROI_number += 1  
                
    page_maker(l)    
    print(len(cnts))

    return ROI_number-1






@app.route('/', methods=['GET', 'POST'])
def upload_file():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            #global filename
            global filename
            filename = secure_filename(file.filename)
            
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return redirect(url_for('getsummary'))
           # return redirect(url_for('upload_file',filename=filename))      
    return render_template('account.html')

@app.route('/getsummary', methods=['GET', 'POST'])
def getsummary():
    global filename 
    global roi
    roi = process(filename)
 
    return render_template('result.html',filename = filename ,roi = roi)

@app.route('/webpage', methods=['GET','POST'])
def webpage():

    return render_template('webit.html')

#def whichlang():



# @app.route('/playaudio',methods=['GET'])
# def playaudio():

#     #language = whichlang()
#     #language = 'en'
#     language = request.args.get('language')
#     summary = ''
#     filename = 'testimage.jpeg'
#     summary = process(filename)
#     tts = gTTS(text=summary, lang=language, slow=False)
#     filename = 'voice.wav'
#     #path = os.path.join(app.config['UPLOAD_FOLDE'], filename)
#     tts.save(os.path.join(app.config['UPLOAD_FOLDER2'], filename))
#     #return render_template('audio.html',summary = summary)
#     def generate():
#         with open("static/voice.wav", "rb") as fwav:
#             data = fwav.read(1024)
#             while data:
#                 yield data
#                 data = fwav.read(1024)
#     return Response(generate(), mimetype="audio/x-wav")

    

    #return '''
    #<!doctype html>
    #<title>Upload new File</title>
    #<h1>Upload new File</h1>
    #<form method=post enctype=multipart/form-data>
    #  <p><input type=file name=file>
    #     <input type=submit value=Upload>
    #</form>
    #'''


if __name__ == '__main__':
    app.run(debug=True)    