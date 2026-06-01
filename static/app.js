/* ── Yakınskop Frontend ── */

// State
let currentTelescope = null;
let chatMessages = [];
let isLoading = false;

// ── Token kullanım gösterimi ──
function updateTokenUsage(usage) {
    if (usage) {
        // Anlık kullanımı göster (toplam kümülatif değeri /api/usage'dan alınır)
        fetch('/api/usage')
            .then(res => res.json())
            .then(stats => {
                document.getElementById('token-total').textContent = stats.total_tokens.toLocaleString('tr-TR');
                document.getElementById('td-input').textContent = stats.total_input_tokens.toLocaleString('tr-TR');
                document.getElementById('td-output').textContent = stats.total_output_tokens.toLocaleString('tr-TR');
                document.getElementById('td-total').textContent = stats.total_tokens.toLocaleString('tr-TR');
                document.getElementById('td-requests').textContent = stats.request_count.toLocaleString('tr-TR');
            })
            .catch(() => {});
    }
}

function toggleTokenDetail() {
    const detail = document.getElementById('token-detail');
    detail.classList.toggle('visible');
}

// ── Profil helpers ──
function getProfile() {
    return {
        age_group: document.getElementById('profile-age').value,
        education: document.getElementById('profile-edu').value,
        background: 'Meraklı/Yeni Başlayan',
    };
}

// ── Teleskop yükleme ──
async function loadTelescope(slug) {
    // Sidebar aktif durumu
    document.querySelectorAll('.sidebar-item').forEach(el => {
        el.classList.toggle('active', el.dataset.slug === slug);
    });

    const content = document.getElementById('content-area');
    content.innerHTML = '<div class="welcome-page"><p>Yükleniyor...</p></div>';

    try {
        const res = await fetch(`/api/telescope/${slug}`);
        const data = await res.json();
        if (data.error) {
            content.innerHTML = `<div class="welcome-page"><p>Hata: ${data.error}</p></div>`;
            return;
        }
        currentTelescope = data;
        renderTelescopePage(data);
    } catch (e) {
        content.innerHTML = `<div class="welcome-page"><p>Bağlantı hatası</p></div>`;
    }
}

function renderTelescopePage(data) {
    const content = document.getElementById('content-area');
    const meta = data.meta;

    let html = `<div class="telescope-page">`;

    // Header
    html += `
        <div class="telescope-header">
            <h1>${meta.name}</h1>
            <div class="location">${meta.location}</div>
            ${data.mission ? `<div class="mission">${data.mission}</div>` : ''}
            <a class="source-link" href="${meta.link}" target="_blank" rel="noopener">
                Kaynak: trgozlemevleri.gov.tr &rarr;
            </a>
        </div>
    `;

    // Sections
    for (const section of data.sections) {
        html += `<div class="section-block">`;
        html += `<div class="section-title">${section.title}</div>`;

        if (section.description && section.description.trim()) {
            html += `<div class="section-desc">${section.description.trim()}</div>`;
        }

        // Ana bölüm tablosu
        if (section.rows && section.rows.length > 0) {
            html += renderTable(section.rows, false);
        }

        // Alt bölümler
        for (const sub of (section.subsections || [])) {
            html += `<div class="subsection-title">${sub.title}</div>`;
            if (sub.description && sub.description.trim()) {
                html += `<div class="subsection-desc">${sub.description.trim()}</div>`;
            }
            if (sub.rows && sub.rows.length > 0) {
                html += renderTable(sub.rows, true);
            }
        }

        html += `</div>`;
    }

    html += `</div>`;
    content.innerHTML = html;

    // Scroll to top
    content.scrollTop = 0;
}

function renderTable(rows, isSub) {
    let html = `<table class="data-table ${isSub ? 'sub' : ''}">`;
    html += `<thead><tr><th>Parametre</th><th>Değer</th></tr></thead><tbody>`;
    for (const row of rows) {
        const keyHtml = wrapTermsClickable(row.key);
        const valHtml = wrapTermsClickable(row.value);
        html += `<tr><td>${keyHtml}</td><td>${valHtml}</td></tr>`;
    }
    html += `</tbody></table>`;
    return html;
}

