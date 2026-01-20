import streamlit as st

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
PROFILE_IMAGE_URL = (
    "https://d2gfz7wkiigkmv.cloudfront.net/pickin/2/1/2/2vjHjuCOSPmbt7EINhO2-g"
)

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.image(
        PROFILE_IMAGE_URL,
        caption="Profile",
        use_container_width=True,
    )

with col2:
    st.subheader("간단 인사")
    st.write(
        """
        반갑습니다!  
        저는 새로운 기술을 배우고, 연구와 교육에 적용하는 것을 좋아합니다.  
        Streamlit를 활용해 아이디어를 빠르게 구현하는 데 관심이 있습니다 😊
        """
    )

# ---------- One-liner ----------
st.divider()
st.markdown("### 💡 한 줄 소개")
st.text("안녕하세요, 배움을 즐기며 성장하는 사람입니다.")

# ---------- Contact ----------
st.markdown("### 📌 연락처 / 링크")
c1, c2 = st.columns(2)

with c1:
    st.text("📧 example@email.com")

with c2:
    st.text("🔗 https://github.com/yourname")

# ---------- Footer ----------
st.divider()
st.caption("© 2026 · Made with Streamlit")
