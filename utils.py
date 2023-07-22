from cdifflib import CSequenceMatcher
import json
import rapidfuzz


def get_close_matches_rapidfuzz(phrase, ayat_arr, ayat_info):
    result = []
    corpus =  " ".join(ayat_arr)
    current_ayat = 0
    char_count = 0
    current_ratio = 0

    for x in range(len(corpus)-len(phrase)):
        test_phrase = corpus[x: x+len(phrase)]

        if x > char_count + len(ayat_arr[current_ayat]):
            current_ayat += 1
            char_count = x

        temp_ratio = rapidfuzz.fuzz.ratio(test_phrase, phrase)
                
        if current_ratio < temp_ratio:
            result.append((temp_ratio, current_ayat))
            current_ratio = temp_ratio
            print(current_ratio, ayat_info[current_ayat])

    score, idx = result[-1]
    
    end_idx = idx-1
    target_char_count = char_count + len(phrase)
    char_x = char_count

    while char_x < target_char_count:
        char_x += len(ayat_arr[end_idx])
        end_idx += 1
        

    return score, ayat_info[idx], ayat_info[end_idx]


def get_close_matches_cseq(phrase, ayat_arr, ayat_info):
    result = []
    s = CSequenceMatcher()
    s.set_seq2(phrase)
    corpus =  " ".join(ayat_arr)
    current_ayat = 0
    char_count = 0
    current_ratio = 0
    for x in range(len(corpus)-len(phrase)):
        test_phrase = corpus[x: x+len(phrase)]
        s.set_seq1(test_phrase)

        if x > char_count + len(ayat_arr[current_ayat]):
            current_ayat += 1
            char_count = x
        
        temp_ratio = s.ratio()
        if current_ratio < temp_ratio:
            result.append((temp_ratio, current_ayat))
            current_ratio = temp_ratio
            print(current_ratio, ayat_info[current_ayat])

    score, idx = result[-1]
    
    end_idx = idx-1
    target_char_count = char_count + len(phrase)
    char_x = char_count

    while char_x < target_char_count:
        char_x += len(ayat_arr[end_idx])
        end_idx += 1
        

    return score, ayat_info[idx], ayat_info[end_idx]

def get_compiled_quran(quran_fn):
    quranjson = json.load(open(quran_fn, "r", encoding="utf-8"))
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
    return ayat_arr, ayat_info


    