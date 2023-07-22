# Set up

### Install requirements


Download Whisper Tarteel model: 

```
https://huggingface.co/tarteel-ai/whisper-base-ar-quran
```

Download quran.json under assets folder
```
wget https://raw.githubusercontent.com/risan/quran-json/main/dist/quran.json
```

Install NPX: 
```
npm install -g npx
```

Run Flask Server:
```
python3 transcribe_app.py
```

Run HTTP server to avoid CORs issue:
```
npx http-server -p 8000
```

Navigate to ```localhost:8000``` to use the app!

## Todo
* Split up audio into chunks for processing in parallel (every 3 seconds)
    * Add a event / session / recording model to keep track of audio clips and join if necessary
    * On html page, add separate tracks per ayat maybe
* Merge outputs together into a summary of what was recited
* Add UI/UX for easy use
* Set up server
* Change to a word based algorithm, from a passage based algorithm to account for repetitions
* Quantize model 
    https://pytorch.org/tutorials/intermediate/dynamic_quantization_bert_tutorial.html#evaluate-the-inference-accuracy-and-time
    https://huggingface.co/docs/optimum/concept_guides/quantization
* Try out Faster-Whisper (https://github.com/guillaumekln/faster-whisper)
* Word based approach could start using string matching for different roots for bi-grams, tri-grams etc
* Deal with a tree of expanding notes of roots 
* stop recording after certain amount of silence 1 minute or so
* Fix the issue when users repeat a verse that it doesn't 
    * Remove repetitious phrases
* Look into switching to streamlit

## Algorithmic approaches
* Whisper model to transcribe speech to arabic using Tarteel AI
* Once transcript is retrieved, we use rapidfuzz for the string matching
