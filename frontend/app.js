const API_BASE = 'http://127.0.0.1:5000/api';
const AUTH_BASE = 'http://127.0.0.1:5000/api/auth';


function saveTokens(data) {
  localStorage.setItem('access', data.access_token);
  localStorage.setItem('refresh', data.refresh_token);
}

function getAccessToken() {
  return localStorage.getItem('access');
}

function getRefreshToken() {
  return localStorage.getItem('refresh');
}

function clearTokens() {
  localStorage.removeItem('access');
  localStorage.removeItem('refresh');
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${getAccessToken()}`,
  };
}

function refreshHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${getRefreshToken()}`,
  };
}

/* ---------- TOKEN REFRESH ---------- */

async function refreshAccessToken() {
  try {
    const res = await fetch(`${AUTH_BASE}/refresh`, {
      method: 'POST',
      headers: refreshHeaders(),
    });

    if (!res.ok) {
      clearTokens();
      window.location = 'index.html';
      return false;
    }

    const data = await res.json();
    localStorage.setItem('access', data.access_token);
    return true;
  } catch (err) {
    clearTokens();
    window.location = 'index.html';
    return false;
  }
}

async function fetchWithAuth(url, options = {}) {
  options.headers = authHeaders();
  let res = await fetch(url, options);

  // If unauthorized, try to refresh token
  if (res.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      options.headers = authHeaders();
      res = await fetch(url, options);
    }
  }

  return res;
}

/* ---------- UI HELPERS ---------- */

function showError(elementId, message) {
  const el = document.getElementById(elementId);
  if (el) {
    el.innerText = message;
    el.classList.add('visible');
  }
}

function clearError(elementId) {
  const el = document.getElementById(elementId);
  if (el) {
    el.innerText = '';
    el.classList.remove('visible');
  }
}

function showLoading(buttonId, isLoading) {
  const btn = document.getElementById(buttonId);
  if (btn) {
    btn.disabled = isLoading;
    btn.classList.toggle('loading', isLoading);
  }
}

function setLoadingState(containerId, isLoading) {
  const container = document.getElementById(containerId);
  if (container) {
    container.classList.toggle('loading', isLoading);
  }
}

/* ---------- AUTH ---------- */

async function login() {
  clearError('auth-error');
  showLoading('login-btn', true);

  try {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    if (!email || !password) {
      throw 'Please fill in all fields';
    }

    const res = await fetch(`${AUTH_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();
    if (!res.ok) throw data.error || 'Login failed';

    saveTokens(data);
    window.location = 'tasks.html';
  } catch (err) {
    showError('auth-error', err);
  } finally {
    showLoading('login-btn', false);
  }
}

async function register() {
  clearError('auth-error');
  showLoading('register-btn', true);

  try {
    const name = document.getElementById('register-name').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password1 = document.getElementById('register-password1').value;
    const password2 = document.getElementById('register-password2').value;

    if (!name || !email || !password1 || !password2) {
      throw 'Please fill in all fields';
    }

    if (password1 !== password2) {
      throw 'Passwords do not match';
    }

    const res = await fetch(`${AUTH_BASE}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password1, password2 }),
    });

    const data = await res.json();
    if (!res.ok) throw data.error || 'Registration failed';

    saveTokens(data);
    window.location = 'tasks.html';
  } catch (err) {
    showError('auth-error', err);
  } finally {
    showLoading('register-btn', false);
  }
}

/* ---------- TASKS ---------- */

