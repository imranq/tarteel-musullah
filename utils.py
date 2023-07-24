import json
import rapidfuzz
import os
import time

def perform_alignment_and_counting(tarteel_string, quran_all, ayat_arr, ayat_info):
    # Perform alignment
    current_time = time.time()
    alignment = rapidfuzz.fuzz.partial_ratio_alignment(tarteel_string, quran_all)

    print("Time for alignment", time.time() - current_time)
    current_time = time.time()

    # Perform ayat counting
    char_count = 0
    idx = 0
    idxs = []

    while char_count <= alignment.dest_start:
        char_count += len(ayat_arr[idx]) + 1
        idx += 1

    # get the first ayat
    idxs.append(idx-1)

    while char_count <= alignment.dest_end:
        char_count += len(ayat_arr[idx]) + 1
        idx += 1

    # get the last ayat
    idxs.append(idx-1)

    print("Time for ayat counting", time.time() - current_time)
    current_time = time.time()

    # Perform compiling Results
    selected_ayats = [ayat_info[x] for x in idxs]
    quran_portion = quran_all[alignment.dest_start:alignment.dest_end]
    ayat_portion = ". ".join(ayat_arr[idxs[0]:(idxs[1]+1)])
    translation_portion = ". ".join([ayat_info[x]["translation"] for x in range(idxs[0], idxs[1]+1)])
    portion_idxs = rapidfuzz.fuzz.partial_ratio_alignment(tarteel_string, ayat_portion)

    print(tarteel_string)
    print(quran_portion)
    print(selected_ayats)
    # sf.write(f'data/{selected_ayats[0]["surah_name"]}_{selected_ayats[0]["ayat_number"]}.mp3', audio_data, 16000, format="mp3")

    output = {
        "score": alignment.score,
        "start": selected_ayats[0],
        "end": selected_ayats[1],
        "transcribed_portion": tarteel_string,
        "ayat_portion": ayat_portion,
        "quran_portion_idx_start": portion_idxs.dest_start,
        "quran_portion_idx_end": portion_idxs.dest_end,
        "translation_portion": translation_portion
    }

    return output

def get_compiled_quran(folder_loc):
    quranjson = json.load(open(os.path.join(folder_loc, "quran.json"), "r", encoding="utf-8"))
    en_translation = json.load(open(os.path.join(folder_loc, "khattab_quran_translation.json"), "r", encoding="utf-8"))
    ayat_arr = []
    ayat_info = []
    for surah in quranjson:
        surah_name = surah["transliteration"]
        surah_id = surah["id"]
        for ayat in surah["verses"]:
            ayat_info.append({
                "surah_name": surah_name,
                "surah_id": surah_id,
                "ayat_number": ayat["id"],
                "translation": en_translation[surah_id-1]["translation"][ayat["id"]-1][1]
            })
            ayat_arr.append(ayat["text"])
    return ayat_arr, ayat_info


    