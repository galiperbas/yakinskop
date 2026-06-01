import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"

# ── Token kullanım takibi ──
_usage_stats = {
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "total_tokens": 0,
    "request_count": 0,
}


def get_usage_stats() -> dict:
    """Kümülatif token kullanım istatistiklerini döndürür."""
    return dict(_usage_stats)

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
    "Sen 'Yakınskop' adlı Türkiye ulusal teleskop altyapısı eğitim ve bilim iletişimi asistanısın. "
    "Aşırı abartılı, çocuksu veya karikatürize benzetmelerden kesinlikle kaçın. "
    "Son derece profesyonel, gerçekçi ve elit bir bilimsel ton koru. "
    "Teknik parametreleri birinci ilkeler fiziğiyle açıkla "
    "(örn. bir CCD'nin neden karanlık akım/termal gürültüyle savaşmak için -60°C'ye soğutulması gerektiği). "
    "Uzamsal veya optik kapasiteleri net, ilişkilendirilebilir insan mühendisliği boyutlarıyla temelle. "
    "Cevaplarını her zaman Türkçe ver. "
    "Cevabında teknik bir parametre geçtiğinde (ör. okuma gürültüsü, Strehl oranı, kuantum etkinliği, "
    "kara akım, f oranı vb.) o parametrenin fiziksel mekanizmasını kısaca 1-2 cümleyle açıkla."
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


COMPARE_SYSTEM = (
    BASE_SYSTEM + "\n\n"
    "Senden teleskopları karşılaştırman isteniyor. "
    "KISA ve NET cevap ver. Gereksiz uzatma. "
    "Kullanıcı belirli bir odak belirtmişse SADECE o konuya odaklan. "
    "Belirtmemişse kısa bir özet tablo yap. "
    "Maksimum 300 kelime ile yanıt ver."
)


def compare_telescopes(telescope_keys: list[str], persona: str, focus: str = "") -> dict:
    """Seçilen teleskopları karşılaştıran Gemini API çağrısı yapar."""
    context = load_telescope_context(telescope_keys)
    system = COMPARE_SYSTEM + "\n\n" + persona
    if context.strip():
        system += (
            "\n\nAşağıda karşılaştırılacak teleskoplara ait teknik veriler bulunmaktadır:\n\n"
            + context
        )
    names = ", ".join(telescope_keys)
    if focus.strip():
        user_msg = f"{names} teleskoplarını şu odakta karşılaştır: {focus}"
    else:
        user_msg = f"{names} teleskoplarını kısaca karşılaştır."
    return chat([{"role": "user", "content": user_msg}], system)


FIRSTPRINCIPLES_SYSTEM = (
    BASE_SYSTEM + "\n\n"
    "Kullanıcı sana bir teknik astronomi/enstrümantasyon parametresi veriyor. "
    "Bu parametrenin arkasındaki FIZIKSEL MEKANIZMAYI birinci ilkelerden açıkla. "
    "Yapı şu olsun:\n"
    "1) **Ne?** — Parametrenin kısa tanımı (1-2 cümle)\n"
    "2) **Neden Önemli?** — Bu değer neden teleskop performansını etkiler (2-3 cümle)\n"
    "3) **Fiziksel Mekanizma** — Arkasındaki fizik (termodinamik, optik, kuantum etkinliği vb.)\n"
    "4) **Somut Örnek** — Verilen teleskoptan veya gerçek bir gözlemden somut bir örnek\n"
    "Maksimum 250 kelime. Cevaplarını Türkçe ver."
)


def explain_term(term: str, persona: str, telescope_key: str = "") -> dict:
    """Teknik bir terimi birinci ilkelerden açıklayan Gemini API çağrısı yapar."""
    system = FIRSTPRINCIPLES_SYSTEM + "\n\n" + persona
    if telescope_key:
        context = load_telescope_context([telescope_key])
        if context.strip():
            system += "\n\nİlgili teleskop verisi:\n\n" + context
    user_msg = f"Şu teknik parametreyi birinci ilkeler fiziğiyle açıkla: {term}"
    return chat([{"role": "user", "content": user_msg}], system)


def chat(messages: list[dict], system_prompt: str) -> dict:
    """Gemini API'ye mesaj geçmişini gönderip cevap ve token kullanım bilgisini döndürür."""
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(genai.types.Content(
            role=role,
            parts=[genai.types.Part.from_text(text=msg["content"])],
        ))

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3,
                    max_output_tokens=16384,
                ),
            )

            # Token kullanım bilgilerini çıkar
            usage = {"input": 0, "output": 0, "total": 0}
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                meta = response.usage_metadata
                usage["input"] = getattr(meta, "prompt_token_count", 0) or 0
                usage["output"] = getattr(meta, "candidates_token_count", 0) or 0
                usage["total"] = getattr(meta, "total_token_count", 0) or 0

            # Kümülatif istatistikleri güncelle
            _usage_stats["total_input_tokens"] += usage["input"]
            _usage_stats["total_output_tokens"] += usage["output"]
            _usage_stats["total_tokens"] += usage["total"]
            _usage_stats["request_count"] += 1

            return {"text": response.text, "usage": usage}
        except ServerError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return {
                "text": "Gemini API şu anda yoğun talep nedeniyle yanıt veremiyor. Lütfen birkaç dakika sonra tekrar deneyin.",
                "usage": {"input": 0, "output": 0, "total": 0},
            }
