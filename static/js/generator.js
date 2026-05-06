const urlInput = document.getElementById('url-input');
const generateBtn = document.getElementById('generate-btn');
const postContent = document.getElementById('post-content');
const postActions = document.getElementById('post-actions');
const copyBtn = document.getElementById('copy-btn');
const shareBtn = document.getElementById('share-btn');
const saveBtn = document.getElementById('save-btn');

let currentPost = '';
let currentUrl = '';
let currentTone = 'friendly';

document.querySelectorAll('input[name="tone"]').forEach(el => {
    el.addEventListener('change', () => { currentTone = el.value; });
});

generateBtn.addEventListener('click', generate);

urlInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') generate();
});

async function generate() {
    const url = urlInput.value.trim();
    if (!url) {
        showToast('Введите ссылку');
        return;
    }

    const tone = document.querySelector('input[name="tone"]:checked')?.value || 'friendly';
    const model = document.getElementById('model-select').value;

    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner"></span> Генерация...';
    postContent.className = 'post-content';
    postContent.textContent = 'Парсинг страницы и генерация поста...';
    postActions.style.display = 'none';

    try {
        const resp = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, tone, model }),
        });

        const data = await resp.json();

        if (!resp.ok) {
            throw new Error(data.error || 'Ошибка сервера');
        }

        currentPost = data.content;
        currentUrl = url;
        currentTone = tone;

        postContent.className = 'post-content';
        postContent.textContent = currentPost;
        postActions.style.display = 'flex';
    } catch (err) {
        postContent.className = 'post-content empty';
        postContent.textContent = '❌ ' + err.message;
        postActions.style.display = 'none';
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '🚀 Сгенерировать';
    }
}

copyBtn.addEventListener('click', async () => {
    if (!currentPost) return;
    try {
        await navigator.clipboard.writeText(currentPost);
        showToast('Скопировано');
    } catch {
        showToast('Ошибка копирования');
    }
});

shareBtn.addEventListener('click', async () => {
    if (!currentPost) return;
    if (navigator.share) {
        try {
            await navigator.share({ text: currentPost });
        } catch { /* user cancelled */ }
    } else {
        await navigator.clipboard.writeText(currentPost);
        showToast('Текст скопирован для отправки');
    }
});

saveBtn.addEventListener('click', async () => {
    if (!currentPost) return;
    const model = document.getElementById('model-select').value;
    try {
        const resp = await fetch('/api/archive', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                original_url: currentUrl,
                tone: currentTone,
                model: model,
                content: currentPost,
            }),
        });
        if (resp.ok) {
            showToast('Пост сохранён в архиве');
        } else {
            showToast('Ошибка сохранения');
        }
    } catch {
        showToast('Ошибка сохранения');
    }
});

const vkPostBtn = document.getElementById('vk-post-btn');

vkPostBtn.addEventListener('click', async () => {
    if (!currentPost) return;
    try {
        const resp = await fetch('/api/vk/groups');
        if (!resp.ok) {
            const data = await resp.json();
            showToast(data.error || 'ВК не подключен');
            return;
        }
        const groups = await resp.json();
        if (!groups.length) {
            showToast('Нет доступных сообществ');
            return;
        }
        showVkGroupSelect(groups);
    } catch {
        showToast('Ошибка получения групп');
    }
});

function showVkGroupSelect(groups) {
    let html = '<div class="modal-overlay open" id="vk-modal">';
    html += '<div class="modal-content">';
    html += '<h3>Выберите сообщество</h3>';
    html += '<select id="vk-group-select" class="form-select" style="margin:12px 0;">';
    groups.forEach(g => {
        html += `<option value="${g.id}">${g.name} (ID: ${g.id})</option>`;
    });
    html += '</select>';
    html += '<div class="btn-group">';
    html += '<button id="vk-post-confirm" class="btn btn-primary btn-sm">Опубликовать</button>';
    html += '<button id="vk-modal-close" class="btn btn-secondary btn-sm">Отмена</button>';
    html += '</div></div></div>';

    document.body.insertAdjacentHTML('beforeend', html);

    document.getElementById('vk-post-confirm').addEventListener('click', async () => {
        const ownerId = document.getElementById('vk-group-select').value;
        const btn = document.getElementById('vk-post-confirm');
        btn.disabled = true;
        btn.textContent = 'Публикация...';

        try {
            const resp = await fetch('/api/vk/post', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    owner_id: -Math.abs(ownerId),
                    message: currentPost,
                    link: currentUrl,
                }),
            });
            if (resp.ok) {
                showToast('Опубликовано в ВК!');
            } else {
                const data = await resp.json();
                showToast(data.error || 'Ошибка публикации');
            }
        } catch {
            showToast('Ошибка публикации');
        }
        document.getElementById('vk-modal').remove();
    });

    document.getElementById('vk-modal-close').addEventListener('click', () => {
        document.getElementById('vk-modal').remove();
    });

    document.getElementById('vk-modal').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) {
            document.getElementById('vk-modal').remove();
        }
    });
}
