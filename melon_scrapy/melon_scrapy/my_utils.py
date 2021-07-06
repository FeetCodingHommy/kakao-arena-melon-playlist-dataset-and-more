import pandas as pd

MELON_JSHREF_REGEX = "javascript:[^\d]+\(\'\d+\',(?P<songId>\d+)\);"
CHARCODE_REGEX = "&#\d+;"

MY_SAVE_POINT_LENGTH = 60 # ※ 카운터 리미트

DATA_DIR = "/content/drive/MyDrive/Colab Notebooks/JOLNON/DATA/multi/"

# 내 노래 데이터프레임
SUCCEEDED = list()
FAILED = list()
SUCCEEDED_DIR   = DATA_DIR+"song_meta_found_DA-12_1.csv"
FAILED_DIR      = DATA_DIR+"song_meta_lost_DA-12_1.csv"
SONG_DF     = pd.read_csv(DATA_DIR+"songs_to_scrap_DA-12_1.csv", encoding="utf-8")

def MY_STRING_CLEANER(some_kakao_arena_title):
    some_kakao_arena_title = some_kakao_arena_title.replace("`", "'")

    match_obj = re.findall(CHARCODE_REGEX, some_kakao_arena_title)

    for charcode in match_obj:
        if charcode[:2] == "&#" and charcode[-1] == ';':
            # "&#000;" --> chr(000)
            some_kakao_arena_title = some_kakao_arena_title.replace(charcode, chr(int(charcode[2:-1])))
    
    return some_kakao_arena_title.strip()