async function loadTasks() {
  setLoadingState('task-list', true);
  clearError('task-error');

  try {
    const res = await fetchWithAuth(`${API_BASE}/tasks`);
    const data = await res.json();

    if (!res.ok) throw data.error || 'Failed to load tasks';

    const list = document.getElementById('task-list');
    list.innerHTML = '';

    if (data.tasks.length === 0) {
      list.innerHTML = '<li class="no-tasks">No tasks yet. Create one above!</li>';
    } else {
      data.tasks.forEach(renderTask);
    }
  } catch (err) {
    showError('task-error', err);
  } finally {
    setLoadingState('task-list', false);
  }
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function renderTask(task) {
  const li = document.createElement('li');
  li.className = `task status-${task.status}`;
  li.id = `task-${task.id}`;

  li.innerHTML = `
    <div class="task-content">
      <span class="task-title">${escapeHtml(task.title)}</span>
      ${task.description ? `<span class="task-description">${escapeHtml(task.description)}</span>` : ''}
      <span class="task-date">Created: ${formatDate(task.created_at)}</span>
    </div>
    <div class="task-actions">
      <select onchange="updateTaskStatus(${task.id}, this.value)" class="status-select">
        <option value="pending" ${task.status === 'pending' ? 'selected' : ''}>Pending</option>
        <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
        <option value="done" ${task.status === 'done' ? 'selected' : ''}>Done</option>
      </select>
      <button class="edit-btn" onclick='openEditModal(${JSON.stringify(task).replace(/'/g, "&#39;")})' title="Edit task">✎</button>
      <button class="delete-btn" onclick="deleteTask(${task.id})" title="Delete task">✕</button>
    </div>
  `;

  document.getElementById('task-list').appendChild(li);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

async function createTask() {
  clearError('task-error');
  showLoading('create-task-btn', true);

  try {
    const titleInput = document.getElementById('task-title');
    const descInput = document.getElementById('task-description');
    const title = titleInput.value.trim();
    const description = descInput.value.trim();

    if (!title) {
      throw 'Task title is required';
    }

    const res = await fetchWithAuth(`${API_BASE}/tasks`, {
      method: 'POST',
      body: JSON.stringify({ title, description }),
    });

    const data = await res.json();
    if (!res.ok) throw data.error || 'Failed to create task';

    // Clear form
    titleInput.value = '';
    descInput.value = '';

    loadTasks();
  } catch (err) {
    showError('task-error', err);
  } finally {
    showLoading('create-task-btn', false);
  }
}

async function updateTaskStatus(id, status) {
  clearError('task-error');

  const taskEl = document.getElementById(`task-${id}`);
  if (taskEl) taskEl.classList.add('updating');

  try {
    const res = await fetchWithAuth(`${API_BASE}/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });

    if (!res.ok) {
      const data = await res.json();
      throw data.error || 'Failed to update task';
    }

    // Update status class
    if (taskEl) {
      taskEl.className = `task status-${status}`;
    }
  } catch (err) {
    showError('task-error', err);
    loadTasks(); // Reload to restore correct state
  } finally {
    if (taskEl) taskEl.classList.remove('updating');
  }
}

/* ---------- EDIT MODAL ---------- */

let currentEditTaskId = null;

function openEditModal(task) {
  currentEditTaskId = task.id;
  document.getElementById('edit-task-title').value = task.title;
  document.getElementById('edit-task-description').value = task.description || '';
  document.getElementById('edit-task-status').value = task.status;
  document.getElementById('edit-modal').classList.add('open');
  document.getElementById('edit-task-title').focus();
}

function closeEditModal() {
  currentEditTaskId = null;
  document.getElementById('edit-modal').classList.remove('open');
  clearError('edit-error');
}

async function saveTaskEdit() {
  if (!currentEditTaskId) return;

  clearError('edit-error');
  showLoading('save-edit-btn', true);

  try {
    const title = document.getElementById('edit-task-title').value.trim();
    const description = document.getElementById('edit-task-description').value.trim();
    const status = document.getElementById('edit-task-status').value;

    if (!title) {
      throw 'Task title is required';
    }

    const res = await fetchWithAuth(`${API_BASE}/tasks/${currentEditTaskId}`, {
      method: 'PUT',
      body: JSON.stringify({ title, description, status }),
    });

    const data = await res.json();
    if (!res.ok) throw data.error || 'Failed to update task';

    closeEditModal();
    loadTasks();
  } catch (err) {
    showError('edit-error', err);
  } finally {
    showLoading('save-edit-btn', false);
  }
}

// Close modal on escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeEditModal();
  }
});

async function deleteTask(id) {
  if (!confirm('Are you sure you want to delete this task?')) return;

  clearError('task-error');

  const taskEl = document.getElementById(`task-${id}`);
  if (taskEl) taskEl.classList.add('deleting');

  try {
    const res = await fetchWithAuth(`${API_BASE}/tasks/${id}`, {
      method: 'DELETE',
    });

    if (!res.ok && res.status !== 204) {
      const data = await res.json();
      throw data.error || 'Failed to delete task';
    }

    loadTasks();
  } catch (err) {
    showError('task-error', err);
    if (taskEl) taskEl.classList.remove('deleting');
  }
}

async function logout() {
  showLoading('logout-btn', true);

  try {
    // Call logout API
    await fetch(`${AUTH_BASE}/logout`, {
      method: 'POST',
      headers: refreshHeaders(),
    });
  } catch (err) {
    // Ignore errors on logout
  } finally {
    clearTokens();
    window.location = 'index.html';
  }
}

/* ---------- AUTH CHECK ---------- */

function checkAuth() {
  const token = getAccessToken();
  const isAuthPage = window.location.pathname.endsWith('index.html') || 
                     window.location.pathname === '/' ||
                     window.location.pathname.endsWith('/');

  if (!token && !isAuthPage) {
    window.location = 'index.html';
  } else if (token && isAuthPage) {
    window.location = 'tasks.html';
  }
}

// Check auth on page load (for protected routes)
if (typeof window !== 'undefined') {
  // Don't auto-redirect on auth page, let user choose to login/register
}
