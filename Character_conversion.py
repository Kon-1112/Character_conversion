import numpy as np
import sounddevice as sd
import wave
import speech_recognition as sr
from flask import Flask,render_template,request

app = Flask(__name__)

def recode(time):
    FILE_NAME = './recode.wav'
    sample_rate = 16_000  
    #録音開始（time秒間録音waitで録音し終わるまで待つ）
    data = sd.rec(int(time * sample_rate), sample_rate, channels=1)
    sd.wait()
    #量子化ビット16bitで録音するのでint16の範囲で最大化する
    data = data / data.max() * np.iinfo(np.int16).max
    # float -> int
    data = data.astype(np.int16)
    # ファイル保存
    with wave.open(FILE_NAME, mode='wb') as wb:
        wb.setnchannels(1)
        # 16bit=2byte
        wb.setsampwidth(2)
        wb.setframerate(sample_rate)
        # バイト列に変換
        wb.writeframes(data.tobytes())

def recogntiton(file_name):
    try:
        r = sr.Recognizer()
        with sr.AudioFile(f"{file_name}.wav") as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language='ja-JP')
    except:
        text="文字を判別できませんでした。"
    return text

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/recoded',methods=["POST"])
def recoded():
    timer = int(request.form['time'])
    recode(timer)
    print("録音完了")
    msg = f"{timer}秒の録音が完了しました。"
    return render_template('index.html',msg=msg)

@app.route('/upload',methods=["POST"])
def upload():
    if 'file' not in request.files:
        return 'ファイル未指定'
    fs = request.files['file']
    app.logger.info('file_name={}'.format(fs.filename))
    app.logger.info('content_type={} content_length={}, mimetype={}, mimetype_params={}'.format(
        fs.content_type, fs.content_length, fs.mimetype, fs.mimetype_params))
    fs.save('recode.wav')

    return "フィアルアップロード成功<br><a href='/'>戻る</a>"


@app.route('/change',methods=['POST'])
def change():
    text = recogntiton('recode')
    return render_template('index.html', voice_text=text)

    
if __name__=="__main__":
    app.run(debug=True,port=8888)