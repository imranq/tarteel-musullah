import librosa
import soundfile as sf
import re 
import numpy as np
import time
import rapidfuzz
import openai
import os
import json

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)


openai.api_key = os.environ["OPENAI_API_KEY"]
print(openai.api_key)

def get_transcription(audio_fn):
    audio_file= open(audio_fn, "rb")
    transcript = openai.Audio.transcribe('whisper-1', audio_file, language="ar")
    return transcript["text"]
        
quranjson = json.load(open("assets/quran.json", "r", encoding="utf-8"))
ayat_arr = []
ayat_info = []
for surah in quranjson:
    surah_name = surah["transliteration"]
    surah_id = surah["id"]
    for ayat in surah["verses"]:
        ayat_info.append({
            "surah_name": surah_name,
            "surah_id": surah_id,
            "ayat_number": ayat["id"]
        })
        ayat_arr.append(ayat["text"])

quran_all = " ".join(ayat_arr)
print("Server ready")

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
    end_idx = sr*30
    if len(audio_data) > end_idx:
        audio_data = audio_data[:end_idx]
    
    sf.write(audio_fn, audio_data, samplerate=sr)
        
    current_time = time.time()

    # Perform transcription
    tarteel = get_transcription(audio_fn)

    print("Time for AI Transcription", time.time() - current_time)
    current_time = time.time()

    alignment = rapidfuzz.fuzz.partial_ratio_alignment(tarteel, quran_all)

    print("Time for alignment", time.time() - current_time)
    current_time = time.time()

    print(tarteel)
    print(quran_all[alignment.dest_start:alignment.dest_end])

    char_count = 0
    idx = 0
    idxs = []
    while char_count <= alignment.dest_start:
        char_count += len(ayat_arr[idx]) + 1
        idx += 1

    idxs.append(idx-1)
    while char_count <= alignment.dest_end:
        char_count += len(ayat_arr[idx]) + 1
        idx += 1

    idxs.append(idx-1)

    print("Time for ayat counting", time.time() - current_time)
    current_time = time.time()

    selected_ayats = [ayat_info[x] for x in idxs]
    print(selected_ayats)

    return jsonify({
        "score": alignment.score,
        "start": selected_ayats[0],
        "end": selected_ayats[1],
        "string": tarteel
    })

if __name__ == "__main__":
    app.run()
