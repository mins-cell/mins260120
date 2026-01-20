import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="간호학과 진로탐색",
    page_icon="🩺",
    layout="wide",
)

# -----------------------------
# 샘플 데이터 (원하면 나중에 CSV/DB로 교체)
# -----------------------------
CAREERS = [
    {
        "직무": "임상간호사(병동/특수부서)",
        "분야": "임상",
        "근무환경": "병원",
        "추천성향": ["사람 중심", "현장 역동", "팀워크"],
        "핵심역량": ["의사소통", "임상추론", "우선순위 판단", "스트레스 관리"],
        "추천경험": ["실습 중 케이스 스터디", "시뮬레이션", "BLS/ACLS 관심"],
        "로드맵": [
            "학부: 기본간호/성인/아동/모성/정신 실습 충실",
            "졸업 후: 신규간호사 교육/프리셉터십",
            "1~3년: 관심부서 전환(중환자실/응급 등) + 전문역량 강화",
            "3년+: 전문간호/교육/리더 역할 확장"
        ],
        "관련자격": ["BLS", "ACLS(선택)", "전문간호사(향후)"],
        "한줄": "환자 곁에서 가장 가까이 돌보는 핵심 역할"
    },
    {
        "직무": "응급간호/응급실 코디네이션",
        "분야": "임상",
        "근무환경": "응급실",
        "추천성향": ["속도감", "판단력", "긴장 상황 대처"],
        "핵심역량": ["ABCDE 평가", "팀리더십", "트리아지", "커뮤니케이션"],
        "추천경험": ["응급 시뮬레이션", "BLS/ACLS", "트리아지 사례 학습"],
        "로드맵": [
            "학부: 응급/중환자 파트 집중 학습",
            "졸업 후: ER 신규 교육 + 프로토콜 숙지",
            "1~3년: 트리아지 숙련 + 소생팀 경험",
            "3년+: 전문역할(교육, QI, 코디네이터) 확장"
        ],
        "관련자격": ["BLS", "ACLS", "PALS(선택)"],
        "한줄": "급성기 환자를 빠르게 분류·안정화하는 최전선"
    },
    {
        "직무": "중환자실(ICU) 간호",
        "분야": "임상",
        "근무환경": "중환자실",
        "추천성향": ["정밀함", "깊이 있는 학습", "기술 친화"],
        "핵심역량": ["중환자 모니터링", "기기관리", "약물/수액", "감염관리"],
        "추천경험": ["ABGA/ventilator 기초", "QI 프로젝트", "중환자 케이스 스터디"],
        "로드맵": [
            "학부: 생리/병태생리 탄탄히 + 중환자 간호 개념 정리",
            "졸업 후: ICU 신규 교육 + 장비/프로토콜 습득",
            "1~3년: 중증도 높은 케이스 경험 + 인증 과정 참여",
            "3년+: 전문간호/연구/QI로 확장"
        ],
        "관련자격": ["BLS", "ACLS", "CRRT/ECMO 교육(기관)"],
        "한줄": "중증 환자 생명유지 치료를 정교하게 관리"
    },
    {
        "직무": "보건소/지역사회 간호",
        "분야": "지역사회",
        "근무환경": "공공/지역",
        "추천성향": ["예방 중심", "교육", "장기 관점"],
        "핵심역량": ["보건교육", "프로그램 기획", "대상자 상담", "자료분석"],
        "추천경험": ["건강증진 프로그램 기획", "설문/자료분석", "교육자료 제작"],
        "로드맵": [
            "학부: 지역사회 간호 + 보건교육 설계 경험",
            "졸업 후: 공공기관/보건사업 이해",
            "1~3년: 프로그램 운영/평가 역량 강화",
            "3년+: 기획·정책·평가로 확장"
        ],
        "관련자격": ["보건교육사(해당 시)", "건강관리 관련 교육"],
        "한줄": "질병 ‘치료’보다 ‘예방’과 ‘건강증진’에 초점"
    },
    {
        "직무": "산업간호/보건관리자",
        "분야": "산업/기업",
        "근무환경": "기업/사업장",
        "추천성향": ["체계적", "조정/협업", "예방/안전"],
        "핵심역량": ["건강검진/상담", "작업환경 이해", "안전보건 법규", "프로그램 운영"],
        "추천경험": ["산업보건 사례 학습", "근골격계/감염 예방 교육 설계", "데이터 기반 보고서"],
        "로드맵": [
            "학부: 산업보건/역학 기본 이해",
            "졸업 후: 사업장 건강관리 프로세스 습득",
            "1~3년: 안전보건체계 운영 + 교육/캠페인 기획",
            "3년+: 조직 차원 건강전략/리더 역할"
        ],
        "관련자격": ["산업위생/안전 관련 교육(선택)", "보건관리자 요건 확인"],
        "한줄": "직장인의 건강과 안전을 설계·운영"
    },
    {
        "직무": "연구간호사(CRC/CRA 보조)",
        "분야": "연구",
        "근무환경": "병원/임상시험센터/제약",
        "추천성향": ["꼼꼼함", "문서/규정", "데이터"],
        "핵심역량": ["GCP 이해", "문서관리", "대상자 관리", "커뮤니케이션"],
        "추천경험": ["연구보조 경험", "논문 읽기", "엑셀/데이터 정리"],
        "로드맵": [
            "학부: 연구방법론/통계 기초",
            "졸업 후: CRC로 시작(기관별 교육)",
            "1~3년: 프로토콜/규정 숙련 + 프로젝트 리딩",
            "3년+: CRA/PM/연구기획으로 확장"
        ],
        "관련자격": ["GCP 교육(필수급)", "CRA 교육(선택)"],
        "한줄": "임상시험을 ‘규정대로’ 굴러가게 만드는 핵심"
    },
    {
        "직무": "간호교육/교수(석·박사 진학)",
        "분야": "교육/학계",
        "근무환경": "대학/교육기관",
        "추천성향": ["설명/가르침", "깊이 있는 탐구", "글쓰기"],
        "핵심역량": ["강의설계", "연구설계", "논문작성", "멘토링"],
        "추천경험": ["튜터링/조교", "학회 발표", "연구 프로젝트 참여"],
        "로드맵": [
            "학부: 성적/연구경험/영어 준비",
            "석사: 연구역량 강화 + 교육/실습지도 경험",
            "박사: 독립연구/논문/펀딩/강의",
            "이후: 전임교원/교육전문가 진출"
        ],
        "관련자격": ["교육 관련 연수(선택)"],
        "한줄": "현장을 교육과 연구로 확장하는 커리어"
    },
    {
        "직무": "디지털헬스/간호정보(간호IT)",
        "분야": "디지털헬스",
        "근무환경": "병원/기업/스타트업",
        "추천성향": ["기술 흥미", "문제해결", "데이터"],
        "핵심역량": ["EMR/데이터 이해", "UX 관점", "프로젝트 협업", "기초분석"],
        "추천경험": ["데이터 분석 기초", "앱/서비스 기획 참여", "QI/지표 관리"],
        "로드맵": [
            "학부: 정보/데이터 기초 + 현장 문제 발굴",
            "초기: QI/지표/EMR 관련 업무 경험",
            "1~3년: PM/기획/분석 역할 확장",
            "3년+: 전문분야(간호정보, 디지털헬스) 리더로 성장"
        ],
        "관련자격": ["데이터/PM 관련 교육(선택)"],
        "한줄": "간호 + 데이터/서비스로 문제를 푸는 커리어"
    },
]

