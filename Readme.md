# Yakınskop

**Yakınskop: Türkiye Ulusal Gözlemevleri Teleskoplarını Yakından ve Daha Detaylı Tanıtan Chatbot Arayüzü**

[Türkiye Ulusal Gözlemevleri](https://trgozlemevleri.gov.tr/) sitesinde yer alan altı teleskop sayfasındaki teknik parametreleri (okuma gürültüsü, Strehl oranı, dalga cephesi hatası vb.) kullanıcının yaş ve eğitim profiline göre dinamik olarak açıklayan bir **Context-Injection RAG** (Retrieval-Augmented Generation) chatbot prototipidir.

![Yakınskop Arayüz Görünümü](demo-foto/Ekran%20görüntüsü%202026-05-28%20110634.png)

---

## Özellikler

| Özellik | Açıklama |
|---|---|
| **Profil Tabanlı Anlatım** | Kullanıcı yaşını ve eğitim düzeyini seçer; sistem üç kademe (çocuk, genel, akademik) arasında otomatik geçiş yapar. |
| **Context-Injection RAG** | Teleskop teknik verilerini yapılandırılmış Markdown dosyalarından okuyarak Gemini API'nin geniş bağlam penceresine doğrudan enjekte eder. |
| **Üç Etkileşim Modu** | Sohbet, teleskop karşılaştırma ve birinci ilkeler (first-principles) terim açıklama modülleri. |
| **Token Kullanım Takibi** | Her API çağrısındaki giriş/çıkış token sayısı ve maliyet canlı olarak izlenebilir. |
| **Metin Seçim Entegrasyonu** | Sayfadaki herhangi bir teknik terimi seçip tek tıkla chatbot'a sorabilme. |

---

## Teleskoplar

| Yerleşke | Teleskop | Ayna Çapı |
|---|---|---|
| Erzurum — DAG | DAG400 | 4,0 m |
| Erzurum — DAG | ATA050 | 0,5 m |
| Erzurum — DAG | DAGTPS | 0,3 m |
| Antalya — TUG | RTT150 | 1,5 m |
| Antalya — TUG | TUG100 | 1,0 m |
| Antalya — TUG | TUG060 | 0,6 m |

Veri kaynağı: [trgozlemevleri.gov.tr/teleskoplar](https://trgozlemevleri.gov.tr/teleskoplar)

---

## Kurulum

```bash
git clone https://github.com/galiperbas/yakinskop.git
cd yakinskop
pip install -r requirements.txt
```

`.env` dosyasına [Google AI Studio](https://aistudio.google.com/) üzerinden alınan API anahtarını yazın:

```
GEMINI_API_KEY=senin_api_anahtarin
```

Sunucuyu başlatın:

```bash
python server.py
```

Tarayıcıda `http://localhost:5000` adresine gidin.

---

## Mimari

```
Yakınskop/
├── data/                   # Teleskop verileri (Markdown)
│   ├── antalya/            # RTT150, TUG100, TUG060
│   └── erzurum/            # DAG400, ATA050, DAGTPS
├── server.py               # Flask backend + API rotaları
├── rag_engine.py           # Gemini API entegrasyonu ve Context-Injection RAG motoru
├── templates/
│   └── index.html          # Ana arayüz şablonu
├── static/
│   ├── app.js              # Frontend etkileşim mantığı
│   └── style.css           # Arayüz stilleri
├── .env                    # API anahtarı (git'e dahil değil)
└── requirements.txt        # Python bağımlılıkları
```

---

## Teknolojiler

- **Backend:** Python, Flask
- **LLM:** Google Gemini 2.5 Flash (google-genai SDK)
- **Frontend:** Vanilla HTML/CSS/JS, Marked.js (Markdown render)

---

## Lisans

MIT
