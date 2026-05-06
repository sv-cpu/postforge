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

let vkApiKey = '';
let vkSelectedGroupId = '';

async function loadVkSettings() {
    try {
        const resp = await fetch('/api/vk/settings');
        if (resp.ok) {
            const data = await resp.json();
            vkApiKey = data.api_key || '';
            vkSelectedGroupId = data.selected_group_id || '';
        }
    } catch { /* ignore */ }
}

vkPostBtn.addEventListener('click', async () => {
    if (!currentPost) return;
    if (!vkApiKey) {
        showToast('Введите VK API ключ в настройках');
        return;
    }
    if (!vkSelectedGroupId) {
        showToast('Выберите сообщество в настройках');
        return;
    }
    const btn = vkPostBtn;
    btn.disabled = true;
    btn.textContent = 'Публикация...';

    try {
        const resp = await fetch('/api/vk/post', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                owner_id: -Math.abs(vkSelectedGroupId),
                message: currentPost,
                link: currentUrl,
                api_key: vkApiKey,
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
    } finally {
        btn.disabled = false;
        btn.textContent = '📢 ВКонтакте';
    }
});

loadVkSettings();