SKILLS = [
    "의사소통", "팀워크", "스트레스 관리", "문서/규정 준수", "데이터/분석",
    "교육/설명", "기기/기술 친화", "리더십", "우선순위 판단", "공감/상담"
]

# -----------------------------
# 유틸
# -----------------------------
def careers_df():
    rows = []
    for c in CAREERS:
        rows.append({
            "직무": c["직무"],
            "분야": c["분야"],
            "근무환경": c["근무환경"],
            "한줄": c["한줄"],
            "추천성향": ", ".join(c["추천성향"]),
            "핵심역량": ", ".join(c["핵심역량"]),
            "관련자격": ", ".join(c["관련자격"]),
        })
    return pd.DataFrame(rows)

def save_inquiry(record: dict, path: str = "inquiries.jsonl"):
    line = json.dumps(record, ensure_ascii=False)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def render_tag_list(tags):
    cols = st.columns(min(4, len(tags)) if tags else 1)
    for i, t in enumerate(tags):
        cols[i % len(cols)].markdown(f"- **{t}**")

def score_career_by_skills(career, selected_skills):
    # 아주 단순 매칭: 핵심역량에 포함되면 +1
    core = set(career["핵심역량"])
    return sum(1 for s in selected_skills if s in core)

# -----------------------------
# 사이드바 네비게이션
# -----------------------------
st.sidebar.title("🩺 간호학과 진로탐색")
page = st.sidebar.radio(
    "메뉴",
    ["홈", "진로 탐색", "자가진단", "진로 로드맵", "자료실", "상담/문의"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.caption("※ 샘플 앱입니다. 데이터/문항/로드맵은 학과 상황에 맞게 수정하세요.")

# -----------------------------
# 페이지: 홈
# -----------------------------
if page == "홈":
    st.title("🩺 간호학과 진로탐색 웹앱")
    st.markdown(
        """
이 사이트는 간호학과 학생이 **관심 분야를 넓히고**, **나에게 맞는 커리어를 빠르게 후보로 뽑고**,  
**다음 학기부터 무엇을 준비할지(로드맵)**까지 연결해주는 것을 목표로 합니다.
        """
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("진로 카드 수", f"{len(CAREERS)}개")
    with col2:
        st.metric("역량 항목 수", f"{len(SKILLS)}개")
    with col3:
        st.metric("오늘 날짜", datetime.now().strftime("%Y-%m-%d"))

    st.subheader("빠른 시작")
    st.markdown(
        """
- **진로 탐색**: 관심 분야/근무환경으로 필터하고 직무를 비교  
- **자가진단**: 성향·역량 기반으로 추천 직무 Top을 확인  
- **진로 로드맵**: 학부→졸업→1~3년→3년+ 단계별 준비 체크  
        """
    )

    st.subheader("진로 분포(샘플)")
    df = careers_df()
    left, right = st.columns(2)
    with left:
        st.write(df[["직무", "분야", "근무환경", "한줄"]])
    with right:
        # 간단한 분포표
        st.write("분야별 개수")
        st.bar_chart(df["분야"].value_counts())

# -----------------------------
# 페이지: 진로 탐색
# -----------------------------
elif page == "진로 탐색":
    st.title("🔎 진로 탐색")
    df = careers_df()

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        field = st.multiselect("분야", sorted(df["분야"].unique().tolist()))
    with c2:
        env = st.multiselect("근무환경", sorted(df["근무환경"].unique().tolist()))
    with c3:
        keyword = st.text_input("키워드(직무/한줄/역량 등)", "")

    filtered = df.copy()
    if field:
        filtered = filtered[filtered["분야"].isin(field)]
    if env:
        filtered = filtered[filtered["근무환경"].isin(env)]
    if keyword.strip():
        k = keyword.strip()
        mask = (
            filtered["직무"].str.contains(k, case=False) |
            filtered["한줄"].str.contains(k, case=False) |
            filtered["추천성향"].str.contains(k, case=False) |
            filtered["핵심역량"].str.contains(k, case=False) |
            filtered["관련자격"].str.contains(k, case=False)
        )
        filtered = filtered[mask]

    st.caption(f"검색 결과: {len(filtered)}개")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("직무 상세 보기")

    job = st.selectbox("직무 선택", ["(선택하세요)"] + [c["직무"] for c in CAREERS])
    if job != "(선택하세요)":
        career = next(c for c in CAREERS if c["직무"] == job)

        left, right = st.columns([2, 1])
        with left:
            st.markdown(f"### {career['직무']}")
            st.write(career["한줄"])
            st.markdown(f"- **분야**: {career['분야']}")
            st.markdown(f"- **근무환경**: {career['근무환경']}")

            st.markdown("#### 추천 성향")
            render_tag_list(career["추천성향"])

            st.markdown("#### 핵심 역량")
            render_tag_list(career["핵심역량"])

        with right:
            st.markdown("#### 추천 경험")
            st.write("\n".join([f"- {x}" for x in career["추천경험"]]))
            st.markdown("#### 관련 자격/교육")
            st.write("\n".join([f"- {x}" for x in career["관련자격"]]))

# -----------------------------
# 페이지: 자가진단
# -----------------------------
elif page == "자가진단":
    st.title("🧭 자가진단 (간단 버전)")
    st.markdown("아래 문항은 샘플이야. 학과/기관 기준으로 문항을 늘려도 좋아.")

    st.subheader("1) 선호 성향")
    trait_q = {
        "현장 속도감이 좋다(응급/급성기 선호)": "속도감",
        "정밀한 관찰/기기/수치 해석이 흥미롭다(ICU 등)": "정밀함",
        "예방·교육·장기관리(만성/지역)가 끌린다": "예방 중심",
        "문서/규정/체계적인 업무가 편하다(연구/관리)": "규정/체계",
        "기술/서비스/데이터로 문제를 푸는 게 재미있다": "기술/데이터",
        "가르치고 설명하는 역할이 잘 맞는다(교육/학계)": "교육 성향",
    }
    trait_scores = {}
    for q, tag in trait_q.items():
        trait_scores[tag] = st.slider(q, 1, 5, 3)

    st.subheader("2) 현재 내가 키우고 싶은 역량(복수 선택)")
    selected_skills = st.multiselect("역량 선택", SKILLS, default=["의사소통", "팀워크"])

    st.markdown("---")
    if st.button("추천 직무 보기", type="primary"):
        results = []
        for c in CAREERS:
            skill_score = score_career_by_skills(c, selected_skills)

            # 성향 점수는 아주 단순 매핑(샘플)
            trait_bonus = 0
            if c["직무"].startswith("응급"):
                trait_bonus += trait_scores["속도감"] - 3
            if "중환자" in c["직무"]:
                trait_bonus += trait_scores["정밀함"] - 3
            if "지역사회" in c["직무"] or "보건소" in c["직무"]:
                trait_bonus += trait_scores["예방 중심"] - 3
            if "연구간호" in c["직무"]:
                trait_bonus += trait_scores["규정/체계"] - 3
            if "디지털헬스" in c["직무"] or "정보" in c["직무"]:
                trait_bonus += trait_scores["기술/데이터"] - 3
            if "교육" in c["직무"] or "교수" in c["직무"]:
                trait_bonus += trait_scores["교육 성향"] - 3

            total = skill_score + trait_bonus
            results.append((total, skill_score, trait_bonus, c["직무"], c["한줄"]))

        results.sort(reverse=True, key=lambda x: x[0])

        st.subheader("추천 Top 5")
        top = results[:5]
        for rank, (total, skill_score, trait_bonus, job, one) in enumerate(top, start=1):
            with st.expander(f"#{rank} {job}  | 점수 {total:.1f} (역량 {skill_score} + 성향 {trait_bonus:+.1f})"):
                st.write(one)
                career = next(c for c in CAREERS if c["직무"] == job)
                st.markdown("**핵심 역량**")
                render_tag_list(career["핵심역량"])
                st.markdown("**추천 경험**")
                st.write("\n".join([f"- {x}" for x in career["추천경험"]]))

        st.caption("※ 이 추천은 ‘샘플 규칙 기반’입니다. 실제 운영 시 문항/가중치/데이터를 개선하세요.")

# -----------------------------
# 페이지: 진로 로드맵
# -----------------------------
elif page == "진로 로드맵":
    st.title("🗺️ 진로 로드맵")
    job = st.selectbox("직무 선택", [c["직무"] for c in CAREERS])

    career = next(c for c in CAREERS if c["직무"] == job)
    st.markdown(f"## {career['직무']}")
    st.write(career["한줄"])
    st.markdown("---")

    left, right = st.columns([2, 1])
    with left:
        st.subheader("단계별 준비")
        for step in career["로드맵"]:
            st.markdown(f"- {step}")

        st.subheader("체크리스트(개인용)")
        checklist = [
            "관련 과목 복습/정리",
            "실습 케이스/포트폴리오 준비",
            "자격/교육(해당 시) 일정 확인",
            "관심부서/기관 정보 수집",
            "멘토(선배/교수/현장)에게 질문 리스트 만들기",
        ]
        checked = {}
        for item in checklist:
            checked[item] = st.checkbox(item, value=False)

    with right:
        st.subheader("관련 자격/교육")
        for x in career["관련자격"]:
            st.markdown(f"- {x}")

        st.subheader("핵심 역량")
        render_tag_list(career["핵심역량"])

# -----------------------------
# 페이지: 자료실
# -----------------------------
elif page == "자료실":
    st.title("📚 자료실(샘플)")
    st.markdown("학과에서 제공하는 자료(가이드, 링크, PDF)를 여기 모아두는 구조로 확장하면 좋아.")

    resources = [
        {"구분": "자기소개서", "제목": "신규간호사 자소서 체크리스트", "설명": "STAR 기반으로 경험 구조화"},
        {"구분": "면접", "제목": "임상 면접 질문 30선", "설명": "상황/역량/태도 문항 대비"},
        {"구분": "학습", "제목": "ICU/ER 기초 개념 학습 로드맵", "설명": "ABGA/ventilator/트리아지 등"},
        {"구분": "연구", "제목": "CRC 입문 가이드", "설명": "GCP/문서관리/대상자 관리 개요"},
        {"구분": "디지털헬스", "제목": "간호 데이터/EMR 기초", "설명": "지표/대시보드/QA 개념"},
    ]
    rdf = pd.DataFrame(resources)

    cat = st.selectbox("구분", ["전체"] + sorted(rdf["구분"].unique().tolist()))
    if cat != "전체":
        rdf = rdf[rdf["구분"] == cat]

    st.dataframe(rdf, use_container_width=True, hide_index=True)

    st.info("실제 운영에서는 파일 업로드/링크 모음/공지(학과 일정) 등을 붙이면 완성도가 확 올라가요.")

# -----------------------------
# 페이지: 상담/문의
# -----------------------------
elif page == "상담/문의":
    st.title("✉️ 상담/문의")
    st.markdown("학생들이 남긴 문의를 **로컬 파일(JSONL)** 로 저장하는 샘플이야(운영 서버에서는 DB로 교체 권장).")

    with st.form("inquiry_form", clear_on_submit=True):
        name = st.text_input("이름(닉네임 가능)", "")
        email = st.text_input("연락처(이메일 등)", "")
        topic = st.selectbox("문의 주제", ["진로 상담", "실습/취업 준비", "대학원/연구", "기타"])
        message = st.text_area("문의 내용", height=160, placeholder="현재 고민/관심 진로/원하는 도움을 구체적으로 적어주세요.")
        agree = st.checkbox("개인정보 수집 및 이용에 동의합니다(샘플 문구)")
        submitted = st.form_submit_button("문의 제출", type="primary")

    if submitted:
        if not agree:
            st.error("동의 체크가 필요합니다.")
        elif not message.strip():
            st.error("문의 내용을 입력해주세요.")
        else:
            record = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "name": name.strip(),
                "contact": email.strip(),
                "topic": topic,
                "message": message.strip()
            }
            save_inquiry(record)
            st.success("문의가 저장되었습니다. (샘플: inquiries.jsonl 파일에 누적 저장)")

    st.markdown("---")
    st.subheader("관리자용: 최근 문의 미리보기(로컬)")
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
            preview = pd.DataFrame(rows[::-1]).head(10)  # 최근 10개
            st.dataframe(preview, use_container_width=True, hide_index=True)
        else:
            st.caption("저장된 문의가 없습니다.")
    else:
        st.caption("아직 inquiries.jsonl 파일이 없습니다. 문의를 1개 저장하면 생성됩니다.")
