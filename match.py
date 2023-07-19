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

    # Strip scores for the best n matches
    return result

def get_compiled_quran():
    quranjson = json.load(open("quran.json", "r", encoding="utf-8"))
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





if __name__ == '__main__':
    string_tarteel = "وَالسَّمَاءِ ذَاتِ الْبُرُوشِ وَالْيَوْمِ الْمَغُودِ"
    ayat_arr, ayat_info = get_compiled_quran()
    results = get_close_matches_indexes(string_tarteel, ayat_arr, cutoff=0.5)
    score, idx = results[0]
    print(string_tarteel)
    print(ayat_arr[idx], ayat_info[idx], score, idx)