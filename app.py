import streamlit as st
from rag_engine import (
    TELESCOPE_MAP,
    load_telescope_context,
    resolve_persona,
    build_system_prompt,
    chat,
)

# ---------- Sayfa Ayarları ----------
st.set_page_config(
    page_title="Yakınsop",
    page_icon="🔭",
    layout="wide",
)

# ---------- Session State Başlatma ----------
if "profile_set" not in st.session_state:
    st.session_state.profile_set = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Sidebar: Profil Formu ----------
with st.sidebar:
    st.header("Profil Bilgileri")

    age_group = st.selectbox(
        "Yaş Grubu",
        ["7-12", "13-18", "19-25", "26+"],
        index=None,
        placeholder="Seçiniz...",
    )

    education = st.selectbox(
        "Eğitim Durumu",
        ["İlkokul/Ortaokul", "Lise", "Üniversite Öğrencisi/Mezun", "Eğitimci/Araştırmacı"],
        index=None,
        placeholder="Seçiniz...",
    )

    background = st.selectbox(
        "Arka Plan Bilgisi",
        ["Meraklı/Yeni Başlayan", "Uzay Meraklısı", "Teknik/Mühendislik Altyapısı"],
        index=None,
        placeholder="Seçiniz...",
    )

    st.divider()
    st.header("Teleskop Seçimi")

    selected_telescopes = st.multiselect(
        "Sormak istediğiniz teleskopları seçin",
        options=list(TELESCOPE_MAP.keys()),
        default=list(TELESCOPE_MAP.keys()),
    )

    st.divider()

    profile_ready = age_group and education and background
    if st.button("Profili Kaydet & Sohbete Başla", disabled=not profile_ready, use_container_width=True):
        st.session_state.age_group = age_group
        st.session_state.education = education
        st.session_state.background = background
        st.session_state.selected_telescopes = selected_telescopes
        st.session_state.profile_set = True
        st.session_state.messages = []
        st.rerun()

    if st.session_state.profile_set:
        st.success(f"Profil: {st.session_state.age_group} | {st.session_state.education}")
        if st.button("Profili Sıfırla", use_container_width=True):
            st.session_state.profile_set = False
            st.session_state.messages = []
            st.rerun()

# ---------- Ana Alan ----------
st.title("🔭 Yakınsop")
st.caption("Türkiye Ulusal Teleskop Altyapısı — Etkileşimli Bilim İletişimi Asistanı")

if not st.session_state.profile_set:
    st.info("Sohbete başlamak için lütfen soldaki panelden profil bilgilerinizi doldurun ve kaydedin.")
    st.stop()

# ---------- Sohbet Geçmişini Göster ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Kullanıcı Girişi ----------
if user_input := st.chat_input("Teleskoplar hakkında bir soru sorun..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Context ve system prompt oluştur
    context = load_telescope_context(st.session_state.selected_telescopes)
    persona = resolve_persona(
        st.session_state.age_group,
        st.session_state.education,
        st.session_state.background,
    )
    system_prompt = build_system_prompt(persona, context)

    # Gemini API çağrısı
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum..."):
            response = chat(st.session_state.messages, system_prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
