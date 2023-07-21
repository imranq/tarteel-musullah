# Set up

### Install requirements


Download Whisper Tarteel model: 

```
https://huggingface.co/tarteel-ai/whisper-base-ar-quran
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
* Split up audio into chunks for processing
* Merge outputs together into a summary of what was recited
* Add UI/UX for easy use
* Set up server
* Change to a word based algorithm, from a passage based algorithm to account for repetitions


## Algorithmic approaches
* Once transcript is retrieved, we use rapidfuzz for the string matching
* Word based approach could start using string matching for different roots for bi-grams, tri-grams etc