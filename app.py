from flask import Flask, render_template, request
import os
import requests
import json
import logging


app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

client_id = "ktL2HwT47eMq6TspNPlP"
client_secret = "TXUzwIGInL"
url = "https://openapi.naver.com/v1/vision/face"


def get_emotion_color(emotion):
    colors = {
        'angry': 'red',
        'fear': 'green',
        'neutral': 'black',
        'sad': 'blue',
        'smile': 'orange',
        'laugh': 'orange'
    }
    other_color = 'gray'  # 기타 감정에 대한 색상
    if emotion.lower() in colors:
        return colors[emotion.lower()]
    else:
        return other_color


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

@app.route('/classify', methods=['POST'])
def classify():
    return render_template('classify.html')


if __name__ == '__main__':
    app.run(debug=True)
