import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"

DATA_DIR = Path(__file__).parent / "data"

TELESCOPE_MAP = {
    "RTT150": "antalya/rtt150.md",
    "TUG100": "antalya/tug100.md",
    "TUG060": "antalya/tug060.md",
    "DAG400": "erzurum/dag400.md",
    "ATA050": "erzurum/ata050.md",
    "DAGTPS": "erzurum/dagtps.md",
}

PERSONAS = {
    "child": (
        "Sen elit düzeyde, ilham veren bir bilim iletişimcisisin. "
        "Çocuk dili KULLANMA. Yapısal konfigürasyonları kesin fiziksel ölçeklendirme ile açıkla "
        "(örneğin, 4 metrelik bir aynayı bir oda boyutuyla karşılaştır). "
        "Teleskobun 'ne' gözlemlediğine ve renklerin/filtrelerin fiziksel anlamına yoğun olarak odaklan. "
        "Cevaplarını Türkçe ver."
    ),
    "general": (
        "Sen uzman bir gözlemevi rehberisin. "
        "Altyapının ulusal ve uluslararası mühendislik önemine odaklan. "
        "Soyut sayısal parametreleri mantıksal operasyonel performans metriklerine çevir. "
        "Cevaplarını Türkçe ver."
    ),
    "academic": (
        "Sen kıdemli bir astrofizik/mühendislik araştırma arkadaşısın. "
        "Kesin akademik terminolojiyi koru (örn. uzaysal ışık modülatörleri, kuantum etkinliği, "
        "dalga cephesi hataları, Strehl oranları). Sistem entegrasyonuna, çoklu dalga boyu "
        "ödünleşimlerine ve birinci ilkeler enstrümantasyon mantığına odaklan. "
        "Cevaplarını Türkçe ver."
    ),
}

BASE_SYSTEM = (
    "Sen 'Yakınsop' adlı Türkiye ulusal teleskop altyapısı eğitim ve bilim iletişimi asistanısın. "
    "Aşırı abartılı, çocuksu veya karikatürize benzetmelerden kesinlikle kaçın. "
    "Son derece profesyonel, gerçekçi ve elit bir bilimsel ton koru. "
    "Teknik parametreleri birinci ilkeler fiziğiyle açıkla "
    "(örn. bir CCD'nin neden karanlık akım/termal gürültüyle savaşmak için -60°C'ye soğutulması gerektiği). "
    "Uzamsal veya optik kapasiteleri net, ilişkilendirilebilir insan mühendisliği boyutlarıyla temelle. "
    "Cevaplarını her zaman Türkçe ver."
)


def load_telescope_context(telescope_keys: list[str]) -> str:
    """Seçilen teleskopların .md dosyalarını okuyup birleştirilmiş context döndürür."""
    parts = []
    for key in telescope_keys:
        rel_path = TELESCOPE_MAP.get(key)
        if not rel_path:
            continue
        full_path = DATA_DIR / rel_path
        if full_path.exists():
            parts.append(full_path.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(parts)


def resolve_persona(age_group: str, education: str, background: str) -> str:
    """Kullanıcı profil alanlarına göre uygun persona system prompt'unu döndürür."""
    if age_group in ("7-12", "13-18") and education == "İlkokul/Ortaokul":
        return PERSONAS["child"]
    if education in ("Üniversite Öğrencisi/Mezun", "Eğitimci/Araştırmacı") or background == "Teknik/Mühendislik Altyapısı":
        return PERSONAS["academic"]
    return PERSONAS["general"]


def build_system_prompt(persona: str, context: str) -> str:
    """Base system + persona + teleskop context birleştirerek nihai system prompt oluşturur."""
    parts = [BASE_SYSTEM, persona]
    if context.strip():
        parts.append(
            "Aşağıda, kullanıcının sorduğu teleskoplara ait teknik veriler bulunmaktadır. "
            "Cevaplarını bu verilere dayandır:\n\n" + context
        )
    return "\n\n".join(parts)


def chat(messages: list[dict], system_prompt: str) -> str:
    """Gemini API'ye mesaj geçmişini gönderip cevap alır."""
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(genai.types.Content(
            role=role,
            parts=[genai.types.Part.from_text(text=msg["content"])],
        ))

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
            max_output_tokens=4096,
        ),
    )
    return response.text
