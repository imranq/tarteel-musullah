import json


def get_compiled_quran():
    quranjson = json.load(open("/content/quran.json", "r", encoding="utf-8"))
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

ayat_arr, ayat_info = get_compiled_quran()

