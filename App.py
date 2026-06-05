from flask import Flask, render_template, request, session, flash, jsonify
import sys
import mysql.connector
import numpy as np
import pickle
import json
from flask import Flask, render_template, request
import nltk
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# chat initialization
model = load_model("chatbot_model.h5")
intents = json.loads(open("intents.json").read())
words = pickle.load(open("words.pkl", "rb"))
classes = pickle.load(open("classes.pkl", "rb"))


app = Flask(__name__)
app.config['SECRET_KEY'] = 'aaa'


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/Chat')
def Chat():
    #return render_template('Chatbot.html')
    return render_template('ChatBot.html')


@app.route("/ask",  methods=['GET', 'POST'])
def ask():

    message = str(request.form['messageText'])
    #msg = request.form["msg"]
    msg = message
    if msg.startswith('my name is'):
        name = msg[11:]
        ints = predict_class(msg, model)
        res1 = getResponse(ints, intents)
        res = res1.replace("{n}", name)
    elif msg.startswith('hi my name is'):
        name = msg[14:]
        ints = predict_class(msg, model)
        res1 = getResponse(ints, intents)
        res = res1.replace("{n}", name)

    elif msg.startswith('exit'):
        res = '<a href="http://127.0.0.1:5000/UserHome">Exit</a>'

    else:
        ints = predict_class(msg, model)
        res = getResponse(ints, intents)
    #return res
    return jsonify({'status':'OK','answer':res})

@app.route("/get")
def chatbot_response():
    msg = request.args.get('msg')
    if msg.startswith('my name is'):
        name = msg[11:]
        ints = predict_class(msg, model)
        res1 = getResponse(ints, intents)
        res =res1.replace("{n}",name)
    elif msg.startswith('hi my name is'):
        name = msg[14:]
        ints = predict_class(msg, model)
        res1 = getResponse(ints, intents)
        res =res1.replace("{n}",name)
    else:
        ints = predict_class(msg, model)
        res = getResponse(ints, intents)
    return res


# chat functionalities
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    print(res)
    ERROR_THRESHOLD = 0.10
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    print(results)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
        print(return_list.append({"intent": classes[r[0]], "probability": str(r[1])}))
    return return_list


'''def getResponse(ints, intents_json):
    tag = ints[0]["intent"]
    list_of_intents = intents_json["intents"]
    for i in list_of_intents:
        if i["tag"] == tag:
            result = random.choice(i["responses"])
            break
    return result'''


import random

def getResponse(ints, intents_json):
    if not ints:
        return "I'm sorry, I didn't understand that."

    tag = ints[0].get("intent")
    list_of_intents = intents_json.get("intents", [])

    for intent in list_of_intents:
        if intent["tag"] == tag:

            # ✅ Pick ONE random response (not full list)
            response = random.choice(intent["responses"])

            # ✅ Get precaution safely
            precaution = intent.get("Precaution", "")

            # If precaution is list, join it
            if isinstance(precaution, list):
                precaution = "<br>".join(precaution)

            # Final output
            if precaution:
                return response + "<br>" + precaution
            else:
                return response

    return "I'm sorry, I don't have a response for that."


@app.route('/AdminLogin')
def AdminLogin():
    return render_template('AdminLogin.html')


@app.route('/NewFaculty')
def NewFaculty():
    return render_template('NewFaculty.html')


@app.route('/FacultyLogin')
def FacultyLogin():
    return render_template('FacultyLogin.html')


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    error = None
    if request.method == 'POST':
        if request.form['uname'] == 'admin' and request.form['password'] == 'admin':

            conn = mysql.connector.connect(user='root', password='', host='localhost', database=' 1faceemotionmusicchatdashdb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb")
            data = cur.fetchall()
            flash("You are Logged In...!")
            return render_template('AdminHome.html', data=data)

        else:
            flash("UserName or Password is Wrong...!")
            return render_template('index.html', error=error)


@app.route("/AdminHome")
def AdminHome():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database=' 1faceemotionmusicchatdashdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb")
    data = cur.fetchall()
    return render_template('AdminHome.html', data=data)


@app.route("/Report")
def Report():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database=' 1faceemotionmusicchatdashdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM reporttb")
    data = cur.fetchall()
    return render_template('Report.html', data=data)


@app.route("/newfac", methods=['GET', 'POST'])
def newfac():
    if request.method == 'POST':
        name = request.form['uname']
        mobile = request.form['mobile']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database=' 1faceemotionmusicchatdashdb')
        cursor = conn.cursor()
        cursor.execute(
            "insert into regtb values('','" + name + "','" + mobile + "','" + email + "','" + username + "','" + password + "')")
        conn.commit()
        conn.close()
        flash("Record Saved!")
    return render_template('FacultyLogin.html')


