import streamlit as st
import pandas as pd
from datetime import datetime
import json, os

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="간호학과 진로탐색",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CSS (예쁘게)
# -----------------------------
st.markdown("""
<style>
/* 전체 폰트/배경 */
.main {background: #fbfbff;}
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}

/* 타이틀/서브타이틀 */
.h1 {font-size: 2.1rem; font-weight: 800; letter-spacing: -0.5px;}
.subtle {color: #6b7280; font-size: 0.98rem;}

/* 히어로 배너 */
.hero {
  background: linear-gradient(135deg, #e8f3ff 0%, #f6ecff 45%, #fff1f2 100%);
  border: 1px solid rgba(0,0,0,0.05);
  border-radius: 18px;
  padding: 18px 18px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.05);
}
.hero-title {font-size: 1.6rem; font-weight: 800; margin: 0;}
.hero-desc {color: #374151; margin: 6px 0 0 0; font-size: 1rem;}

/* KPI 카드 */
.kpi {
  background: white;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 16px;
  padding: 14px 14px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}
.kpi .label {color:#6b7280; font-size:0.9rem;}
.kpi .value {font-size:1.35rem; font-weight:800; margin-top:2px;}

/* 진로 카드 */
.card {
  background: white;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 14px 14px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.045);
  height: 100%;
}
.badge {
  display:inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  border: 1px solid rgba(0,0,0,0.06);
  background: rgba(99,102,241,0.08);
  color: #3730a3;
  margin-right: 6px;
}
.badge2 {
  display:inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  border: 1px solid rgba(0,0,0,0.06);
  background: rgba(16,185,129,0.10);
  color: #065f46;
}

/* 구분선 */
.hr {margin: 12px 0; border-top: 1px solid rgba(0,0,0,0.06);}

/* 작은 태그 */
.tag {
  display:inline-block;
  margin: 3px 6px 0 0;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(0,0,0,0.04);
  font-size: 0.85rem;
}

/* Streamlit 기본 버튼 살짝 둥글게 */
.stButton>button {
  border-radius: 12px;
  padding: 0.55rem 0.9rem;
  font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Data
# -----------------------------
CAREERS = [
    {
        "emoji": "🏥",
        "직무": "임상간호사(병동/특수부서)",
        "분야": "임상",
        "근무환경": "병원",
        "추천성향": ["사람 중심", "현장 역동", "팀워크"],
        "핵심역량": ["의사소통", "임상추론", "우선순위 판단", "스트레스 관리"],
        "추천경험": ["실습 케이스 스터디", "시뮬레이션 참여", "BLS/ACLS 관심 갖기"],
        "로드맵": [
            "학부: 기본·성인·아동·모성·정신 실습을 ‘내 언어’로 정리",
            "졸업 후: 신규교육/프리셉터십에서 기본기 탄탄히",
            "1~3년: 관심부서(ER/ICU 등) 탐색 + 임상역량 강화",
            "3년+: 교육/리더/QI/전문분야로 확장"
        ],
        "관련자격": ["BLS", "ACLS(선택)"],
        "한줄": "환자 곁에서 가장 가까이 돌보는 핵심 역할"
    },
    {
        "emoji": "🚑",
        "직무": "응급간호(응급실/트리아지)",
        "분야": "임상",
        "근무환경": "응급실",
        "추천성향": ["속도감", "판단력", "긴장 상황 대처"],
        "핵심역량": ["ABCDE 평가", "트리아지", "팀 커뮤니케이션", "우선순위 판단"],
        "추천경험": ["응급 시뮬레이션", "BLS/ACLS 학습", "트리아지 사례 읽기"],
        "로드맵": [
            "학부: 응급/중환자 핵심개념(ABCDE, 쇼크 등) 정리",
            "졸업 후: ER 신규교육 + 프로토콜 숙지",
            "1~3년: 트리아지 숙련 + 소생팀 경험",
            "3년+: 코디네이터/교육/QI 역할 확장"
        ],
        "관련자격": ["BLS", "ACLS", "PALS(선택)"],
        "한줄": "급성기 환자를 빠르게 분류·안정화하는 최전선"
    },
    {
        "emoji": "🫁",
        "직무": "중환자실(ICU) 간호",
        "분야": "임상",
        "근무환경": "중환자실",
        "추천성향": ["정밀함", "깊이 있는 학습", "기술 친화"],
        "핵심역량": ["중환자 모니터링", "약물/수액", "기기관리", "감염관리"],
        "추천경험": ["ABGA/환기 기초", "QI 프로젝트", "중환자 케이스 스터디"],
        "로드맵": [
            "학부: 병태생리+약리 핵심을 ‘케이스’로 연결",
            "졸업 후: ICU 신규교육 + 장비/프로토콜 습득",
            "1~3년: 고난도 케이스 경험 + 인증 과정 참여",
            "3년+: 전문간호/연구/QI로 확장"
        ],
        "관련자격": ["BLS", "ACLS(권장)"],
        "한줄": "중증 환자 생명유지 치료를 정교하게 관리"
    },
    {
        "emoji": "🏘️",
        "직무": "보건소/지역사회 간호",
        "분야": "지역사회",
        "근무환경": "공공/지역",
        "추천성향": ["예방 중심", "교육", "장기 관점"],
        "핵심역량": ["보건교육", "상담", "프로그램 기획", "자료분석"],
        "추천경험": ["교육자료 제작", "건강증진 프로그램 기획", "설문/데이터 정리"],
        "로드맵": [
            "학부: 지역사회 간호 + 보건교육 설계 경험 만들기",
            "졸업 후: 공공보건사업 구조 이해",
            "1~3년: 프로그램 운영/평가 역량 강화",
            "3년+: 기획·정책·평가로 확장"
        ],
        "관련자격": ["보건교육사(해당 시)"],
        "한줄": "질병 ‘치료’보다 ‘예방’과 ‘건강증진’에 초점"
    },
    {
        "emoji": "🏭",
        "직무": "산업간호/보건관리자",
        "분야": "산업/기업",
        "근무환경": "기업/사업장",
        "추천성향": ["체계적", "조정/협업", "예방/안전"],
        "핵심역량": ["건강상담", "안전보건 이해", "교육/캠페인 운영", "리포팅"],
        "추천경험": ["근골격계 예방 교육 설계", "사업장 사례 학습", "지표 기반 보고서"],
        "로드맵": [
            "학부: 산업보건/역학 기본 이해",
            "졸업 후: 사업장 건강관리 프로세스 습득",
            "1~3년: 교육/캠페인 운영 + 보고 역량 강화",
            "3년+: 조직 차원 건강전략/리더 역할"
        ],
        "관련자격": ["보건관리자 요건 확인", "산업안전 관련 교육(선택)"],
        "한줄": "직장인의 건강과 안전을 설계·운영"
    },
    {
        "emoji": "📑",
        "직무": "연구간호사(CRC)",
        "분야": "연구",
        "근무환경": "임상시험센터/병원",
        "추천성향": ["꼼꼼함", "문서/규정", "데이터"],
        "핵심역량": ["GCP 이해", "문서관리", "대상자 관리", "커뮤니케이션"],
        "추천경험": ["연구보조", "논문 읽기", "엑셀 정리/기초 통계"],
        "로드맵": [
            "학부: 연구방법론/통계 기초 만들기",
            "졸업 후: CRC 입문(기관별 교육 수료)",
            "1~3년: 프로토콜/규정 숙련 + 프로젝트 리딩",
            "3년+: CRA/PM/연구기획으로 확장"
        ],
        "관련자격": ["GCP 교육(권장)"],
        "한줄": "임상시험이 ‘규정대로’ 굴러가게 만드는 핵심"
    },
    {
        "emoji": "🎓",
        "직무": "간호교육/학계(대학원 진학)",
        "분야": "교육/학계",
        "근무환경": "대학/교육기관",
        "추천성향": ["설명/가르침", "탐구", "글쓰기"],
        "핵심역량": ["강의설계", "연구설계", "논문작성", "멘토링"],
        "추천경험": ["튜터링/조교", "학회 발표", "연구 참여"],
        "로드맵": [
            "학부: 연구경험/영어/성적 관리 + 관심주제 탐색",
            "석사: 연구역량 강화 + 실습지도 경험",
            "박사: 독립연구/논문/강의",
            "이후: 전임/교육전문가로 진출"
        ],
        "관련자격": ["교육 관련 연수(선택)"],
        "한줄": "현장을 교육과 연구로 확장하는 커리어"
    },
    {
        "emoji": "📱",
        "직무": "디지털헬스/간호정보(간호IT)",
        "분야": "디지털헬스",
        "근무환경": "병원/기업/스타트업",
        "추천성향": ["기술 흥미", "문제해결", "데이터"],
        "핵심역량": ["EMR/데이터 이해", "프로젝트 협업", "기초분석", "UX 관점"],
        "추천경험": ["데이터 분석 기초", "서비스 기획 참여", "QI/지표 관리"],
        "로드맵": [
            "학부: 데이터/정보 기초 + 현장 문제 발굴",
            "초기: QI/지표/EMR 관련 경험",
            "1~3년: PM/기획/분석 역할 확장",
            "3년+: 디지털헬스 리더로 성장"
        ],
        "관련자격": ["데이터/PM 관련 교육(선택)"],
        "한줄": "간호 + 데이터/서비스로 문제를 푸는 커리어"
    },
]

SKILLS = [
    "의사소통", "팀워크", "스트레스 관리", "문서/규정 준수", "데이터/분석",
    "교육/설명", "기기/기술 친화", "리더십", "우선순위 판단", "공감/상담",
    "임상추론", "감염관리", "프로그램 기획"
]

def render_tags(tags):
    html = "".join([f"<span class='tag'>{t}</span>" for t in tags])
    st.markdown(html, unsafe_allow_html=True)

def save_inquiry(record: dict, path: str = "inquiries.jsonl"):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def score_career(career, selected_skills, trait_fast, trait_precise, trait_prevent, trait_rules, trait_tech, trait_teach):
    core = set(career["핵심역량"])
    skill_score = sum(1 for s in selected_skills if s in core)

    bonus = 0
    title = career["직무"]
    if "응급" in title:
        bonus += (trait_fast - 3)
    if "중환자" in title:
        bonus += (trait_precise - 3)
    if "보건소" in title or "지역사회" in title:
        bonus += (trait_prevent - 3)
    if "연구간호" in title or "CRC" in title:
        bonus += (trait_rules - 3)
    if "디지털헬스" in title or "정보" in title or "IT" in title:
        bonus += (trait_tech - 3)
    if "교육" in title or "학계" in title or "대학원" in title:
        bonus += (trait_teach - 3)

    total = skill_score + bonus
    return total, skill_score, bonus

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🩺 Nursing Career Lab")
menu = st.sidebar.radio("메뉴", ["🏠 홈", "🔎 진로탐색", "🧭 자가진단", "🗺️ 로드맵", "✉️ 상담/문의"])
st.sidebar.markdown("---")
st.sidebar.caption("✨ 학부생용 ‘가볍고 예쁜’ 샘플 UI 버전")

# -----------------------------
# Header (Hero)
# -----------------------------
st.markdown(f"""
<div class="hero">
  <p class="hero-title">🩺 간호학과 진로탐색 사이트</p>
  <p class="hero-desc">
    관심 분야를 찾고(🔎) → 나에게 맞는 직무를 추천받고(🧭) → 이번 학기부터 준비 로드맵까지(🗺️)
  </p>
</div>
""", unsafe_allow_html=True)

st.write("")

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"<div class='kpi'><div class='label'>진로 카드</div><div class='value'>🎯 {len(CAREERS)}개</div></div>", unsafe_allow_html=True)
with k2:
    st.markdown(f"<div class='kpi'><div class='label'>역량 항목</div><div class='value'>🧠 {len(SKILLS)}개</div></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div class='kpi'><div class='label'>오늘</div><div class='value'>📅 {datetime.now().strftime('%Y-%m-%d')}</div></div>", unsafe_allow_html=True)
with k4:
    st.markdown(f"<div class='kpi'><div class='label'>TIP</div><div class='value'>💡 ‘카드 클릭’</div></div>", unsafe_allow_html=True)

st.write("")

# -----------------------------
# Pages
# -----------------------------
if menu == "🏠 홈":
    st.markdown("<div class='h1'>✨ 어디로 갈지 모르겠다면, 여기서부터!</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtle'>학부생이 보기 쉽게 ‘카드형’으로 진로를 정리했어요. 자가진단도 해보세요 🙂</div>", unsafe_allow_html=True)
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.subheader("🚀 빠른 시작")
        st.markdown("""
- 🔎 **진로탐색**: 분야/환경 필터로 직무를 골라보기  
- 🧭 **자가진단**: 성향+역량으로 Top 추천 보기  
- 🗺️ **로드맵**: 이번 학기부터 뭘 준비할지 체크  
        """)
    with c2:
        st.subheader("🌱 추천 사용법")
        st.markdown("""
1) 흥미 가는 카드 2~3개 저장(메모)  
2) 각 직무의 **핵심역량**을 보고 부족한 부분을 체크  
3) 로드맵대로 ‘이번 학기 할 일’만 뽑기  
        """)

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.subheader("🔥 인기 진로(예시)")
    cols = st.columns(4)
    for i, career in enumerate(CAREERS[:4]):
        with cols[i]:
            st.markdown(f"""
            <div class='card'>
              <div style='font-size:1.35rem; font-weight:900;'>{career['emoji']} {career['직무']}</div>
              <div style='margin-top:6px; color:#374151;'>{career['한줄']}</div>
              <div style='margin-top:10px;'>
                <span class='badge'>#{career['분야']}</span>
                <span class='badge2'>@{career['근무환경']}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

