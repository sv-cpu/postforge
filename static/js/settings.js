const saveBtn = document.getElementById('save-settings-btn');
const apiKeyInput = document.getElementById('api-key-input');
const modelSelect = document.getElementById('model-select');

const saveVkBtn = document.getElementById('save-vk-btn');
const vkApiKey = document.getElementById('vk-api-key');
const vkGroupSelect = document.getElementById('vk-group-select');
const vkFetchGroupsBtn = document.getElementById('vk-fetch-groups-btn');
const vkStatus = document.getElementById('vk-status');

saveBtn.addEventListener('click', async () => {
    const api_key = apiKeyInput.value.trim();
    const model = modelSelect.value;

    try {
        const resp = await fetch('/api/settings', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key, model }),
        });

        if (resp.ok) {
            showToast('Настройки сохранены');
        } else {
            const data = await resp.json();
            showToast(data.error || 'Ошибка сохранения');
        }
    } catch {
        showToast('Ошибка сохранения');
    }
});

async function loadVkSettings() {
    try {
        const resp = await fetch('/api/vk/settings');
        if (resp.ok) {
            const data = await resp.json();
            vkApiKey.value = data.api_key || '';
            if (data.selected_group_id) {
                vkStatus.innerHTML = '✅ <span style="color:var(--accent);">Сообщество выбрано</span>';
            } else {
                vkStatus.innerHTML = '❌ <span style="color:var(--text-muted);">Сообщество не выбрано</span>';
            }
        }
    } catch {
        vkStatus.innerHTML = '❌ <span style="color:var(--text-muted);">Ошибка загрузки</span>';
    }
}

vkFetchGroupsBtn.addEventListener('click', async () => {
    const apiKey = vkApiKey.value.trim();
    if (!apiKey) {
        showToast('Введите VK API ключ');
        return;
    }

    vkFetchGroupsBtn.disabled = true;
    vkFetchGroupsBtn.textContent = 'Загрузка...';

    try {
        const resp = await fetch(`/api/vk/groups?api_key=${encodeURIComponent(apiKey)}`);
        if (!resp.ok) {
            const data = await resp.json();
            showToast(data.error || 'Ошибка получения групп');
            return;
        }
        const groups = await resp.json();
        vkGroupSelect.innerHTML = '<option value="">— Выберите сообщество —</option>';
        groups.forEach(g => {
            const opt = document.createElement('option');
            opt.value = g.id;
            opt.textContent = `${g.name} (ID: ${g.id})`;
            vkGroupSelect.appendChild(opt);
        });
        showToast(`Найдено сообществ: ${groups.length}`);
        vkStatus.innerHTML = '✅ <span style="color:var(--accent);">Группы загружены</span>';
    } catch {
        showToast('Ошибка получения групп');
    } finally {
        vkFetchGroupsBtn.disabled = false;
        vkFetchGroupsBtn.textContent = '🔄 Получить';
    }
});

saveVkBtn.addEventListener('click', async () => {
    const api_key = vkApiKey.value.trim();
    const selected_group_id = vkGroupSelect.value;

    if (!api_key) {
        showToast('Введите VK API ключ');
        return;
    }

    try {
        const resp = await fetch('/api/vk/settings', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key, selected_group_id }),
        });

        if (resp.ok) {
            showToast('Настройки VK сохранены');
            loadVkSettings();
        } else {
            const data = await resp.json();
            showToast(data.error || 'Ошибка сохранения VK');
        }
    } catch {
        showToast('Ошибка сохранения VK');
    }
});

loadVkSettings();
