import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor

import librosa
import re 
import numpy as np

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from utils import get_close_matches_rapidfuzz, get_compiled_quran

app = Flask(__name__)
cors = CORS(app)

# Load the Hugging Face model and processor
device = "cuda" if torch.cuda.is_available() else "cpu"
stt_model = WhisperForConditionalGeneration.from_pretrained("./whisper-base-ar-quran").to(device)
processor = WhisperProcessor.from_pretrained("./whisper-base-ar-quran")
print("Model loaded")
# Set the model to evaluation mode
stt_model.eval()

ayat_arr, ayat_info = get_compiled_quran("assets/quran.json")
print("Server ready")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    # Check if the request contains audio data
    print("Received request", request.files)

    if "audio_data" not in request.files:
        print("No audio file found")
        return jsonify({"data": "No audio file found."})

    audio_file = request.files["audio_data"]

    audio_file.save(audio_file.filename)
    
    # Perform transcription
    audio_data, sr = librosa.load(audio_file.filename)
    audio_data = librosa.resample(audio_data, orig_sr = sr, target_sr=16000)
    
    # chunks = librosa.effects.split(audio_data, top_db = 40)
    # print("Chunks", chunks)
    
    # quran_matches = []

    # for chunk in chunks:
    #     segment = audio_data[chunk[0]:chunk[1]]
        
    inputs = processor.feature_extractor(audio_data, return_tensors="pt", sampling_rate=16_000).input_features.to(device)
    predicted_ids = stt_model.generate(inputs, max_length=480_000)
    decoded_ids = processor.tokenizer.batch_decode(predicted_ids)

    tarteel_string = re.sub(r'<[^>]*>', '', decoded_ids[0])
    score, ayat_start, ayat_end = get_close_matches_rapidfuzz(tarteel_string, ayat_arr, ayat_info)
    
    return jsonify({
        "score": score,
        "start": ayat_start,
        "end": ayat_end,
        "string": tarteel_string
    })

if __name__ == "__main__":
    app.run()
