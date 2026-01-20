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
        {"title": "Moneyball", "year": "2011", "genre"
