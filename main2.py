import streamlit as st
from datetime import date
import random
import urllib.parse

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="MBTI 오늘의 노래 & 영화",
    page_icon="🎧",
    layout="wide",
)

# -----------------------------
# Pretty CSS
# -----------------------------
st.markdown("""
<style>
.main {background: #fbfbff;}
.block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1100px;}
.hero {
  background: linear-gradient(135deg, #e8f3ff 0%, #f6ecff 45%, #fff1f2 100%);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 18px 18px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.06);
}
.hero-title {font-size: 1.7rem; font-weight: 900; margin: 0;}
.hero-desc {color: #374151; margin: 6px 0 0 0; font-size: 1rem;}
.card {
  background: white;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow:: 0 10px 24px rgba(0,0,0,0.05);
  height: 100%;
}
.badge {
  display:inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.85rem;
  border: 1px solid rgba(0,0,0,0.08);
  background: rgba(99,102,241,0.10);
  color: #3730a3;
  margin-right: 6px;
}
.badge2 {
  display:inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.85rem;
  border: 1px solid rgba(0,0,0,0.08);
  background: rgba(16,185,129,0.12);
  color: #065f46;
}
.big {font-size: 1.15rem; font-weight: 900;}
.muted {color: #6b7280;}
.hr {margin: 14px 0; border-top: 1px solid rgba(0,0,0,0.07);}
.stButton>button {border-radius: 12px; padding: 0.55rem 0.95rem; font-weight: 800;}
a {text-decoration: none;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Data
# NOTE: 저작권 문제 없는 수준(제목/아티스트/영화명만)
# -----------------------------
SONGS_BY_TEMPERAMENT = {
    "NF": [  # ENFP INFP ENFJ INFJ
        {"title": "Spring Day", "artist": "BTS", "mood": "🌸 따뜻/회상"},
        {"title": "Love Poem", "artist": "IU", "mood": "💗 위로"},
        {"title": "Fix You", "artist": "Coldplay", "mood": "🫶 회복"},
        {"title": "Holocene", "artist": "Bon Iver", "mood": "🌌 감성"},
        {"title": "About You", "artist": "The 1975", "mood": "✨ 몽글"},
        {"title": "Somewhere Only We Know", "artist": "Keane", "mood": "🌿 서정"},
    ],
    "NT": [  # ENTP INTP ENTJ INTJ
        {"title": "Time", "artist": "Hans Zimmer", "mood": "🧠 몰입"},
        {"title": "Harder, Better, Faster, Stronger", "artist": "Daft Punk", "mood": "⚙️ 생산성"},
        {"title": "Black Skinhead", "artist": "Kanye West", "mood": "🔥 추진력"},
        {"title": "Nights", "artist": "Frank Ocean", "mood": "🌗 전환/사고"},
        {"title": "Take Five", "artist": "Dave Brubeck", "mood": "🧩 리듬/구조"},
        {"title": "Midnight City", "artist": "M83", "mood": "🌃 집중/확장"},
    ],
    "SJ": [  # ESTJ ISTJ ESFJ ISFJ
        {"title": "Here Comes the Sun", "artist": "The Beatles", "mood": "☀️ 안정"},
        {"title": "Count on Me", "artist": "Bruno Mars", "mood": "🤝 신뢰"},
        {"title": "Dynamite", "artist": "BTS", "mood": "🕺 기분전환"},
        {"title": "Happy", "artist": "Pharrell Williams", "mood": "😄 리프레시"},
        {"title": "Good Day", "artist": "IU", "mood": "🌈 밝음"},
        {"title": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "mood": "💥 에너지"},
    ],
    "SP": [  # ESTP ISTP ESFP ISFP
        {"title": "Levitating", "artist": "Dua Lipa", "mood": "🪩 텐션"},
        {"title": "Blinding Lights", "artist": "The Weeknd", "mood": "🚦 드라이브"},
        {"title": "HUMBLE.", "artist": "Kendrick Lamar", "mood": "⚡ 임팩트"},
        {"title": "Shut Up and Dance", "artist": "WALK THE MOON", "mood": "🎉 파티"},
        {"title": "Bang Bang Bang", "artist": "BIGBANG", "mood": "🥁 쾌감"},
        {"title": "Don’t Start Now", "artist": "Dua Lipa", "mood": "💃 즉흥"},
    ],
}

MOVIES_BY_TEMPERAMENT = {
    "NF": [
        {"title": "About Time", "year": "2013", "genre": "💞 로맨스/인생"},
        {"title": "Little Women", "year": "2019", "genre": "🌷 성장/가족"},
        {"title": "Her", "year": "2013", "genre": "🤖 감성 SF"},
        {"title": "The Secret Life of Walter Mitty", "year": "2013", "genre": "🗺️ 힐링/여행"},
        {"title": "Inside Out", "year": "2015", "genre": "🧠 감정/애니"},
        {"title": "La La Land", "year": "2016", "genre": "🎹 뮤지컬"},
    ],
    "NT": [
        {"title": "Interstellar", "year": "2014", "genre": "🚀 SF"},
        {"title": "The Imitation Game", "year": "2014", "genre": "🧩 전기/추리"},
        {"title": "Inception", "year": "2010", "genre": "🌀 SF/스릴러"},
        {"title": "The Social Network", "year": "2010", "genre": "💻 드라마"},
        {"title": "Arrival", "year": "2016", "genre": "🛰️ 언어/사고"},
        {"title": "Moneyball", "year": "2011", "genre": "📊 전략"},
    ],
    "SJ": [
        {"title": "The Intern", "year": "2015", "genre": "👔 일상/힐링"},
        {"title": "Hidden Figures", "year": "2016", "genre": "🧮 실화"},
        {"title": "The Martian", "year": "2015", "genre": "🛠️ 문제해결"},
        {"title": "Wonder", "year": "2017", "genre": "💛 가족"},
        {"title": "The Pursuit of Happyness", "year": "2006", "genre": "🎯 동기부여"},
        {"title": "Paddington 2", "year": "2017", "genre": "🧸 따뜻"},
    ],
    "SP": [
        {"title": "Baby Driver", "year": "2017", "genre": "🏎️ 액션"},
        {"title": "Top Gun: Maverick", "year": "2022", "genre": "✈️ 액션"},
        {"title": "Spider-Man: Into the Spider-Verse", "year": "2018", "genre": "🕷️ 애니/액션"},
        {"title": "The Greatest Showman", "year": "2017", "genre": "🎪 뮤지컬"},
        {"title": "Mad Max: Fury Road", "year": "2015", "genre": "🔥 액션"},
        {"title": "Guardians of the Galaxy", "year": "2014", "genre": "🌌 오락"},
    ],
}

# MBTI → temperament (기질) 매핑
def temperament(mbti: str) -> str:
    mbti = mbti.upper().strip()
    # 2,3 글자로 기질 분류: N/S + F/T
    if len(mbti) != 4:
        return "NF"
    n_or_s = mbti[1]
    f_or_t = mbti[2]
    if n_or_s == "N" and f_or_t == "F":
        return "NF"
    if n_or_s == "N" and f_or_t == "T":
        return "NT"
    if n_or_s == "S" and f_or_t == "J":
        # 엄밀히는 SJ는 S + J 조합이지만, MBTI엔 3번째가 J/P가 아니라 T/F라서
        # 기존의 4기질 분류(SJ/SP/NF/NT)는 보통 2~4번째 조합으로 합니다.
        # 여기서는 "S + (마지막이 J)" 를 SJ로 분류
        pass
    # 4기질은 보통:
    # SJ: _S_TJ / _S_FJ / IS_TJ / IS_FJ (즉 2번째 S + 4번째 J)
    # SP: 2번째 S + 4번째 P
    # NF: 2번째 N + 3번째 F
    # NT: 2번째 N + 3번째 T
    last = mbti[3]
    if mbti[1] == "S" and last == "J":
        return "SJ"
    if mbti[1] == "S" and last == "P":
        return "SP"
    if mbti[1] == "N" and mbti[2] == "F":
        return "NF"
    if mbti[1] == "N" and mbti[2] == "T":
        return "NT"
    return "NF"

def link_spotify_search(query: str) -> str:
    return "https://open.spotify.com/search/" + urllib.parse.quote(query)

def link_youtube_search(query: str) -> str:
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)

def link_imdb_search(query: str) -> str:
    return "https://www.imdb.com/find/?q=" + urllib.parse.quote(query)

def daily_rng(mbti: str, extra_seed: int = 0) -> random.Random:
    # 같은 날짜 + 같은 MBTI면 결과가 고정되도록 seed 생성
    today = date.today().isoformat()
    seed_str = f"{today}-{mbti.upper()}-{extra_seed}"
    seed = abs(hash(seed_str)) % (2**32)
    return random.Random(seed)

# -----------------------------
# UI: Hero
# -----------------------------
st.markdown("""
<div class="hero">
  <p class="hero-title">🎧 MBTI 오늘의 노래 & 🎬 오늘의 영화</p>
  <p class="hero-desc">MBTI를 고르면, 오늘 분위기에 맞춰 한 곡 + 한 편을 추천해줘요 ✨ (매일 바뀜)</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🧩 설정")
mbti_list = [
    "ISTJ","ISFJ","INFJ","INTJ",
    "ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP",
    "ESTJ","ESFJ","ENFJ","ENTJ",
]
mbti = st.sidebar.selectbox("내 MBTI는?", mbti_list, index=10)  # 기본 ENFP
show_reason = st.sidebar.toggle("🔍 추천 이유도 보기", value=True)
extra_roll = st.sidebar.number_input("🎲 다시 뽑기(숫자 올리면 다른 추천)", min_value=0, max_value=999, value=0, step=1)

temp = temperament(mbti)
temp_label = {"NF":"🌷 NF(공감·감성)", "NT":"🧠 NT(사고·전략)", "SJ":"🧱 SJ(안정·책임)", "SP":"⚡ SP(즉흥·경험)"}[temp]
st.sidebar.markdown(f"**기질 분류:** {temp_label}")
st.sidebar.caption("같은 날엔 같은 번호(extra_roll)에서 추천이 고정돼요 🙂")

# -----------------------------
# Recommend
# -----------------------------
rng = daily_rng(mbti, extra_seed=extra_roll)

song = rng.choice(SONGS_BY_TEMPERAMENT[temp])
movie = rng.choice(MOVIES_BY_TEMPERAMENT[temp])

# Top badges
st.markdown(f"<span class='badge'>#{mbti}</span> <span class='badge2'>{temp_label}</span>", unsafe_allow_html=True)
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🎧 오늘의 노래")
    st.markdown(f"<div class='big'>🎵 {song['title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='muted'>👤 {song['artist']} · {song['mood']}</div>", unsafe_allow_html=True)

    q_song = f"{song['title']} {song['artist']}"
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("🔎 Spotify에서 찾기", link_spotify_search(q_song))
    with c2:
        st.link_button("▶️ YouTube에서 듣기", link_youtube_search(q_song))

    if show_reason:
        st.write("")
        st.markdown("**💡 오늘의 추천 포인트**")
        if temp == "NF":
            st.write("- 감정 정리/위로/서정적인 멜로디에 잘 반응하는 편 → 오늘은 마음을 부드럽게 정돈하는 곡")
        elif temp == "NT":
            st.write("- 사고 흐름을 깨우는 구조/리듬/확장감이 중요 → 집중·몰입에 도움 되는 곡")
        elif temp == "SJ":
            st.write("- 안정감·긍정·일상 회복에 강점 → 오늘 하루를 ‘정상궤도’로 돌려주는 곡")
        else:
            st.write("- 즉흥·에너지·몸이 반응하는 템포 선호 → 기분 끌어올리는 곡")

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🎬 오늘의 영화")
    st.markdown(f"<div class='big'>🍿 {movie['title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='muted'>📅 {movie['year']} · {movie['genre']}</div>", unsafe_allow_html=True)

    q_movie = f"{movie['title']} {movie['year']}"
    st.write("")
    st.link_button("🔎 IMDB에서 찾아보기", link_imdb_search(q_movie))

    if show_reason:
        st.write("")
        st.markdown("**💡 오늘의 추천 포인트**")
        if temp == "NF":
            st.write("- 관계/감정선이 살아있는 이야기에서 큰 만족 → ‘여운’ 남는 영화")
        elif temp == "NT":
            st.write("- 아이디어/구조/문제해결/큰 질문에 끌림 → 생각할 거리 있는 영화")
        elif temp == "SJ":
            st.write("- 따뜻한 메시지 + 현실적인 성장/성취 → 마음이 안정되는 영화")
        else:
            st.write("- 속도감/재미/비주얼/음악이 중요 → 한 편으로 텐션 채우는 영화")

    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# -----------------------------
# Optional: "Today's playlist" list
# -----------------------------
with st.expander("📌 같은 기질(temperament) 추천 후보 더 보기"):
    cols = st.columns(2)
    with cols[0]:
        st.markdown("#### 🎧 노래 후보")
        for s in SONGS_BY_TEMPERAMENT[temp]:
            st.write(f"- 🎵 {s['title']} — {s['artist']} ({s['mood']})")
    with cols[1]:
        st.markdown("#### 🎬 영화 후보")
        for m in MOVIES_BY_TEMPERAMENT[temp]:
            st.write(f"- 🍿 {m['title']} ({m['year']}) · {m['genre']}")

st.caption("※ 추천은 ‘분위기 기반’ 샘플입니다. 학교/동아리/프로젝트용이면 장르·국내작·최신작 리스트로 더 풍성하게 커스터마이징 가능!")
