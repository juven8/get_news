# ニュースの取得
import requests
import os

def fetch_news():
    API_KEY = os.getenv('NEWS_API_KEY')
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "Japan economy OR Japan technology OR Japan business", 
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 30,
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)
    articles = response.json().get("articles", [])
    return articles

#from transformers import MarianMTModel, MarianTokenizer

#tokenizer = MarianTokenizer.from_pretrained("staka/fugumt-en-ja")
#model = MarianMTModel.from_pretrained("staka/fugumt-en-ja")

# 翻訳関数
#def translate(text):
#    inputs = tokenizer(text, return_tensors="pt", padding=True)
#    output = model.generate(**inputs)
#    return tokenizer.decode(output[0], skip_special_tokens=True)

import uuid
import json

AZURE_KEY = os.getenv('AZURE_TRANSLATOR_API_KEY')
AZURE_ENDPOINT = "https://api.cognitive.microsofttranslator.com/"
AZURE_LOCATION = "JapanEast"

def translate_text(texts):
    path = '/translate'
    constructed_url = AZURE_ENDPOINT + path
    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': ['ja']
    }
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_KEY,
        'Ocp-Apim-Subscription-Region': AZURE_LOCATION,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    body = [{'text': texts}]
    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()
    return response[0]['translations'][0]['text']

# 英語の音声合成
import pyttsx3
def speak_en(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


# VOICEVOXで日本語の音声合成
from pydub import AudioSegment
from pydub.playback import play

def speak_ja(text, speaker=2, filename="./voice.wav"):
    # 音声クエリ生成
    query = requests.post(
    "http://localhost:50021/audio_query",
    params={"text": text, "speaker": speaker}
    )

    if query.status_code != 200:
        print("audio_query に失敗:", query.text)


    # synthesis に JSON形式で送信
    audio = requests.post(
        "http://localhost:50021/synthesis",
        params={"speaker": speaker},
        headers={"Content-Type": "application/json"},
        data=json.dumps(query.json())  # ← 明示的にJSON文字列に変換
    )

    # 音声保存（raw形式）
    with open(filename, "wb") as f:
        f.write(audio.content)

    # 保存成功の確認
    if not os.path.exists(filename):
        print("音声ファイルが保存されていません")
    else:
        # pydubで読み込んで再生（Windows環境でも安定）
        sound = AudioSegment.from_file(filename, format="wav")
        play(sound)


# ストリームリットで表示
import streamlit as st
#from streamlit_autorefresh import st_autorefresh
import time

news_list = fetch_news()
start_time = time.strftime('%Y年%m月%d日 %H:%M:%S', time.localtime())
#news_cnt = len(news_list)
index = 0


st.title("🗞 ニュース翻訳＆読み上げステーション")
st.write(start_time)

# セッションステートで表示インデックスを管理
if "index" not in st.session_state:
    st.session_state.index = 0

key = st.text_input("キーボード操作（n: 次、p: 前）", "")

if key.lower() == "n" and st.session_state.index < len(news_list) - 1:
    st.session_state.index += 1
elif key.lower() == "p" and st.session_state.index > 0:
    st.session_state.index -= 1


# スライドコントロール
#col1, col2, col3 = st.columns([1, 6, 1])
#with col1:
#    if st.button("◀ 前") and st.session_state.index > 0:
#        st.session_state.index -= 1

#with col3:
#    if st.button("次 ▶") and st.session_state.index < len(news_list) - 1:
#        st.session_state.index += 1

# 中央に表示（翻訳付き）
article = news_list[st.session_state.index]
english = f"{article['title']}\n\n{article['description']}"
japanese = translate_text(english)
#with col2:
st.subheader(st.session_state.index + 1)
st.subheader("📰 英語原文")
st.write(english)
st.subheader("🌐 日本語訳")
st.write(japanese)    
# 読み上げ
speak_en(english)
speak_ja(japanese) 