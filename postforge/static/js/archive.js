const archiveList = document.getElementById('archive-list');

async function loadArchive() {
    archiveList.innerHTML = '<div class="archive-empty">Загрузка...</div>';
    try {
        const resp = await fetch('/api/archive');
        if (!resp.ok) throw new Error('Ошибка загрузки');
        const posts = await resp.json();

        if (posts.length === 0) {
            archiveList.innerHTML = '<div class="archive-empty">В архиве пока нет сохранённых постов</div>';
            return;
        }

        archiveList.innerHTML = '';
        posts.forEach(p => {
            const date = p.created_at
                ? new Date(p.created_at).toLocaleDateString('ru-RU')
                : '—';

            const toneLabels = { expert: 'Экспертный', friendly: 'Дружелюбный', brief: 'Краткий' };
            const toneLabel = toneLabels[p.tone] || p.tone;

            const div = document.createElement('div');
            div.className = 'archive-item';
            div.innerHTML = `
                <div class="archive-item-header">
                    <span>📅 ${date} &nbsp;|&nbsp; 🎯 ${toneLabel} &nbsp;|&nbsp; 🤖 ${p.model}</span>
                    <span style="color:var(--text-muted);font-size:12px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${p.original_url}</span>
                </div>
                <div class="archive-item-content">${escapeHtml(p.content)}</div>
                <div class="archive-item-actions">
                    <button class="btn btn-secondary btn-sm view-btn" data-id="${p.id}">👁 Просмотр</button>
                    <button class="btn btn-danger btn-sm delete-btn" data-id="${p.id}">🗑 Удалить</button>
                </div>
            `;
            archiveList.appendChild(div);
        });

        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', () => viewPost(parseInt(btn.dataset.id)));
        });
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', () => deletePost(parseInt(btn.dataset.id)));
        });
    } catch (err) {
        archiveList.innerHTML = `<div class="archive-empty">❌ ${err.message}</div>`;
    }
}

function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

async function viewPost(id) {
    try {
        const resp = await fetch('/api/archive');
        const posts = await resp.json();
        const post = posts.find(p => p.id === id);
        if (!post) return;

        document.getElementById('modal-title').textContent = `Пост от ${new Date(post.created_at).toLocaleDateString('ru-RU')}`;
        document.getElementById('modal-text').textContent = post.content;
        document.getElementById('view-modal').classList.add('open');
    } catch {
        showToast('Ошибка загрузки');
    }
}

document.getElementById('modal-close-btn').addEventListener('click', () => {
    document.getElementById('view-modal').classList.remove('open');
});

document.getElementById('view-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
        document.getElementById('view-modal').classList.remove('open');
    }
});

async function deletePost(id) {
    if (!confirm('Удалить этот пост?')) return;
    try {
        const resp = await fetch(`/api/archive/${id}`, { method: 'DELETE' });
        if (resp.ok) {
            showToast('Пост удалён');
            loadArchive();
        } else {
            showToast('Ошибка удаления');
        }
    } catch {
        showToast('Ошибка удаления');
    }
}

loadArchive();
