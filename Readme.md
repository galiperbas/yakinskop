# Yakınsop: Ajan Tabanlı ve Kişiselleştirilmiş Ulusal Teleskop Bilim-Toplum Portalı

**Yakınsop**, Türkiye'deki ulusal teleskop altyapısının teknik verilerini toplumun her kesimine (7'den 77'ye) anlaşılır, kaliteli ve bilimsel doğruluktan ödün vermeden aktarmayı amaçlayan yapay zeka destekli bir interaktif dashboard projesidir.

Proje, kuru ve soyut enstrümantasyon verilerini (okuma gürültüleri, piksel ölçekleri, dalga cephesi hataları vb.) kullanıcının yaş ve eğitim arka planına göre dinamik olarak hikayeleştiren bir **Context-Injection RAG (Retrieval-Augmented Generation)** mimarisine sahiptir.

Yakınsop arayüzünden bir görünüm: Profil tabanlı uyarlanabilir anlatım ve teleskop karşılaştırma paneli.

![Yakınsop Arayüz Görünümü](demo-foto/Ekran%20görüntüsü%202026-05-28%20110634.png)

---
## Kurulum

  Test etmek için adım adım, proje dizini local'e klonlandıktan sonra, proje yolunda çalıştırılması komutlar:

  pip install -r requirements.txt

  Ardından .env dosyasına gerçek API key'ini yaz (https://aistudio.google.com/ adresinden alınmaktadır.):
  GEMINI_API_KEY="senin_gercek_api_keyin"
  
  Sonra çalıştır:
  streamlit run app.py

---
## 🚀 Öne Çıkan Özellikler

* **Persona-Adaptive Mutation (Profil Tabanlı Uyarlanabilir Anlatım):** Kullanıcı onboarding ekranında yaşını ve eğitim durumunu seçer. Sistem prompt katmanı bu verilere göre anlık mutasyona uğrayarak; bir ilkokul öğrencisine yapısal ölçeklerle, bir mühendislik öğrencisine ise doğrudan temel fizik ilkeleriyle (First-Principles) açıklama yapar.
* **Context-Injection RAG:** Büyük ve maliyetli Vector DB/Embedding süreçleri yerine, teleskopların tüm teknik speşlerini içeren statik Markdown dosyalarını Gemini API'nin geniş bağlam penceresine doğrudan "bağlam" olarak enjekte eder. %100 deterministik ve sapmasız (hallucination-free) çalışır.
* **Elit ve Gerçekçi Dil Sınırı:** Anlatımlarda çocuksu, abartılı veya gerçek dışı analojiler kesinlikle kullanılmaz. Tüm açıklamalar akademik kalitede, popüler bilim çizgisine uygun ve fiziksel gerçekliklere dayalıdır.
* **Ekosistem Karşılaştırma Modülü:** Ulusal teleskopların birbirleriyle olan teknik farklarını ve uluslararası gözlemevleri karşısındaki stratejik önemini yapısal olarak analiz eder.

---

## 📂 Proje Dizini Yapısı

```text
Yakınsop/
├── data/                   # Teleskop verilerinin temiz Markdown halleri
│   ├── antalya/
│   │   ├── rtt150.md       # RTT150 teleskop ve odak düzlem verileri
│   │   ├── tug100.md       # TUG T100 teleskop verileri
│   │   └── tug060.md       # TUG T060 teleskop ve Andor iKon-L 936 kamera speşleri
│   └── erzurum/
│       ├── ata050.md       # ATA050 robotik teleskop verileri
│       ├── dag400.md       # DAG400 teleskop, KORAY, DIRAC, TROIA, PLACID, DAGOS özellikleri
│       └── dagtps.md       # DAG TPS donanım verileri
├── app.py                  # Streamlit UI (Profil ekranı, Karşılaştırma Paneli, Chat arayüzü)
├── rag_engine.py           # Gemini API (google-genai SDK) entegrasyonu ve Context yükleyici logic
├── mimari.json             # Projenin tüm fonksiyonel ve yapısal master konfigürasyonu
└── requirements.txt        # Bağımlılıklar (streamlit, google-genai, python-dotenv)