// Teknik terimleri tıklanabilir yap
function wrapTermsClickable(text) {
    if (!text) return '';
    // Teknik değerler için: sayı+birim kalıpları
    return text.replace(
        /(\d+[\.,]?\d*\s*(?:mm|µm|nm|m|cm|km|MHz|kHz|Hz|e[⁻-]|mas|"|'|°|⁰|piksel|px|µs|ms|s|saniye|ton|kg|ADU|FPS|Bit|rad))/g,
        '<span class="clickable-term" onclick="askAboutTerm(this, event)">$1</span>'
    );
}

// ── Chat Panel ──
function toggleChatPanel() {
    const panel = document.getElementById('chat-panel');
    const btn = document.getElementById('btn-chat-toggle');
    panel.classList.toggle('hidden');
    btn.classList.toggle('active');
}

function toggleCompareMode() {
    const panel = document.getElementById('chat-panel');
    if (panel.classList.contains('hidden')) {
        panel.classList.remove('hidden');
        document.getElementById('btn-chat-toggle').classList.add('active');
    }
    switchChatTab('compare');
}

function switchChatTab(tab) {
    document.querySelectorAll('.chat-tab').forEach(el => {
        el.classList.toggle('active', el.dataset.tab === tab);
    });
    document.querySelectorAll('.chat-tab-content').forEach(el => {
        el.style.display = 'none';
    });
    const target = document.getElementById(`tab-${tab}`);
    if (target) {
        target.style.display = 'flex';
    }
}

// ── Chat ──
function addChatMessage(role, text) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;

    if (role === 'bot') {
        // Markdown render
        div.innerHTML = marked.parse(text);
    } else {
        div.textContent = text;
    }

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return div;
}

function showTyping() {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = 'typing-indicator';
    div.id = 'typing';
    div.innerHTML = '<span></span><span></span><span></span>';
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById('typing');
    if (el) el.remove();
}

async function sendChat() {
    if (isLoading) return;
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    input.style.height = '38px';

    // Kullanıcı mesajı
    chatMessages.push({ role: 'user', content: text });
    addChatMessage('user', text);

    // Hangi teleskoplar bağlamda
    const telescopes = currentTelescope
        ? [currentTelescope.meta.key]
        : Object.keys({DAG400:1, RTT150:1, TUG100:1, TUG060:1, ATA050:1, DAGTPS:1});

    isLoading = true;
    document.getElementById('chat-send').disabled = true;
    showTyping();

    try {
        const profile = getProfile();
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: chatMessages,
                telescopes: telescopes,
                ...profile,
            }),
        });
        const data = await res.json();
        hideTyping();

        const response = data.response || data.error || 'Yanıt alınamadı.';
        chatMessages.push({ role: 'assistant', content: response });
        addChatMessage('bot', response);
        updateTokenUsage(data.usage);
    } catch (e) {
        hideTyping();
        addChatMessage('bot', 'Bağlantı hatası. Lütfen tekrar deneyin.');
    }

    isLoading = false;
    document.getElementById('chat-send').disabled = false;
}

function clearChat() {
    chatMessages = [];
    const container = document.getElementById('chat-messages');
    container.innerHTML = '<div class="chat-msg system">Sohbet temizlendi. Yeni bir soru sorun.</div>';
}

