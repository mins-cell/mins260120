import streamlit as st
from pathlib import Path

# ---------- Page config ----------
st.set_page_config(
    page_title="자기소개 | Streamlit",
    page_icon="👋",
    layout="centered",
)

# ---------- Header ----------
st.title("👋 안녕하세요!")
st.caption("Streamlit로 만든 간단한 자기소개 페이지입니다.")

# ---------- Profile section ----------
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    # 같은 폴더에 profile.jpg(또는 png) 넣으면 자동 표시
    img_path = None
    for name in ["profile.jpg", "profile.png", "me.jpg", "me.png"]:
        p = Path(name)
        if p.exists():
            img_path = p
            break

    if img_path:
        st.image(str(img_path), caption="Profile", use_container_width=True)
    else:
        st.info("📷 사진 파일이 없어서 기본 아바타로 표시할게요. `profile.jpg`를 업로드해 주세요.")
        st.image("https://placehold.co/400x400/png?text=Upload+profile.jpg", use_container_width=True)

with col2:
    st.subheader("간단 인사")
    st.write(
        """
        반갑습니다! 저는 **데이터/연구/교육**에 관심이 많고,  
        Streamlit로 빠르게 아이디어를 제품처럼 만들어보는 걸 좋아해요.  
        
        이 페이지는 제 소개를 아주 간단히 보여주는 데모입니다 🙂
        """
    )

# ---------- Quick info ----------
st.divider()
st.markdown("### 💡 한 줄 소개")
one_liner = st.text_input("한 줄 소개를 입력해보세요", value="안녕하세요, 저는 배움을 즐기는 사람입니다.")

st.markdown("### 📌 연락처/링크")
c1, c2 = st.columns(2)
with c1:
    st.text_input("이메일", value="example@email.com")
with c2:
    st.text_input("링크(예: GitHub/LinkedIn)", value="https://github.com/yourname")

st.divider()

# ---------- Footer ----------
st.caption("© 2026 · Made with Streamlit")
