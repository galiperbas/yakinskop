"""
Yakınskop — Flask Backend
Teleskop tanıtım sayfaları + Chatbot API
"""

import os
import re
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

load_dotenv()

# ── RAG Engine import ──
from rag_engine import (
    TELESCOPE_MAP,
    load_telescope_context,
    resolve_persona,
    build_system_prompt,
    compare_telescopes,
    explain_term,
    chat,
    get_usage_stats,
)

app = Flask(__name__)

DATA_DIR = Path(__file__).parent / "data"

# ── Teleskop metadata ──
TELESCOPES = {
    "dag400": {
        "key": "DAG400",
        "name": "DAG400 Teleskobu",
        "subtitle": "4.0 m — Doğu Anadolu Gözlemevi",
        "location": "Erzurum, Karakaya Tepesi (3170 m)",
        "campus": "erzurum",
        "mirror": "4,0 m",
        "link": "https://trgozlemevleri.gov.tr/teleskoplar/erzurum/dag400",
    },
    "dagtps": {
        "key": "DAGTPS",
        "name": "DAGTPS Teleskop Sistemi",
        "subtitle": "0.3 m — Atmosferik Türbülans Profil Sistemi",
        "location": "Erzurum, Karakaya Tepesi (3170 m)",
        "campus": "erzurum",
        "mirror": "0,3 m",
        "link": "https://trgozlemevleri.gov.tr/teleskoplar/erzurum/dagtps",
    },
    "ata050": {
        "key": "ATA050",
        "name": "ATA050 Teleskobu",
        "subtitle": "0.5 m — Robotik Teleskop",
        "location": "Erzurum, Karakaya Tepesi (3170 m)",
        "campus": "erzurum",
        "mirror": "0,5 m",
        "link": "https://trgozlemevleri.gov.tr/teleskoplar/erzurum/ata050",
    },
    "rtt150": {
        "key": "RTT150",
        "name": "RTT150 Teleskobu",
        "subtitle": "1.5 m — Rus-Türk Teleskobu",
        "location": "Antalya, Saklıkent (TUG)",
        "campus": "antalya",
        "mirror": "1,5 m",
        "link": "https://trgozlemevleri.gov.tr/teleskoplar/antalya/rtt150",
    },
    "tug100": {
        "key": "TUG100",
        "name": "TUG100 Teleskobu",
        "subtitle": "1.0 m — Ritchey-Chrétien",
        "location": "Antalya, Saklıkent (TUG)",
        "campus": "antalya",
        "mirror": "1,0 m",
        "link": "https://trgozlemevleri.gov.tr/teleskoplar/antalya/tug100",
    },
    "tug060": {
        "key": "TUG060",
        "name": "TUG060 Teleskobu",
        "subtitle": "0.6 m — Ritchey-Chrétien",
        "location": "Antalya, Saklıkent (TUG)",
        "campus": "antalya",
        "mirror": "0,6 m",
        "link": "https://trgozlemevleri.gov.tr/teleskoplar/antalya/tug060",
    },
}


def parse_md_to_sections(md_text: str) -> list[dict]:
    """Markdown dosyasını başlık + tablo bölümlerine ayırır."""
    lines = md_text.split("\n")
    sections = []
    current_section = None
    current_subsection = None

    for line in lines:
        # h1 — sayfa başlığı, atla (zaten metadata'da var)
        if line.startswith("# ") and not line.startswith("## "):
            continue
        # Metadata satırları (konum, misyon, fotoğraf, link)
        if line.startswith("* **"):
            continue
        # Ayırıcı
        if line.strip() == "---":
            continue

        # h2 — ana bölüm
        if line.startswith("## "):
            current_section = {
                "title": line[3:].strip(),
                "type": "section",
                "rows": [],
                "subsections": [],
                "description": "",
            }
            sections.append(current_section)
            current_subsection = None
            continue

        # h3 — alt bölüm
        if line.startswith("### "):
            if current_section:
                current_subsection = {
                    "title": line[4:].strip(),
                    "type": "subsection",
                    "rows": [],
                    "description": "",
                }
                current_section["subsections"].append(current_subsection)
            continue

        # h4 — alt-alt bölüm (filtre tabloları vb.)
        if line.startswith("#### "):
            if current_section:
                current_subsection = {
                    "title": line[5:].strip(),
                    "type": "subsection",
                    "rows": [],
                    "description": "",
                }
                current_section["subsections"].append(current_subsection)
            continue

        target = current_subsection if current_subsection else current_section
        if not target:
            continue

        # Liste öğesi → tablo satırı
        stripped = line.strip()
        if stripped.startswith("- "):
            content = stripped[2:]
            if ":" in content:
                key, val = content.split(":", 1)
                target["rows"].append({"key": key.strip(), "value": val.strip()})
            else:
                target["rows"].append({"key": content, "value": ""})
        elif stripped and not stripped.startswith("- "):
            # Açıklama metni
            target["description"] += stripped + " "

    return sections