@app.route("/facultylogin", methods=['GET', 'POST'])
def facultylogin():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        session['fname'] = request.form['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database=' 1faceemotionmusicchatdashdb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + username + "' and password='" + password + "'")
        data = cursor.fetchone()
        if data is None:

            flash("UserName Or  Password Incorrect!")
            return render_template('FacultyLogin.html')
        else:

            session['mob'] = data[2]
            session['email'] = data[3]
            emotion()
            conn = mysql.connector.connect(user='root', password='', host='localhost', database=' 1faceemotionmusicchatdashdb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb where username='" + username + "' and password='" + password + "'")
            data = cur.fetchall()
            return render_template('FacultyHome.html', data=data)


def emotion():
    import csv
    import copy
    import itertools

    import cv2 as cv
    import numpy as np
    import mediapipe as mp
    from model import KeyPointClassifier
    import os

    os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'

    def calc_landmark_list(image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        landmark_point = []

        # Keypoint
        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)

            landmark_point.append([landmark_x, landmark_y])

        return landmark_point

    def pre_process_landmark(landmark_list):
        temp_landmark_list = copy.deepcopy(landmark_list)

        # Convert to relative coordinates
        base_x, base_y = 0, 0
        for index, landmark_point in enumerate(temp_landmark_list):
            if index == 0:
                base_x, base_y = landmark_point[0], landmark_point[1]

            temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
            temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

        # Convert to a one-dimensional list
        temp_landmark_list = list(
            itertools.chain.from_iterable(temp_landmark_list))

        # Normalization
        max_value = max(list(map(abs, temp_landmark_list)))

        def normalize_(n):
            return n / max_value

        temp_landmark_list = list(map(normalize_, temp_landmark_list))

        return temp_landmark_list

    def draw_bounding_rect(use_brect, image, brect):
        if use_brect:
            # Outer rectangle
            cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]),
                         (0, 0, 0), 1)

        return image

    def calc_bounding_rect(image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]

        landmark_array = np.empty((0, 2), int)

        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)

            landmark_point = [np.array((landmark_x, landmark_y))]

            landmark_array = np.append(landmark_array, landmark_point, axis=0)

        x, y, w, h = cv.boundingRect(landmark_array)

        return [x, y, x + w, y + h]

    def draw_info_text(image, brect, facial_text):
        cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22),
                     (0, 0, 0), -1)

        if facial_text != "":
            info_text = 'Emotion :' + facial_text
        cv.putText(image, info_text, (brect[0] + 5, brect[1] - 4),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)

        return image

    cap_device = 0
    cap_width = 800
    cap_height = 600

    use_brect = True

    # Camera preparation
    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    # Model load
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)

    keypoint_classifier = KeyPointClassifier()

    # Read labels
    with open('model/keypoint_classifier/keypoint_classifier_label.csv',
              encoding='utf-8-sig') as f:
        keypoint_classifier_labels = csv.reader(f)
        keypoint_classifier_labels = [
            row[0] for row in keypoint_classifier_labels
        ]

    mode = 0
    flag = 0
    flag1 = 0
    c1 = 0
    c2 = 0
    c3 = 0
    c4 = 0
    c5 = 0
    c6 = 0

    while True:

        # Process Key (ESC: end)
        key = cv.waitKey(10)
        if key == 27:  # ESC
            break

        # Camera capture
        ret, image = cap.read()
        if not ret:
            break
        image = cv.flip(image, 1)  # Mirror display
        debug_image = copy.deepcopy(image)

        # Detection implementation
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = face_mesh.process(image)
        image.flags.writeable = True

        if results.multi_face_landmarks is not None:
            for face_landmarks in results.multi_face_landmarks:
                # Bounding box calculation
                brect = calc_bounding_rect(debug_image, face_landmarks)

                # Landmark calculation
                landmark_list = calc_landmark_list(debug_image, face_landmarks)

                # Conversion to relative coordinates / normalized coordinates
                pre_processed_landmark_list = pre_process_landmark(
                    landmark_list)

                # emotion classification
                facial_emotion_id = keypoint_classifier(pre_processed_landmark_list)
                # Drawing part
                debug_image = draw_bounding_rect(use_brect, debug_image, brect)
                debug_image = draw_info_text(
                    debug_image,
                    brect,
                    keypoint_classifier_labels[facial_emotion_id])

                emo = keypoint_classifier_labels[facial_emotion_id]
                print(emo)

                # ================= FACE CROP =================
                # Full face with label rectangle save

                x1 = brect[0]
                y1 = brect[1]
                x2 = brect[2]
                y2 = brect[3]

                # Copy original frame
                save_img = debug_image.copy()

                # Draw rectangle
                cv.rectangle(save_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Draw emotion label
                cv.putText(
                    save_img,
                    emo,
                    (x1, y1 - 10),
                    cv.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                    cv.LINE_AA
                )

                # ================= ANGRY =================
                if emo == "Angry":

                    c1 += 1

                    if c1 == 200:

                        import datetime
                        import time
                        import os

                        name = session['fname']

                        ts = time.time()

                        date = datetime.datetime.now().strftime('%d-%b-%Y')
                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H-%M-%S')

                        # Folder Create
                        if not os.path.exists("static/faces"):
                            os.makedirs("static/faces")

                        # Image Name
                        img_name = name + "_" + emo + "_" + timeStamp + ".jpg"

                        img_path = "static/faces/" + img_name

                        # SAVE FULL IMAGE WITH LABEL
                        cv.imwrite(img_path, save_img)

                        # DATABASE
                        conn = mysql.connector.connect(
                            user='root',
                            password='',
                            host='localhost',
                            database='1faceemotionmusicchatdashdb'
                        )

                        cursor = conn.cursor()

                        cursor.execute(
                            "INSERT INTO reporttb VALUES('',%s,%s,%s,%s,%s)",
                            (name, date, timeStamp, emo, img_path)
                        )

                        conn.commit()
                        conn.close()

                        cv.waitKey(2)

                        cap.release()

                        cv.destroyAllWindows()

                        for i in range(1, 5):
                            cv.waitKey(1)

                        session['emo'] = emo
                        session['img'] = img_path

                        sendmsg(session['mob'], "Your Child is Very Angry")
                        sendmail(img_path,'😡 Take a deep breath and relax for few minutes')
                        flash("You Are 😡 " + str(emo))
                        import AngryMusicl
                        return render_template(
                            'FacultyHome.html',
                            emo=session['emo'],
                            img=session['img']
                        )

                # ================= HAPPY =================
                if emo == "Happy":

                    c2 += 1

                    if c2 == 200:

                        import datetime
                        import time
                        import os

                        name = session['fname']

                        ts = time.time()

                        date = datetime.datetime.now().strftime('%d-%b-%Y')
                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H-%M-%S')

                        if not os.path.exists("static/faces"):
                            os.makedirs("static/faces")

                        img_name = name + "_" + emo + "_" + timeStamp + ".jpg"

                        img_path = "static/faces/" + img_name

                        cv.imwrite(img_path, save_img)

                        conn = mysql.connector.connect(
                            user='root',
                            password='',
                            host='localhost',
                            database='1faceemotionmusicchatdashdb'
                        )

                        cursor = conn.cursor()

                        cursor.execute(
                            "INSERT INTO reporttb VALUES('',%s,%s,%s,%s,%s)",
                            (name, date, timeStamp, emo, img_path)
                        )

                        conn.commit()
                        conn.close()

                        cv.waitKey(2)

                        cap.release()

                        cv.destroyAllWindows()

                        for i in range(1, 5):
                            cv.waitKey(1)

                        session['emo'] = emo
                        session['img'] = img_path

                        flash("You Are 😄 " + str(emo))
                        sendmsg(session['mob'], "Your Child is Very Happy")
                        sendmail(img_path,'😄 Keep smiling and stay positive')
                        import HappyMusic
                        return render_template(
                            'FacultyHome.html',
                            emo=session['emo'],
                            img=session['img']
                        )

                # ================= NEUTRAL =================
                if emo == "Neutral":

                    c3 += 1

                    if c3 == 200:

                        import datetime
                        import time
                        import os

                        name = session['fname']

                        ts = time.time()

                        date = datetime.datetime.now().strftime('%d-%b-%Y')
                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H-%M-%S')

                        if not os.path.exists("static/faces"):
                            os.makedirs("static/faces")

                        img_name = name + "_" + emo + "_" + timeStamp + ".jpg"

                        img_path = "static/faces/" + img_name

                        cv.imwrite(img_path, save_img)

                        conn = mysql.connector.connect(
                            user='root',
                            password='',
                            host='localhost',
                            database='1faceemotionmusicchatdashdb'
                        )

                        cursor = conn.cursor()

                        cursor.execute(
                            "INSERT INTO reporttb VALUES('',%s,%s,%s,%s,%s)",
                            (name, date, timeStamp, emo, img_path)
                        )

                        conn.commit()
                        conn.close()

                        cv.waitKey(2)

                        cap.release()

                        cv.destroyAllWindows()

                        for i in range(1, 5):
                            cv.waitKey(1)

                        session['emo'] = emo
                        session['img'] = img_path

                        flash("You Are 😐 " + str(emo))
                        sendmsg(session['mob'], "Your Child is Very Neutral")
                        sendmail(img_path,'😐 Stay calm and have a peaceful day')
                        import NeutralMusic
                        return render_template(
                            'FacultyHome.html',
                            emo=session['emo'],
                            img=session['img']
                        )

                # ================= SAD =================
                if emo == "Sad":

                    c4 += 1

                    if c4 == 200:

                        import datetime
                        import time
                        import os

                        name = session['fname']

                        ts = time.time()

                        date = datetime.datetime.now().strftime('%d-%b-%Y')
                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H-%M-%S')

                        if not os.path.exists("static/faces"):
                            os.makedirs("static/faces")

                        img_name = name + "_" + emo + "_" + timeStamp + ".jpg"

                        img_path = "static/faces/" + img_name

                        cv.imwrite(img_path, save_img)

                        conn = mysql.connector.connect(
                            user='root',
                            password='',
                            host='localhost',
                            database='1faceemotionmusicchatdashdb'
                        )

                        cursor = conn.cursor()

                        cursor.execute(
                            "INSERT INTO reporttb VALUES('',%s,%s,%s,%s,%s)",
                            (name, date, timeStamp, emo, img_path)
                        )

                        conn.commit()
                        conn.close()

                        cv.waitKey(2)

                        cap.release()

                        cv.destroyAllWindows()

                        for i in range(1, 5):
                            cv.waitKey(1)

                        session['emo'] = emo
                        session['img'] = img_path

                        flash("You Are 😢 " + str(emo))
                        sendmsg(session['mob'], "Your Child is Very Sad")
                        sendmail(img_path,"😢 Don't worry, everything will be okay")
                        import SadMusic
                        return render_template(
                            'FacultyHome.html',
                            emo=session['emo'],
                            img=session['img']
                        )

                # ================= SURPRISE =================
                if emo == "Surprise":

                    c5 += 1

                    if c5 == 200:

                        import datetime
                        import time
                        import os

                        name = session['fname']

                        ts = time.time()

                        date = datetime.datetime.now().strftime('%d-%b-%Y')
                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H-%M-%S')

                        if not os.path.exists("static/faces"):
                            os.makedirs("static/faces")

                        img_name = name + "_" + emo + "_" + timeStamp + ".jpg"

                        img_path = "static/faces/" + img_name

                        cv.imwrite(img_path, save_img)

                        conn = mysql.connector.connect(
                            user='root',
                            password='',
                            host='localhost',
                            database='1faceemotionmusicchatdashdb'
                        )

                        cursor = conn.cursor()

                        cursor.execute(
                            "INSERT INTO reporttb VALUES('',%s,%s,%s,%s,%s)",
                            (name, date, timeStamp, emo, img_path)
                        )

                        conn.commit()
                        conn.close()

                        cv.waitKey(2)

                        cap.release()

                        cv.destroyAllWindows()

                        for i in range(1, 5):
                            cv.waitKey(1)

                        session['emo'] = emo
                        session['img'] = img_path

                        flash("You Are 😲 " + str(emo))
                        sendmsg(session['mob'], "Your Child is Very Surprised")
                        sendmail(img_path,"😲 Wow! You look surprised")
                        import SurpriseMusic
                        return render_template(
                            'FacultyHome.html',
                            emo=session['emo'],
                            img=session['img']
                        )

                # ================= SCREEN =================
                cv.imshow('Facial Emotion Recognition', debug_image)

    cap.release()
    cv.destroyAllWindows()

def sendmsg(targetno,message):
    import requests
    requests.post(
        "http://sms.creativepoint.in/api/push.json?apikey=6555c521622c1&route=transsms&sender=FSSMSS&mobileno=" + targetno + "&text=Dear customer your msg is " + message + "  Sent By FSMSG FSSMSS")


def sendmail(image,message):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "projectmailm@gmail.com"
    toaddr =  session['email']

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Face Emotion Detection"

    # string to store the body of the mail
    body = message

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = image
    attachment = open(image, "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "tdyr kebi hnyr yzyh")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()


@app.route("/playsong", methods=['GET', 'POST'])
def playsong():
    if request.method == 'POST':
        emo = session['emo']
        print(emo)

        if emo == "Angry":
            import AngryMusicl

        if emo == "Happy":
            import HappyMusic

        if emo == "Neutral":
            import NeutralMusic

        if emo == "Sad":
            import SadMusic

        if emo == "Surprise":
            import SurpriseMusic

        return render_template('FacultyHome.html', emo=session['emo'])


@app.route("/FacultyHome")
def FacultyHome():
    fac = session['fname']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database=' 1faceemotionmusicchatdashdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb where UserName='"+ fac +"'")
    data = cur.fetchall()
    return render_template('FacultyHome.html', data=data)




@app.route('/AddGames')
def AddGames():
    return render_template('AddGames.html')



@app.route("/newgame", methods=['GET', 'POST'])
def newgame():
    if request.method == 'POST':
        name = request.form['name']
        emo = request.form['emo']
        link = request.form['link']
        des = request.form['des']

        import random
        file = request.files['image']
        fnew = random.randint(1111, 9999)
        savename = str(fnew) + ".png"
        file.save("static/upload/" + savename)

        conn = mysql.connector.connect(user='root', password='', host='localhost', database=' 1faceemotionmusicchatdashdb')
        cursor = conn.cursor()
        cursor.execute(
            "insert into gamestb values('','" + name + "','" + emo + "','" + link + "','" + des + "','" + savename + "')")
        conn.commit()
        conn.close()
        flash("Record Saved!")
        return render_template('AddGames.html')


@app.route("/AGames")
def AGames():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database=' 1faceemotionmusicchatdashdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM gamestb")
    data = cur.fetchall()
    return render_template('AGames.html', data=data)


@app.route("/ARemove")
def ARemove():
    id = request.args.get('id')
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1faceemotionmusicchatdashdb')
    cursor = conn.cursor()
    cursor.execute(
        "delete from gamestb where id='" + id + "'")
    conn.commit()
    conn.close()

    flash('Game info Remove Successfully!')

    return AGames()




@app.route("/UGames")
def UGames():
    emotion = session['emo']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database=' 1faceemotionmusicchatdashdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM gamestb where Emotion='"+ emotion +"'")
    data = cur.fetchall()
    return render_template('UGames.html', data=data)

#=============Dashboard============

@app.route("/Dashboard")
def Dashboard():
    conn = mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='1faceemotionmusicchatdashdb'
    )
    cur = conn.cursor()

    cur.execute("SELECT * FROM regtb")
    data = cur.fetchall()

    cur.execute("SELECT * FROM reporttb")
    data1 = cur.fetchall()

    conn.close()

    return render_template('Dashboard.html', data=data, data1=data1)

#==================================================================================================


@app.route("/UReport")
def UReport():
    import datetime
    fac = session['fname']
    date = datetime.datetime.now()
    date1 = date.strftime('%d-%b-%Y')
    print(date1)
    conn = mysql.connector.connect(user='root', password='', host='localhost', database=' 1faceemotionmusicchatdashdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM reporttb where UserName='"+ fac +"' and Date='"+ date1 +"'")
    data = cur.fetchall()
    return render_template('UReport.html', data=data)


@app.route("/usearch", methods=['GET', 'POST'])
def usearch():

    if request.method == 'POST':

        import datetime

        fac = session['fname']

        # Get date from form
        date = request.form['date']

        # Convert string to date format
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')

        # Convert to MySQL stored format
        date1 = date_obj.strftime('%d-%b-%Y')

        print(date1)

        conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='1faceemotionmusicchatdashdb'
        )

        cur = conn.cursor()

        query = "SELECT * FROM reporttb WHERE UserName=%s AND Date=%s"
        cur.execute(query, (fac, date1))

        data = cur.fetchall()

        return render_template('UReport.html', data=data)

@app.route('/download_pdf')
def download_pdf():

    import mysql.connector
    from fpdf import FPDF
    import os

    conn = mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='1faceemotionmusicchatdashdb'
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM reporttb WHERE UserName='" + session['fname'] + "'")
    data = cur.fetchall()

    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Emotion Information Report", ln=True, align='C')

    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", 'B', 10)

    pdf.cell(35, 15, "Name", 1, 0, 'C')
    pdf.cell(35, 15, "Date", 1, 0, 'C')
    pdf.cell(35, 15, "Time", 1, 0, 'C')
    pdf.cell(35, 15, "Emotion", 1, 0, 'C')
    pdf.cell(50, 15, "Face", 1, 1, 'C')

    pdf.set_font("Arial", '', 10)

    for item in data:

        y_before = pdf.get_y()

        # Text columns
        pdf.cell(35, 40, str(item[1]), 1, 0, 'C')
        pdf.cell(35, 40, str(item[2]), 1, 0, 'C')
        pdf.cell(35, 40, str(item[3]), 1, 0, 'C')
        pdf.cell(35, 40, str(item[4]), 1, 0, 'C')

        # Image cell
        x = pdf.get_x()
        y = pdf.get_y()

        pdf.cell(50, 40, "", 1, 1, 'C')

        # Image path
        img_path = item[5]

        # Remove first slash if needed
        img_path = img_path.replace("\\", "/")

        if os.path.exists(img_path):
            pdf.image(img_path, x + 5, y + 5, 30, 30)

    pdf.output("emotion_report.pdf")
    sendmail2("emotion_report.pdf")

    from flask import send_file
    return send_file("emotion_report.pdf", as_attachment=True)


def sendmail2(image):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "projectmailm@gmail.com"
    toaddr =  session['email']

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Face Emotion Detection"

    # string to store the body of the mail
    body = "Your Reports"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = image
    attachment = open(image, "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "tdyr kebi hnyr yzyh")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()


#=============Dashboard============
@app.route("/UDashboard")
def UDashboard():

    uname = session['fname']

    conn = mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        database='1faceemotionmusicchatdashdb'
    )

    cur = conn.cursor()

    # User Details
    cur.execute("SELECT * FROM regtb WHERE UserName=%s", (uname,))
    data = cur.fetchall()

    # Emotion Reports
    cur.execute("SELECT * FROM reporttb WHERE UserName=%s", (uname,))
    data1 = cur.fetchall()

    conn.close()

    return render_template(
        'UDashboard.html',
        data=data,
        data1=data1
    )


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
