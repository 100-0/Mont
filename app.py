from flask import Flask, render_template, jsonify, request, session, redirect
import os
import requests
import json
import logging
import random

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# ajax에서 세션 사용을 위한 key
app.secret_key = 'your_secret_key'

client_id = "ktL2HwT47eMq6TspNPlP"
client_secret = "TXUzwIGInL"
# naver 얼굴인식 api
url = "https://openapi.naver.com/v1/vision/face"


def get_emotion_color(emotion):
    colors = {
        'angry': 'red',
        'fear': 'green',
        'neutral': 'black',
        'sad': 'blue',
        'smile': 'orange',
        'laugh': 'orange',
        'talking': 'black',
        'disgust': 'black',
        'surprise': 'black'
    }
    return colors.get(emotion.lower(), '')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        image = request.files['image']
        image_path = os.path.join('static', image.filename)
        image.save(image_path)

        files = {'image': open(image_path, 'rb')}
        headers = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret}
        response = requests.post(url, files=files, headers=headers)
        rescode = response.status_code
        result = {}

        if rescode == 200:
            detect_result = json.loads(response.text)
            detect_summary = detect_result['faces'][0]
            result['image_path'] = image_path
            result['gender'] = detect_summary['gender']['value']
            result['gender_confidence'] = detect_summary['gender']['confidence']
            result['emotion'] = detect_summary['emotion']['value']
            result['emotion_confidence'] = detect_summary['emotion']['confidence']
            result['age'] = detect_summary['age']['value']
            result['age_confidence'] = detect_summary['age']['confidence']

        return render_template('Mont.html', result=result, get_emotion_color=get_emotion_color)

    return render_template('Mont.html', get_emotion_color=get_emotion_color)

# classify.html 페이지 이동
@app.route('/classify', methods=['GET', 'POST'])
def classify():
    return render_template('classify.html')

# result.html 페이지
@app.route('/result', methods=['POST', 'GET'])
def result():
    # POST : genreData와 emotionData 요청 (session으로)
    if request.method == 'POST':
        genreData = request.json['genreData']
        emotionData = request.json['emotionData']
        session['genreData'] = genreData
        session['emotionData'] = emotionData
        return redirect('/result')
    # GET : session으로 받아낸 genreData와 emotionData의 값 가져옴
    elif request.method == 'GET':
        genreData = session.get('genreData')
        emotionData = session.get('emotionData')

        # 이미지 파일 경로 설정 static/color_img/emotionData/genreData
        image_folder = os.path.join('static', 'color_img', emotionData, genreData)
        image_files = os.listdir(image_folder)

        # 랜덤으로 이미지 5개 선택
        # 추천할 이미지가 5개보다 적다면, 그 만큼을 추천해주기
        if len(image_files) > 5:
            random_images = random.sample(image_files, 5)
        else:
            random_images = image_files
        # GET 이라면, result.html에 genreData와 emotionDat와 추천해줄 이미지를 전달
        return render_template('result.html', genreData=genreData, emotionData=emotionData, images=random_images)



if __name__ == '__main__':
    app.run(debug=True)
