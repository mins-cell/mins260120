import streamlit as st
import sqlite3
from datetime import date, datetime, timedelta
import pandas as pd

# =============================
# Page config + UI
# =============================
st.set_page_config(page_title="Campus Planner", page_icon="📚", layout="wide")

st.markdown("""
<style>
.main {background: #fbfbff;}
.block-container {padding-top: 1.0rem; padding-bottom: 2.0rem; max-width: 1400px;}
.hero{
  background: linear-gradient(135deg, #e8f3ff 0%, #f6ecff 45%, #fff1f2 100%);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 16px 18px;
  box-shadow: 0 10px 26px rgba(0,0,0,0.06);
}
.hero-title{font-size:1.7rem; font-weight:900; margin:0;}
.hero-desc{color:#374151; margin:6px 0 0 0;}

.kpi{
  background: white;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 16px;
  padding: 12px 14px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}
.kpi .label{color:#6b7280; font-size:0.9rem;}
.kpi .value{font-size:1.25rem; font-weight:900; margin-top:2px;}

.card{
  background:white;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 12px 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.045);
}
.dayhead{
  font-weight:900;
  font-size:1.05rem;
  margin:0;
}
.daydate{
  color:#6b7280;
  font-size:0.9rem;
  margin-top:2px;
}
.pill{
  display:inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  border: 1px solid rgba(0,0,0,0.08);
  background: rgba(99,102,241,0.10);
  color: #3730a3;
  margin-right: 6px;
  margin-top: 6px;
}
.pill2{
  display:inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  border: 1px solid rgba(0,0,0,0.08);
  background: rgba(16,185,129,0.12);
  color: #065f46;
  margin-right: 6px;
  margin-top: 6px;
}
.todo{
  padding: 8px 10px;
  border-radius: 14px;
  border: 1px solid rgba(0,0,0,0.06);
  background: rgba(0,0,0,0.02);
  margin: 8px 0;
}
.todo.done{
  opacity: 0.62;
  text-decoration: line-through;
}
.small {color:#6b7280; font-size:0.88rem;}
.hr{margin: 12px 0; border-top: 1px solid rgba(0,0,0,0.08);}
.stButton>button{border-radius: 12px; font-weight: 800; padding: 0.55rem 0.95rem;}
</style>
""", unsafe_allow_html=True)

# =============================
# DB (SQLite) - persistent
# =============================
DB_PATH = "planner.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT NOT NULL,              -- YYYY-MM-DD
        title TEXT NOT NULL,
        category TEXT DEFAULT '📌 일반',
        priority TEXT DEFAULT '⭐ 보통', -- ⭐ 보통 / 🔥 높음 / 🧊 낮음
        done INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT DEFAULT '진행중',     -- 진행중/대기/완료
        progress INTEGER DEFAULT 0,      -- 0~100
        due TEXT,                       -- YYYY-MM-DD nullable
        notes TEXT DEFAULT '',
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS diary (
        day TEXT PRIMARY KEY,           -- YYYY-MM-DD (1일 1일기)
        mood TEXT DEFAULT '🙂',
        title TEXT DEFAULT '',
        content TEXT DEFAULT '',
        gratitude TEXT DEFAULT '',
        highlight TEXT DEFAULT '',
        updated_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =============================
# Date helpers
# =============================
WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]

def week_start(d: date) -> date:
    # Monday as start
    return d - timedelta(days=d.weekday())

def daterange(start: date, days: int):
    for i in range(days):
        yield start + timedelta(days=i)

def iso(d: date) -> str:
    return d.isoformat()

# =============================
# CRUD functions
# =============================
def fetch_todos_between(start: date, end: date) -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM todos WHERE day >= ? AND day <= ? ORDER BY day ASC, done ASC, id DESC",
        conn, params=(iso(start), iso(end))
    )
    conn.close()
    return df

