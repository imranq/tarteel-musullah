import librosa
import soundfile as sf
import re 
import numpy as np
import time
import rapidfuzz
import openai
import os
import json
from utils import get_compiled_quran, perform_alignment_and_counting
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)


openai.api_key = os.environ["OPENAI_API_KEY"]
print(openai.api_key)

def get_transcription_openai(audio_fn):
    audio_file= open(audio_fn, "rb")
    transcript = openai.Audio.transcribe('whisper-1', audio_file, language="ar")
    return transcript["text"]
        
ayat_arr, ayat_info = get_compiled_quran("assets")
quran_all = " ".join(ayat_arr)
print("Server ready")


@app.route("/", methods=["GET"])
def home():
    return send_file('index.html')


@app.route("/transcribe", methods=["POST"])
def transcribe():
    # Check if the request contains audio data
    print("Received request", request.files)

    if "audio_data" not in request.files:
        print("No audio file found")
        return jsonify({"data": "No audio file found."})

    audio_file = request.files["audio_data"]
    audio_fn = "blob.wav"

    audio_file.save(audio_fn)
    audio_data, sr = librosa.load(audio_fn)
    audio_data, index = librosa.effects.trim(audio_data)

    # get first 30 seconds
    # end_idx = sr*30
    # if len(audio_data) > end_idx:
    #     audio_data = audio_data[:end_idx]
    
    sf.write(audio_fn, audio_data, samplerate=sr)
        
    # Perform transcription
    current_time = time.time()
    tarteel_string = get_transcription_openai(audio_fn)
    print("Time for AI Transcription", time.time() - current_time)
    
    output = perform_alignment_and_counting(tarteel_string, quran_all, ayat_arr, ayat_info)

    return jsonify(output)

@app.route("/ping-ayat-detect", methods=["GET"])
def ping():
    return "AyatDetect Server"

if __name__ == "__main__":
    app.run()
