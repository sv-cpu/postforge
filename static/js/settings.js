const saveBtn = document.getElementById('save-settings-btn');
const apiKeyInput = document.getElementById('api-key-input');
const modelSelect = document.getElementById('model-select');

const saveVkBtn = document.getElementById('save-vk-btn');
const connectVkBtn = document.getElementById('connect-vk-btn');
const vkClientId = document.getElementById('vk-client-id');
const vkClientSecret = document.getElementById('vk-client-secret');
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

async function loadVkStatus() {
    try {
        const resp = await fetch('/api/vk/groups');
        if (resp.ok) {
            vkStatus.innerHTML = '✅ <span style="color:var(--accent);">ВК подключен</span>';
            connectVkBtn.style.display = 'none';
        } else {
            vkStatus.innerHTML = '❌ <span style="color:var(--text-muted);">ВК не подключен</span>';
            connectVkBtn.style.display = 'inline-flex';
        }
    } catch {
        vkStatus.innerHTML = '❌ <span style="color:var(--text-muted);">ВК не подключен</span>';
        connectVkBtn.style.display = 'inline-flex';
    }
}

saveVkBtn.addEventListener('click', async () => {
    const client_id = vkClientId.value.trim();
    const client_secret = vkClientSecret.value.trim();

    try {
        const resp = await fetch('/api/settings', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vk_client_id: client_id, vk_client_secret: client_secret }),
        });

        if (resp.ok) {
            showToast('Настройки VK сохранены');
            loadVkStatus();
        } else {
            showToast('Ошибка сохранения VK');
        }
    } catch {
        showToast('Ошибка сохранения VK');
    }
});

connectVkBtn.addEventListener('click', async () => {
    try {
        const resp = await fetch('/api/vk/auth-url');
        const data = await resp.json();
        if (data.url) {
            window.open(data.url, '_blank', 'width=600,height=700');
            checkVkCallback();
        } else {
            showToast(data.error || 'Ошибка получения ссылки');
        }
    } catch {
        showToast('Ошибка подключения VK');
    }
});

function checkVkCallback() {
    const check = setInterval(async () => {
        try {
            const resp = await fetch('/api/vk/groups');
            if (resp.ok) {
                clearInterval(check);
                showToast('ВК успешно подключен!');
                loadVkStatus();
            }
        } catch { /* still waiting */ }
    }, 3000);
    setTimeout(() => clearInterval(check), 60000);
}

loadVkStatus();
