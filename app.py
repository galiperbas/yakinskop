import streamlit as st
from rag_engine import (
    TELESCOPE_MAP,
    load_telescope_context,
    resolve_persona,
    build_system_prompt,
    compare_telescopes,
    explain_term,
    chat,
)

# ---------- Sayfa Ayarları ----------
st.set_page_config(
    page_title="Yakınskop",
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

    profile_ready = age_group and education and background
    if st.button("Profili Kaydet", disabled=not profile_ready, use_container_width=True):
        st.session_state.age_group = age_group
        st.session_state.education = education
        st.session_state.background = background
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
st.title("🔭 Yakınskop")
st.caption("Türkiye Ulusal Teleskop Altyapısı — Etkileşimli Bilim İletişimi Asistanı")

if not st.session_state.profile_set:
    st.info("Başlamak için lütfen soldaki panelden profil bilgilerinizi doldurun ve kaydedin.")
    st.stop()

# ---------- Navigasyon Tabları ----------
tab_chat, tab_compare, tab_explain = st.tabs(["💬 Sohbet", "⚖️ Karşılaştırma", "🔬 Teknik Terim Açıklama"])

# ==================== TAB 1: SOHBET ====================
with tab_chat:
    st.subheader("Teleskop Sohbet Asistanı")

    # Teleskop seçimi (sohbet için)
    chat_telescopes = st.multiselect(
        "Sohbet için teleskop seçin",
        options=list(TELESCOPE_MAP.keys()),
        default=list(TELESCOPE_MAP.keys()),
        key="chat_telescopes",
    )

    # Sohbet geçmişini göster
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Kullanıcı girişi
    if user_input := st.chat_input("Teleskoplar hakkında bir soru sorun..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        context = load_telescope_context(chat_telescopes)
        persona = resolve_persona(
            st.session_state.age_group,
            st.session_state.education,
            st.session_state.background,
        )
        system_prompt = build_system_prompt(persona, context)

        with st.chat_message("assistant"):
            with st.spinner("Düşünüyorum..."):
                response = chat(st.session_state.messages, system_prompt)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

# ==================== TAB 2: KARŞILAŞTIRMA ====================
with tab_compare:
    st.subheader("Ekosistem Karşılaştırma Modülü")
    st.markdown("İki veya daha fazla ulusal teleskobu seçerek teknik parametrelerini "
                "birinci ilkeler fiziğiyle karşılaştırın.")

    all_keys = list(TELESCOPE_MAP.keys())

    col1, col2 = st.columns(2)
    with col1:
        tel_a = st.selectbox("Teleskop A", options=all_keys, index=0, key="cmp_a")
    with col2:
        remaining = [k for k in all_keys if k != tel_a]
        tel_b = st.selectbox("Teleskop B", options=remaining, index=0, key="cmp_b")

    extra = st.multiselect(
        "Ek teleskop ekle (opsiyonel)",
        options=[k for k in all_keys if k not in (tel_a, tel_b)],
        key="cmp_extra",
    )

    compare_keys = [tel_a, tel_b] + extra

    focus = st.text_input(
        "Karşılaştırma odağı (opsiyonel)",
        placeholder="Örn: CCD performansı, gözlem bandı farkları, ayna çapı etkisi...",
        key="cmp_focus",
    )

    if st.button("Karşılaştır", use_container_width=True, type="primary"):
        persona = resolve_persona(
            st.session_state.age_group,
            st.session_state.education,
            st.session_state.background,
        )
        with st.spinner("Teleskoplar karşılaştırılıyor..."):
            result = compare_telescopes(compare_keys, persona, focus)
        st.markdown(result)

# ==================== TAB 3: TEKNİK TERİM AÇIKLAMA ====================
with tab_explain:
    st.subheader("Birinci İlkeler Teknik Açıklama")
    st.markdown("Bir teknik astronomi/enstrümantasyon parametresi girin, "
                "arkasındaki fiziksel mekanizmayı birinci ilkelerden öğrenin.")

    term = st.text_input(
        "Teknik terim veya parametre",
        placeholder="Örn: Okuma Gürültüsü 6.9 e⁻ rms, Strehl Oranı %94, f/7.7, Kuantum Etkinliği...",
        key="explain_term",
    )

    explain_telescope = st.selectbox(
        "Bağlam teleskobu (opsiyonel — somut örnek için)",
        options=["Genel"] + list(TELESCOPE_MAP.keys()),
        index=0,
        key="explain_tel",
    )

    if st.button("Açıkla", use_container_width=True, type="primary", disabled=not term):
        persona = resolve_persona(
            st.session_state.age_group,
            st.session_state.education,
            st.session_state.background,
        )
        tel_key = explain_telescope if explain_telescope != "Genel" else ""
        with st.spinner("Fiziksel mekanizma açıklanıyor..."):
            result = explain_term(term, persona, tel_key)
        st.markdown(result)