// ── Karşılaştırma ──
async function runCompare() {
    const checkboxes = document.querySelectorAll('#compare-checkboxes input:checked');
    const selected = Array.from(checkboxes).map(cb => cb.value);
    if (selected.length < 2) {
        document.getElementById('compare-result').innerHTML =
            '<div class="chat-msg system">En az 2 teleskop seçmelisiniz.</div>';
        return;
    }

    const focus = document.getElementById('compare-focus').value.trim();
    const btn = document.getElementById('compare-btn');
    const result = document.getElementById('compare-result');

    btn.disabled = true;
    btn.textContent = 'Karşılaştırılıyor...';
    result.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';

    try {
        const profile = getProfile();
        const res = await fetch('/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ telescopes: selected, focus, ...profile }),
        });
        const data = await res.json();
        result.innerHTML = marked.parse(data.response || data.error || 'Yanıt alınamadı.');
        updateTokenUsage(data.usage);
    } catch (e) {
        result.innerHTML = '<div class="chat-msg system">Bağlantı hatası.</div>';
    }

    btn.disabled = false;
    btn.textContent = 'Karşılaştır';
}

// ── Terim Açıklama ──
async function runExplain() {
    const term = document.getElementById('explain-term').value.trim();
    if (!term) return;

    const telescope = document.getElementById('explain-telescope').value;
    const btn = document.getElementById('explain-btn');
    const result = document.getElementById('explain-result');

    btn.disabled = true;
    btn.textContent = 'Açıklanıyor...';
    result.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';

    try {
        const profile = getProfile();
        const res = await fetch('/api/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ term, telescope, ...profile }),
        });
        const data = await res.json();
        result.innerHTML = marked.parse(data.response || data.error || 'Yanıt alınamadı.');
        updateTokenUsage(data.usage);
    } catch (e) {
        result.innerHTML = '<div class="chat-msg system">Bağlantı hatası.</div>';
    }

    btn.disabled = false;
    btn.textContent = 'Açıkla';
}

// ── Tıklanabilir terim → chatbot ──
function askAboutTerm(el, event) {
    event.stopPropagation();
    const term = el.textContent.trim();

    // Terim açıklama sekmesine yönlendir
    const panel = document.getElementById('chat-panel');
    if (panel.classList.contains('hidden')) {
        panel.classList.remove('hidden');
        document.getElementById('btn-chat-toggle').classList.add('active');
    }
    switchChatTab('explain');
    document.getElementById('explain-term').value = term;

    // Bağlam teleskobunu otomatik seç
    if (currentTelescope) {
        document.getElementById('explain-telescope').value = currentTelescope.meta.key;
    }
}

// ── Text Selection → Chatbot Popup ──
const popup = document.getElementById('selection-popup');
let selectedText = '';

document.addEventListener('mouseup', (e) => {
    // Chat paneli içindeki seçimleri yoksay
    if (e.target.closest('.chat-panel')) return;

    const selection = window.getSelection();
    const text = selection.toString().trim();

    if (text.length > 2 && text.length < 500) {
        selectedText = text;
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        popup.style.left = (rect.left + rect.width / 2 - 60) + 'px';
        popup.style.top = (rect.top - 40 + window.scrollY) + 'px';
        popup.style.display = 'block';
    } else {
        popup.style.display = 'none';
    }
});

document.addEventListener('mousedown', (e) => {
    if (e.target !== popup && !popup.contains(e.target)) {
        popup.style.display = 'none';
    }
});

function sendSelectionToChat() {
    if (!selectedText) return;
    popup.style.display = 'none';

    // Chat panelini aç
    const panel = document.getElementById('chat-panel');
    if (panel.classList.contains('hidden')) {
        panel.classList.remove('hidden');
        document.getElementById('btn-chat-toggle').classList.add('active');
    }

    // Sohbet sekmesine geç ve mesajı gönder
    switchChatTab('chat');
    const input = document.getElementById('chat-input');
    input.value = `"${selectedText}" — bu ne anlama geliyor? Açıklar mısın?`;
    sendChat();

    window.getSelection().removeAllRanges();
}

// ── Textarea auto-resize ──
document.getElementById('chat-input').addEventListener('input', function () {
    this.style.height = '38px';
    this.style.height = Math.min(this.scrollHeight, 100) + 'px';
});
