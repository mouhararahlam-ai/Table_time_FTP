const API_URL = 'http://127.0.0.1:8000/tasks/';
let tasks = [];
let currentView = 'table';

document.addEventListener('DOMContentLoaded', () => {
    fetchTasks();
    setupEventListeners();
});

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchView(e.target.dataset.view);
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
        });
    });

    // Modal
    const modal = document.getElementById('task-modal');
    const closeBtn = document.querySelector('.close-modal');
    const addBtn = document.getElementById('add-task-btn');
    const form = document.getElementById('task-form');

    addBtn.onclick = () => openModal();
    closeBtn.onclick = () => modal.style.display = 'none';
    window.onclick = (e) => {
        if (e.target === modal) modal.style.display = 'none';
    };

    form.onsubmit = async (e) => {
        e.preventDefault();
        const taskId = document.getElementById('task-id').value;
        const taskData = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            deadline: document.getElementById('deadline').value,
            status: document.getElementById('status').value
        };

        if (taskId) {
            await updateTask(taskId, taskData);
        } else {
            await createTask(taskData);
        }
        modal.style.display = 'none';
        fetchTasks();
    };
}

function switchView(viewName) {
    currentView = viewName;
    document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
    document.getElementById(`view-${viewName}`).classList.add('active');
    render();
}

async function fetchTasks() {
    try {
        const response = await fetch(API_URL);
        tasks = await response.json();
        render();
    } catch (error) {
        console.error('Error fetching tasks:', error);
    }
}

async function createTask(task) {
    await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task)
    });
}

async function updateTask(id, task) {
    await fetch(`${API_URL}${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task)
    });
}

async function deleteTask(id) {
    if (confirm('Are you sure?')) {
        await fetch(`${API_URL}${id}`, { method: 'DELETE' });
        fetchTasks();
    }
}

function openModal(task = null) {
    const modal = document.getElementById('task-modal');
    const title = document.getElementById('modal-title');
    const form = document.getElementById('task-form');

    // Set default deadline to now if new task
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    const defaultDate = now.toISOString().slice(0, 16);

    if (task) {
        title.textContent = 'Edit Task';
        document.getElementById('task-id').value = task.id;
        document.getElementById('title').value = task.title;
        document.getElementById('description').value = task.description || '';
        document.getElementById('deadline').value = task.deadline ? task.deadline.slice(0, 16) : defaultDate;
        document.getElementById('status').value = task.status;
    } else {
        title.textContent = 'New Task';
        form.reset();
        document.getElementById('task-id').value = '';
        document.getElementById('deadline').value = defaultDate;
    }
    modal.style.display = 'flex';
}

function render() {
    if (currentView === 'table') renderTable();
    else if (currentView === 'calendar') renderCalendar();
    else if (currentView === 'agenda') renderAgenda();
}

function renderTable() {
    const tbody = document.getElementById('task-table-body');
    tbody.innerHTML = tasks.map(task => `
        <tr>
            <td><span class="status-badge status-${task.status}">${task.status}</span></td>
            <td><strong>${task.title}</strong><br><small>${task.description || ''}</small></td>
            <td>${new Date(task.deadline).toLocaleString()}</td>
            <td>
                <button class="action-btn" onclick='openModal(${JSON.stringify(task)})'>Edit</button>
                <button class="action-btn delete-btn" onclick="deleteTask(${task.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function renderCalendar() {
    const grid = document.getElementById('calendar-grid');
    grid.innerHTML = ''; // Simplified: just render tasks in a mock grid for now or simple day grouping

    // True calendar logic is complex. We'll group by "Day" for visual simplicity in this demo grid
    // Get unique dates
    const dates = [...new Set(tasks.map(t => t.deadline.split('T')[0]))].sort();

    // If no tasks, show empty state or just a few placeholder days
    if (dates.length === 0) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #aaa;">No tasks scheduled.</p>';
        return;
    }

    dates.forEach(date => {
        const dayTasks = tasks.filter(t => t.deadline.startsWith(date));
        const dayEl = document.createElement('div');
        dayEl.className = 'calendar-day';
        dayEl.innerHTML = `<div class="day-header">${new Date(date).toDateString()}</div>`;

        dayTasks.forEach(task => {
            const taskEl = document.createElement('div');
            taskEl.className = 'calendar-task';
            taskEl.textContent = task.title;
            taskEl.onclick = () => openModal(task);
            dayEl.appendChild(taskEl);
        });
        grid.appendChild(dayEl);
    });
}

function renderAgenda() {
    const container = document.getElementById('agenda-list');
    const sortedTasks = [...tasks].sort((a, b) => new Date(a.deadline) - new Date(b.deadline));

    container.innerHTML = sortedTasks.map(task => `
        <div class="agenda-item">
            <div>
                <div class="agenda-date">${new Date(task.deadline).toLocaleString()}</div>
                <h3>${task.title}</h3>
                <p>${task.description || ''}</p>
            </div>
            <div>
                 <span class="status-badge status-${task.status}">${task.status}</span>
                 <button class="action-btn" onclick='openModal(${JSON.stringify(task)})'>Edit</button>
            </div>
        </div>
    `).join('');
}