# ── Sayfa ──
@app.route("/")
def index():
    return render_template("index.html", telescopes=TELESCOPES)


# ── Teleskop veri API'si ──
@app.route("/api/telescope/<slug>")
def telescope_data(slug):
    meta = TELESCOPES.get(slug)
    if not meta:
        return jsonify({"error": "Teleskop bulunamadı"}), 404

    key = meta["key"]
    rel_path = TELESCOPE_MAP.get(key)
    if not rel_path:
        return jsonify({"error": "Veri dosyası bulunamadı"}), 404

    full_path = DATA_DIR / rel_path
    if not full_path.exists():
        return jsonify({"error": "Dosya mevcut değil"}), 404

    md_text = full_path.read_text(encoding="utf-8")

    # Misyon metnini çıkar
    mission = ""
    for line in md_text.split("\n"):
        if line.startswith("* **Misyonu:"):
            mission = line.split(":**", 1)[1].strip() if ":**" in line else ""
            break

    sections = parse_md_to_sections(md_text)

    return jsonify({
        "slug": slug,
        "meta": meta,
        "mission": mission,
        "sections": sections,
    })


# ── Chat API ──
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json
    messages = data.get("messages", [])
    telescope_keys = data.get("telescopes", list(TELESCOPE_MAP.keys()))
    age_group = data.get("age_group", "26+")
    education = data.get("education", "Üniversite Öğrencisi/Mezun")
    background = data.get("background", "Meraklı/Yeni Başlayan")

    context = load_telescope_context(telescope_keys)
    persona = resolve_persona(age_group, education, background)
    system_prompt = build_system_prompt(persona, context)

    result = chat(messages, system_prompt)
    return jsonify({"response": result["text"], "usage": result["usage"]})


# ── Karşılaştırma API ──
@app.route("/api/compare", methods=["POST"])
def api_compare():
    data = request.json
    telescope_keys = data.get("telescopes", [])
    focus = data.get("focus", "")
    age_group = data.get("age_group", "26+")
    education = data.get("education", "Üniversite Öğrencisi/Mezun")
    background = data.get("background", "Meraklı/Yeni Başlayan")

    if len(telescope_keys) < 2:
        return jsonify({"error": "En az 2 teleskop seçmelisiniz"}), 400

    persona = resolve_persona(age_group, education, background)
    result = compare_telescopes(telescope_keys, persona, focus)
    return jsonify({"response": result["text"], "usage": result["usage"]})


# ── Terim Açıklama API ──
@app.route("/api/explain", methods=["POST"])
def api_explain():
    data = request.json
    term = data.get("term", "")
    telescope_key = data.get("telescope", "")
    age_group = data.get("age_group", "26+")
    education = data.get("education", "Üniversite Öğrencisi/Mezun")
    background = data.get("background", "Meraklı/Yeni Başlayan")

    if not term:
        return jsonify({"error": "Terim belirtilmedi"}), 400

    persona = resolve_persona(age_group, education, background)
    result = explain_term(term, persona, telescope_key)
    return jsonify({"response": result["text"], "usage": result["usage"]})


# ── Token Kullanım API ──
@app.route("/api/usage")
def api_usage():
    return jsonify(get_usage_stats())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
