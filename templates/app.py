from flask import Flask, request, render_template, jsonify
import openai
from gtts import gTTS
import os
import speech_recognition as sr
from pydub import AudioSegment

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    if "audio" not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400

    # Save the uploaded (webm) file
    audio_file = request.files["audio"]
    input_path = "temp_input.webm"
    audio_file.save(input_path)

    # Convert to proper WAV using pydub + ffmpeg
    converted_path = "converted.wav"
    try:
        audio = AudioSegment.from_file(input_path)
        audio.export(converted_path, format="wav")
    except Exception as e:
        return jsonify({"error": f"Audio conversion failed: {str(e)}"}), 500

    # Speech recognition
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(converted_path) as source:
            audio_data = recognizer.record(source)
            user_text = recognizer.recognize_google(audio_data)
    except Exception as e:
        return jsonify({"error": f"Speech recognition failed: {str(e)}"}), 500

    # Get ChatGPT response
    system_prompt = "You are ChatGPT. Speak as yourself—thoughtful, grounded, honest. Be helpful and warm, with clear language."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    )
    bot_reply = response.choices[0].message.content.strip()

    # Generate audio response
    tts = gTTS(bot_reply)
    tts.save("static/response.mp3")

    return jsonify({
        "user_text": user_text,
        "bot_reply": bot_reply,
        "audio_url": "/static/response.mp3"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)