elif menu == "🔎 진로탐색":
    st.markdown("<div class='h1'>🔎 진로 카드 둘러보기</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtle'>필터로 좁혀보고, 마음에 드는 카드를 눌러 상세를 확인하세요.</div>", unsafe_allow_html=True)
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    df = pd.DataFrame([{
        "직무": f"{c['emoji']} {c['직무']}",
        "분야": c["분야"],
        "근무환경": c["근무환경"],
        "한줄": c["한줄"],
    } for c in CAREERS])

    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        fields = st.multiselect("분야", sorted(df["분야"].unique().tolist()))
    with f2:
        envs = st.multiselect("근무환경", sorted(df["근무환경"].unique().tolist()))
    with f3:
        keyword = st.text_input("키워드 검색 (예: ICU, 데이터, 교육, 트리아지)", "")

    filtered = df.copy()
    if fields:
        filtered = filtered[filtered["분야"].isin(fields)]
    if envs:
        filtered = filtered[filtered["근무환경"].isin(envs)]
    if keyword.strip():
        k = keyword.strip()
        filtered = filtered[
            filtered["직무"].str.contains(k, case=False) |
            filtered["한줄"].str.contains(k, case=False)
        ]

    st.caption(f"📌 검색 결과: {len(filtered)}개")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.subheader("🃏 카드 보기")

    # 카드 그리드
    cols = st.columns(4)
    for i, c in enumerate(CAREERS):
        # 필터 적용된 목록만 보여주기 위해 체크
        row_title = f"{c['emoji']} {c['직무']}"
        if row_title not in filtered["직무"].values:
            continue

        with cols[i % 4]:
            st.markdown(f"""
            <div class='card'>
              <div style='font-size:1.2rem; font-weight:900;'>{c['emoji']} {c['직무']}</div>
              <div style='margin-top:6px; color:#4b5563;'>{c['한줄']}</div>
              <div style='margin-top:10px;'>
                <span class='badge'>#{c['분야']}</span>
                <span class='badge2'>@{c['근무환경']}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"🔍 상세보기", key=f"detail_{i}"):
                st.session_state["selected_job"] = c["직무"]

    st.write("")
    job = st.session_state.get("selected_job", None)
    if job:
        c = next(x for x in CAREERS if x["직무"] == job)
        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
        st.markdown(f"## {c['emoji']} {c['직무']}")
        st.write(c["한줄"])
        b1, b2 = st.columns([2, 1])
        with b1:
            st.markdown(f"**분야**: {c['분야']}  |  **근무환경**: {c['근무환경']}")
            st.markdown("### 💛 추천 성향")
            render_tags(c["추천성향"])
            st.markdown("### 🧠 핵심 역량")
            render_tags(c["핵심역량"])
        with b2:
            st.markdown("### ✅ 추천 경험")
            st.write("\n".join([f"- {x}" for x in c["추천경험"]]))
            st.markdown("### 🏷️ 관련 자격/교육")
            st.write("\n".join([f"- {x}" for x in c["관련자격"]]))

elif menu == "🧭 자가진단":
    st.markdown("<div class='h1'>🧭 자가진단으로 ‘나에게 맞는’ 진로 찾기</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtle'>완전 진지한 검사라기보다, ‘방향을 잡는’ 가벼운 추천이에요 🙂</div>", unsafe_allow_html=True)
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    st.subheader("1) 나의 성향은?")
    c1, c2, c3 = st.columns(3)
    with c1:
        trait_fast = st.slider("🚑 속도감/긴급상황 대처", 1, 5, 3)
        trait_precise = st.slider("🫁 정밀함/기기·수치 친화", 1, 5, 3)
    with c2:
        trait_prevent = st.slider("🏘️ 예방/교육/장기관리 선호", 1, 5, 3)
        trait_rules = st.slider("📑 문서/규정/체계 좋아함", 1, 5, 3)
    with c3:
        trait_tech = st.slider("📱 기술/데이터 흥미", 1, 5, 3)
        trait_teach = st.slider("🎓 가르치기/설명 선호", 1, 5, 3)

    st.subheader("2) 이번 학기에 키우고 싶은 역량(복수 선택)")
    selected_skills = st.multiselect("🧩 역량 선택", SKILLS, default=["의사소통", "팀워크"])

    st.write("")
    if st.button("✨ 추천 받기", type="primary"):
        results = []
        for c in CAREERS:
            total, sscore, bonus = score_career(
                c, selected_skills,
                trait_fast, trait_precise, trait_prevent, trait_rules, trait_tech, trait_teach
            )
            results.append((total, sscore, bonus, c))

        results.sort(key=lambda x: x[0], reverse=True)

        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
        st.subheader("🏆 추천 TOP 3")

        top3 = results[:3]
        cols = st.columns(3)
        for i, (total, sscore, bonus, c) in enumerate(top3):
            with cols[i]:
                st.markdown(f"""
                <div class='card'>
                  <div style='font-size:1.25rem; font-weight:900;'>{c['emoji']} {c['직무']}</div>
                  <div style='margin-top:6px; color:#4b5563;'>{c['한줄']}</div>
                  <div style='margin-top:10px;'>
                    <span class='badge'>#{c['분야']}</span>
                    <span class='badge2'>@{c['근무환경']}</span>
                  </div>
                  <div style='margin-top:10px; font-weight:800;'>점수: {total:.1f}</div>
                  <div style='color:#6b7280; font-size:0.9rem;'>역량 {sscore} + 성향 {bonus:+.1f}</div>
                </div>
                """, unsafe_allow_html=True)

        st.subheader("🧠 이 직무들이 추천된 이유(요약)")
        for rank, (total, sscore, bonus, c) in enumerate(top3, start=1):
            st.markdown(f"**#{rank} {c['emoji']} {c['직무']}** — 핵심역량 매칭 *{sscore}개*, 성향 보너스 *{bonus:+.1f}*")
            st.caption("핵심역량")
            render_tags(c["핵심역량"])
            st.caption("추천 경험")
            st.write("\n".join([f"- {x}" for x in c["추천경험"]]))

elif menu == "🗺️ 로드맵":
    st.markdown("<div class='h1'>🗺️ 진로 로드맵</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtle'>선택한 직무 기준으로 ‘이번 학기 할 일’을 구체화해요.</div>", unsafe_allow_html=True)
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    job = st.selectbox("🃏 직무 선택", [f"{c['emoji']} {c['직무']}" for c in CAREERS])
    raw_job = job.split(" ", 1)[1]
    c = next(x for x in CAREERS if x["직무"] == raw_job)

    left, right = st.columns([2, 1])
    with left:
        st.markdown(f"## {c['emoji']} {c['직무']}")
        st.write(c["한줄"])
        st.markdown("### 📌 단계별 준비")
        for step in c["로드맵"]:
            st.markdown(f"- {step}")

        st.markdown("### ✅ 이번 학기 체크리스트")
        checklist = [
            "관련 과목(병태/약리/기본) 요약노트 만들기",
            "실습 케이스 1개 ‘완성본’으로 정리(사정-진단-중재-평가)",
            "직무 관련 자격/교육 일정 확인하기",
            "현직 선배 인터뷰 질문 10개 만들기",
            "포트폴리오(활동/수상/프로젝트) 1페이지로 정리"
        ]
        for item in checklist:
            st.checkbox(item, value=False)

    with right:
        st.markdown("### 🏷️ 태그")
        st.markdown(f"<span class='badge'>#{c['분야']}</span> <span class='badge2'>@{c['근무환경']}</span>", unsafe_allow_html=True)
        st.markdown("### 🧠 핵심 역량")
        render_tags(c["핵심역량"])
        st.markdown("### 🎟️ 관련 자격/교육")
        st.write("\n".join([f"- {x}" for x in c["관련자격"]]))

elif menu == "✉️ 상담/문의":
    st.markdown("<div class='h1'>✉️ 상담/문의</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtle'>학생 질문을 모아두면 다음 해에 ‘FAQ’로 발전시키기 좋아요.</div>", unsafe_allow_html=True)
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    with st.form("inquiry", clear_on_submit=True):
        name = st.text_input("🙋 이름(닉네임 가능)")
        contact = st.text_input("📩 연락처(이메일 등)")
        topic = st.selectbox("🧩 주제", ["진로 상담", "실습/취업 준비", "대학원/연구", "기타"])
        message = st.text_area("💬 내용", height=160, placeholder="현재 고민/관심 진로/원하는 도움을 구체적으로 적어주세요.")
        agree = st.checkbox("✅ 개인정보 수집 및 이용에 동의합니다(샘플)")
        submitted = st.form_submit_button("📨 보내기", type="primary")

    if submitted:
        if not agree:
            st.error("동의 체크가 필요해요!")
        elif not message.strip():
            st.error("내용을 입력해주세요!")
        else:
            record = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "name": name.strip(),
                "contact": contact.strip(),
                "topic": topic,
                "message": message.strip()
            }
            save_inquiry(record)
            st.success("저장 완료! (샘플: inquiries.jsonl 파일에 누적 저장됩니다)")

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.subheader("🔐 관리자용: 최근 문의 미리보기(로컬)")
    path = "inquiries.jsonl"
    if os.path.exists(path):
        rows = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except:
                    pass
        if rows:
            df = pd.DataFrame(rows[::-1]).head(10)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.caption("저장된 문의가 없어요.")
    else:
        st.caption("아직 문의가 없어요. 1개 저장하면 파일이 생성됩니다.")
