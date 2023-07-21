import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor

from difflib import SequenceMatcher
from heapq import nlargest as _nlargest

import librosa
import soundfile as sf
import json
import re 
import numpy as np

from difflib import SequenceMatcher
from heapq import nlargest as _nlargest
import json

def get_close_matches_indexes(word, possibilities, n=3, cutoff=0.6):
    """Use SequenceMatcher to return a list of the indexes of the best 
    "good enough" matches. word is a sequence for which close matches 
    are desired (typically a string).
    possibilities is a list of sequences against which to match word
    (typically a list of strings).
    Optional arg n (default 3) is the maximum number of close matches to
    return.  n must be > 0.
    Optional arg cutoff (default 0.6) is a float in [0, 1].  Possibilities
    that don't score at least that similar to word are ignored.
    """

    if not n >  0:
        raise ValueError("n must be > 0: %r" % (n,))
    if not 0.0 <= cutoff <= 1.0:
        raise ValueError("cutoff must be in [0.0, 1.0]: %r" % (cutoff,))
    result = []
    s = SequenceMatcher()
    s.set_seq2(word)
    for idx, x in enumerate(possibilities):
        s.set_seq1(x)
        if s.real_quick_ratio() >= cutoff and \
           s.quick_ratio() >= cutoff and \
           s.ratio() >= cutoff:
            result.append((s.ratio(), idx))

    # Move the best scorers to head of list
    result = _nlargest(n, result)

    return result

def get_compiled_quran():
    quranjson = json.load(open("assets/quran.json", "r", encoding="utf-8"))
    ayat_arr = []
    ayat_info = []
    for surah in quranjson:
        surah_name = surah["transliteration"]
        for ayat in surah["verses"]:
            ayat_info.append({
                "surah_name": surah_name,
                "ayat_number": ayat["id"],
            })
            ayat_arr.append(ayat["text"])
    return ayat_arr, ayat_info


# Load the Hugging Face model and processor
device = "cuda" if torch.cuda.is_available() else "cpu"
stt_model = WhisperForConditionalGeneration.from_pretrained("./whisper-base-ar-quran").to(device)
processor = WhisperProcessor.from_pretrained("./whisper-base-ar-quran")
print("Model loaded")
# Set the model to evaluation mode
stt_model.eval()
ayat_arr, ayat_info = get_compiled_quran()

audio_file = "Ya-Sin - Test.m4a"

audio_data, sr = librosa.load(audio_file)
audio_data = librosa.resample(audio_data, orig_sr = sr, target_sr=16000)
chunks = librosa.effects.split(audio_data, top_db = 20)
print("Chunks", chunks)

quran_matches = []

for chunk in chunks:
    segment = audio_data[chunk[0]:chunk[1]]
    
    inputs = processor.feature_extractor(segment, return_tensors="pt", sampling_rate=16_000).input_features.to(device)
    predicted_ids = stt_model.generate(inputs, max_length=480_000)
    decoded_ids = processor.tokenizer.batch_decode(predicted_ids)

    tarteel_string = re.sub(r'<[^>]*>', '', decoded_ids[0])
    result = get_close_matches_indexes(tarteel_string, ayat_arr, cutoff=0.0, n=1)
    score, idx = result[0]
    quran_matches.append(ayat_info[idx])
    quran_matches[-1]["score"] = score
    print(ayat_info[idx])
# print(quran_matches)