def add_todo(day: date, title: str, category: str, priority: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO todos(day,title,category,priority,done,created_at) VALUES (?,?,?,?,0,?)",
        (iso(day), title, category, priority, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()
    conn.close()

def set_todo_done(todo_id: int, done: bool):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE todos SET done=? WHERE id=?", (1 if done else 0, todo_id))
    conn.commit()
    conn.close()

def delete_todo(todo_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id=?", (todo_id,))
    conn.commit()
    conn.close()

def fetch_projects() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM projects ORDER BY status ASC, progress DESC, id DESC", conn)
    conn.close()
    return df

def add_project(name: str, due: date | None, status: str, progress: int, notes: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO projects(name,status,progress,due,notes,created_at) VALUES (?,?,?,?,?,?)",
        (name, status, progress, iso(due) if due else None, notes, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()
    conn.close()

def update_project(pid: int, status: str, progress: int, due: date | None, notes: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE projects SET status=?, progress=?, due=?, notes=? WHERE id=?",
        (status, progress, iso(due) if due else None, notes, pid)
    )
    conn.commit()
    conn.close()

def delete_project(pid: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM projects WHERE id=?", (pid,))
    conn.commit()
    conn.close()

def fetch_diary(day: date) -> dict | None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT day,mood,title,content,gratitude,highlight,updated_at FROM diary WHERE day=?", (iso(day),))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "day": row[0], "mood": row[1], "title": row[2], "content": row[3],
        "gratitude": row[4], "highlight": row[5], "updated_at": row[6]
    }

def upsert_diary(day: date, mood: str, title: str, content: str, gratitude: str, highlight: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO diary(day,mood,title,content,gratitude,highlight,updated_at)
    VALUES (?,?,?,?,?,?,?)
    ON CONFLICT(day) DO UPDATE SET
        mood=excluded.mood,
        title=excluded.title,
        content=excluded.content,
        gratitude=excluded.gratitude,
        highlight=excluded.highlight,
        updated_at=excluded.updated_at
    """, (iso(day), mood, title, content, gratitude, highlight, datetime.now().isoformat(timespec="seconds")))
    conn.commit()
    conn.close()

# =============================
# Sidebar controls
# =============================
st.sidebar.title("📚 Campus Planner")
today = date.today()

if "anchor_date" not in st.session_state:
    st.session_state.anchor_date = today

anchor = st.sidebar.date_input("📅 기준 날짜", value=st.session_state.anchor_date)
st.session_state.anchor_date = anchor

ws = week_start(anchor)
we = ws + timedelta(days=6)

st.sidebar.markdown("---")
view_mode = st.sidebar.radio("보기", ["🗓️ 위클리 보드", "📦 프로젝트", "✍️ 오늘의 일기", "⚙️ 데이터"], index=0)

st.sidebar.caption("가로형 위클리(월~일) + 투두/프로젝트/일기 통합 ✨")

# =============================
# Header + KPI
# =============================
st.markdown(f"""
<div class="hero">
  <p class="hero-title">✨ Campus Planner (대학생용 투두 · 프로젝트 · 일기)</p>
  <p class="hero-desc">이번 주: <b>{ws.isoformat()} ~ {we.isoformat()}</b> · 가로형 위클리 보드로 한 눈에 보기 🗓️</p>
</div>
""", unsafe_allow_html=True)

todos_week = fetch_todos_between(ws, we)
projects_all = fetch_projects()

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"<div class='kpi'><div class='label'>이번 주 할 일</div><div class='value'>🧾 {len(todos_week)}개</div></div>", unsafe_allow_html=True)
with k2:
    done_cnt = int(todos_week["done"].sum()) if len(todos_week) else 0
    st.markdown(f"<div class='kpi'><div class='label'>완료</div><div class='value'>✅ {done_cnt}개</div></div>", unsafe_allow_html=True)
with k3:
    inprog = int((projects_all["status"] == "진행중").sum()) if len(projects_all) else 0
    st.markdown(f"<div class='kpi'><div class='label'>진행중 프로젝트</div><div class='value'>🚧 {inprog}개</div></div>", unsafe_allow_html=True)
with k4:
    d = fetch_diary(today)
    st.markdown(f"<div class='kpi'><div class='label'>오늘 일기</div><div class='value'>✍️ {'작성됨' if d else '미작성'}</div></div>", unsafe_allow_html=True)

st.write("")

# =============================
# VIEW: Weekly board (horizontal)
# =============================
if view_mode == "🗓️ 위클리 보드":
    st.markdown("## 🗓️ 위클리 보드 (월~일 가로형)")
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    # Quick add bar
    with st.expander("➕ 빠른 추가 (이번 주 투두)", expanded=True):
        c1, c2, c3, c4, c5 = st.columns([1, 2.6, 1.1, 1.1, 1.2])
        with c1:
            add_day = st.date_input("날짜", value=today, min_value=ws, max_value=we, key="quick_add_day")
        with c2:
            add_title = st.text_input("할 일", placeholder="예: 성인간호학 퀴즈 준비 / 팀플 회의 / 과제 제출", key="quick_add_title")
        with c3:
            add_cat = st.selectbox("카테고리", ["📌 일반", "📚 공부", "🧪 과제", "🤝 팀플", "🏃 건강", "🧹 생활"], key="quick_add_cat")
        with c4:
            add_pri = st.selectbox("우선순위", ["🔥 높음", "⭐ 보통", "🧊 낮음"], index=1, key="quick_add_pri")
        with c5:
            if st.button("추가 ✨", type="primary", key="quick_add_btn"):
                if add_title.strip():
                    add_todo(add_day, add_title.strip(), add_cat, add_pri)
                    st.success("추가 완료!")
                    st.rerun()
                else:
                    st.warning("할 일을 입력해줘!")

    # Horizontal columns: Mon..Sun
    cols = st.columns(7, gap="small")
    for i, day in enumerate(daterange(ws, 7)):
        day_iso = iso(day)
        day_name = WEEKDAY_KO[i]
        is_today = (day == today)

        with cols[i]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<p class='dayhead'>{'⭐ ' if is_today else ''}{day_name}요일</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='daydate'>{day_iso}</p>", unsafe_allow_html=True)

            # Diary indicator
            diary_row = fetch_diary(day)
            if diary_row and (diary_row.get("content","").strip() or diary_row.get("title","").strip()):
                st.markdown("<span class='pill2'>✍️ 일기 있음</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='pill'>✍️ 일기 비움</span>", unsafe_allow_html=True)

            # Todos for the day
            day_df = todos_week[todos_week["day"] == day_iso].copy()
            st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

            if day_df.empty:
                st.caption("🫧 할 일 없음")
            else:
                for _, r in day_df.iterrows():
                    todo_id = int(r["id"])
                    done = bool(r["done"])
                    title = r["title"]
                    cat = r["category"]
                    pri = r["priority"]

                    # checkbox to toggle done
                    chk_key = f"todo_done_{todo_id}"
                    new_done = st.checkbox(f"{pri} {title}", value=done, key=chk_key)

                    # update on change
                    if new_done != done:
                        set_todo_done(todo_id, new_done)
                        st.rerun()

                    # small meta + delete
                    st.caption(f"{cat}")
                    del_key = f"del_{todo_id}"
                    if st.button("🗑️", key=del_key):
                        delete_todo(todo_id)
                        st.rerun()

                    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

            # Mini add inside each day
            with st.expander("➕ 이 날에 추가", expanded=False):
                t = st.text_input("할 일", key=f"mini_title_{day_iso}", placeholder="짧게 입력")
                cat = st.selectbox("카테고리", ["📌 일반","📚 공부","🧪 과제","🤝 팀플","🏃 건강","🧹 생활"], key=f"mini_cat_{day_iso}")
                pri = st.selectbox("우선순위", ["🔥 높음","⭐ 보통","🧊 낮음"], index=1, key=f"mini_pri_{day_iso}")
                if st.button("추가", key=f"mini_add_{day_iso}"):
                    if t.strip():
                        add_todo(day, t.strip(), cat, pri)
                        st.rerun()
                    else:
                        st.warning("할 일을 입력해줘!")

            st.markdown("</div>", unsafe_allow_html=True)

# =============================
# VIEW: Projects
# =============================
elif view_mode == "📦 프로젝트":
    st.markdown("## 📦 프로젝트 진행 상황")
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    with st.expander("➕ 새 프로젝트 추가", expanded=True):
        c1, c2, c3, c4 = st.columns([2, 1.1, 1.1, 2])
        with c1:
            pname = st.text_input("프로젝트 이름", placeholder="예: 지역사회간호 팀플 / 연구계획서 / 공모전")
        with c2:
            pstatus = st.selectbox("상태", ["진행중", "대기", "완료"])
        with c3:
            pdue = st.date_input("마감(선택)", value=None)
        with c4:
            pnotes = st.text_input("메모(선택)", placeholder="예: 역할 분담/다음 할 일/링크")
        pprog = st.slider("진행률(%)", 0, 100, 0)
        if st.button("추가 🚀", type="primary"):
            if pname.strip():
                add_project(pname.strip(), pdue, pstatus, int(pprog), pnotes.strip())
                st.success("프로젝트 추가 완료!")
                st.rerun()
            else:
                st.warning("프로젝트 이름을 입력해줘!")

    df = fetch_projects()
    if df.empty:
        st.info("아직 프로젝트가 없어요. 위에서 하나 추가해봐! ✨")
    else:
        # Filter
        f1, f2 = st.columns([1, 3])
        with f1:
            status_filter = st.multiselect("필터(상태)", ["진행중", "대기", "완료"], default=["진행중","대기","완료"])
        with f2:
            search = st.text_input("검색", placeholder="프로젝트 이름/메모 키워드")
        view = df[df["status"].isin(status_filter)].copy()
        if search.strip():
            s = search.strip().lower()
            view = view[
                view["name"].str.lower().str.contains(s) |
                view["notes"].fillna("").str.lower().str.contains(s)
            ]

        st.caption(f"표시 중: {len(view)}개")
        for _, r in view.iterrows():
            pid = int(r["id"])
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            top = st.columns([3, 1.1, 1.2, 0.8])
            with top[0]:
                st.markdown(f"### 📌 {r['name']}")
                due = r["due"] if r["due"] else "—"
                st.markdown(f"<span class='pill'>상태: {r['status']}</span> <span class='pill2'>마감: {due}</span>", unsafe_allow_html=True)
            with top[1]:
                st.metric("진행률", f"{int(r['progress'])}%")
            with top[2]:
                st.progress(int(r["progress"]) / 100)
            with top[3]:
                if st.button("🗑️ 삭제", key=f"del_proj_{pid}"):
                    delete_project(pid)
                    st.rerun()

            with st.expander("✏️ 수정하기", expanded=False):
                nstatus = st.selectbox("상태", ["진행중","대기","완료"], index=["진행중","대기","완료"].index(r["status"]), key=f"st_{pid}")
                ndue = st.date_input("마감", value=(date.fromisoformat(r["due"]) if r["due"] else None), key=f"due_{pid}")
                nprog = st.slider("진행률(%)", 0, 100, int(r["progress"]), key=f"prog_{pid}")
                nnotes = st.text_area("메모", value=(r["notes"] or ""), height=110, key=f"note_{pid}")
                if st.button("저장 💾", key=f"save_{pid}", type="primary"):
                    update_project(pid, nstatus, int(nprog), ndue, nnotes)
                    st.success("저장 완료!")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")

# =============================
# VIEW: Diary
# =============================
elif view_mode == "✍️ 오늘의 일기":
    st.markdown("## ✍️ 오늘의 일기/다이어리")
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    d = st.date_input("📅 날짜 선택", value=today, key="diary_day")
    existing = fetch_diary(d)

    mood_opts = ["😄", "🙂", "😐", "🥲", "😤", "😭", "🤩", "😴", "🧘‍♀️"]
    mood = st.selectbox("오늘 기분", mood_opts, index=(mood_opts.index(existing["mood"]) if existing and existing["mood"] in mood_opts else 1))

    title = st.text_input("제목(한 줄)", value=(existing["title"] if existing else ""), placeholder="예: 오늘은 좀 버거웠지만 끝까지 해냈다")
    content = st.text_area("일기", value=(existing["content"] if existing else ""), height=220, placeholder="오늘 있었던 일 / 감정 / 배운 점을 자유롭게 적어봐 ✨")
    gratitude = st.text_input("감사한 일(1~3개)", value=(existing["gratitude"] if existing else ""), placeholder="예: 팀원이 도와줬다, 커피가 맛있었다")
    highlight = st.text_input("오늘의 하이라이트(한 문장)", value=(existing["highlight"] if existing else ""), placeholder="예: 도서관에서 2시간 집중 성공!")

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("저장 💾", type="primary"):
            upsert_diary(d, mood, title, content, gratitude, highlight)
            st.success("저장 완료!")
            st.rerun()
    with c2:
        if existing:
            st.caption(f"마지막 수정: {existing['updated_at']}")
        else:
            st.caption("아직 작성된 일기가 없어요.")
    with c3:
        st.info("팁: 위클리 보드에서 ✍️ 표시로 ‘일기 작성 여부’를 한눈에 볼 수 있어요.")

# =============================
# VIEW: Data / Export
# =============================
elif view_mode == "⚙️ 데이터":
    st.markdown("## ⚙️ 데이터 보기 / 내보내기(샘플)")
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    tdf = fetch_todos_between(ws - timedelta(days=21), we + timedelta(days=21))
    pdf = fetch_projects()

    st.subheader("🧾 Todos (최근 약 6주 범위)")
    st.dataframe(tdf, use_container_width=True, hide_index=True)

    st.subheader("📦 Projects")
    st.dataframe(pdf, use_container_width=True, hide_index=True)

    st.subheader("✍️ Diary")
    conn = get_conn()
    ddf = pd.read_sql_query("SELECT * FROM diary ORDER BY day DESC", conn)
    conn.close()
    st.dataframe(ddf, use_container_width=True, hide_index=True)

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.caption("원하면: CSV 내보내기 버튼, 구글 캘린더 연동, 로그인(계정별 DB 분리)도 붙일 수 있어요.")

