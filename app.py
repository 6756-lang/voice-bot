from flask import Flask, request, render_template, jsonify
import openai
from gtts import gTTS
import os
import speech_recognition as sr

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    if "audio" not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400

    audio_file = request.files["audio"]
    audio_path = "temp.wav"
    audio_file.save(audio_path)

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            user_text = recognizer.recognize_google(audio_data)
        except:
            return jsonify({"error": "Speech not recognized"}), 400

    system_prompt = "You are ChatGPT. Speak as yourself—thoughtful, grounded, honest. Be helpful and warm, with clear language."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    )
    bot_reply = response.choices[0].message.content.strip()

    tts = gTTS(bot_reply)
    tts.save("static/response.mp3")

    return jsonify({
        "user_text": user_text,
        "bot_reply": bot_reply,
        "audio_url": "/static/response.mp3"
    })

if __name__ == "__main__":
    app.run(debug=True)