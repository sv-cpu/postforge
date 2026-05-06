const saveBtn = document.getElementById('save-settings-btn');
const apiKeyInput = document.getElementById('api-key-input');
const modelSelect = document.getElementById('model-select');

const saveVkBtn = document.getElementById('save-vk-btn');
const vkApiKey = document.getElementById('vk-api-key');
const vkGroupId = document.getElementById('vk-group-id');
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
            console.log('VK settings loaded:', data);
            vkApiKey.value = data.api_key || '';
            vkGroupId.value = data.selected_group_id || '';
            if (data.selected_group_id) {
                vkStatus.innerHTML = '✅ <span style="color:var(--accent);">Сообщество выбрано</span>';
            } else {
                vkStatus.innerHTML = '❌ <span style="color:var(--text-muted);">Сообщество не выбрано</span>';
            }
        } else {
            const err = await resp.json();
            console.log('VK settings load error:', err);
        }
    } catch (e) {
        console.log('VK settings load exception:', e);
        vkStatus.innerHTML = '❌ <span style="color:var(--text-muted);">Ошибка загрузки</span>';
    }
}

saveVkBtn.addEventListener('click', async () => {
    const api_key = vkApiKey.value.trim();
    const selected_group_id = vkGroupId.value.trim();

    console.log('Save VK clicked:', { api_key, selected_group_id });

    if (!api_key) {
        showToast('Введите VK API ключ');
        return;
    }
    if (!selected_group_id) {
        showToast('Введите ID сообщества');
        return;
    }

    try {
        const payload = { api_key: api_key, selected_group_id: selected_group_id };
        console.log('Sending payload:', payload);
        const resp = await fetch('/api/vk/settings', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        console.log('Response status:', resp.status);
        const respData = await resp.json();
        console.log('Response body:', respData);

        if (resp.ok) {
            showToast('Настройки VK сохранены');
            loadVkSettings();
        } else {
            showToast(respData.error || 'Ошибка сохранения VK');
        }
    } catch (e) {
        console.error('Save VK error:', e);
        showToast('Ошибка сохранения VK: ' + e.message);
    }
});

loadVkSettings();
