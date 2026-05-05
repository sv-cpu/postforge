const saveBtn = document.getElementById('save-settings-btn');
const apiKeyInput = document.getElementById('api-key-input');
const modelSelect = document.getElementById('model-select');

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
