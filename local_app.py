import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor

import librosa
import soundfile as sf
import re 
import numpy as np
import time
import rapidfuzz
import openai
import os

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin

from utils import get_compiled_quran, perform_alignment_and_counting

app = Flask(__name__)
cors = CORS(app)

# Load the Hugging Face model and processor
device = "cuda" if torch.cuda.is_available() else "cpu"
stt_model = WhisperForConditionalGeneration.from_pretrained("./whisper-base-ar-quran").to(device)
processor = WhisperProcessor.from_pretrained("./whisper-base-ar-quran")
print("Model loaded")
# Set the model to evalion mode
stt_model.eval()


def get_local_transcription(audio_data):
    inputs = processor.feature_extractor(audio_data, return_tensors="pt", sampling_rate=16_000).input_features.to(device)
    predicted_ids = stt_model.generate(inputs, max_length=480_000)
    decoded_ids = processor.tokenizer.batch_decode(predicted_ids)
    tarteel_string = re.sub(r'<[^>]*>', '', decoded_ids[0])
    return tarteel_string
        
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

    audio_file.save(audio_file.filename)
    
    current_time = time.time()

    audio_data, sr = librosa.load(audio_file.filename)
    inputs = processor.feature_extractor(audio_data, return_tensors="pt", sampling_rate=16_000).input_features.to(device)
    
    # Perform transcription
    tarteel_string = get_local_transcription(audio_data)
    
    print("Time for AI Transcription", time.time() - current_time)
    current_time = time.time()

    output = perform_alignment_and_counting(tarteel_string, quran_all, ayat_arr, ayat_info)
    return jsonify(output)


@app.route("/ping-ayat-detect", methods=["GET"])
def ping():
    return "AyatDetect Server"


if __name__ == "__main__":
    app.run()
