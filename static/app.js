// DOM Elements
const catalogSelect = document.getElementById('catalogSelect');
const schemaSelect = document.getElementById('schemaSelect');
const tableSelect = document.getElementById('tableSelect');
const loadTableBtn = document.getElementById('loadTableBtn');
const customQueryBtn = document.getElementById('customQueryBtn');
const querySection = document.getElementById('querySection');
const queryInput = document.getElementById('queryInput');
const executeQueryBtn = document.getElementById('executeQueryBtn');
const cancelQueryBtn = document.getElementById('cancelQueryBtn');
const statusBar = document.getElementById('statusBar');
const statusMessage = document.getElementById('statusMessage');
const resultsContainer = document.getElementById('resultsContainer');
const rowCount = document.getElementById('rowCount');

let currentCatalog = '';
let currentSchema = '';
let currentTable = '';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadCatalogs();
    setupEventListeners();
});

function setupEventListeners() {
    catalogSelect.addEventListener('change', onCatalogChange);
    schemaSelect.addEventListener('change', onSchemaChange);
    tableSelect.addEventListener('change', onTableChange);
    loadTableBtn.addEventListener('click', loadTableData);
    customQueryBtn.addEventListener('click', showCustomQuery);
    executeQueryBtn.addEventListener('click', executeCustomQuery);
    cancelQueryBtn.addEventListener('click', hideCustomQuery);
}

// API Functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`/api/${endpoint}`, options);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showStatus(error.message, 'error');
        throw error;
    }
}

async function loadCatalogs() {
    showStatus('Loading catalogs...', 'loading');
    try {
        const data = await apiCall('catalogs');
        populateSelect(catalogSelect, data.catalogs);
        showStatus('Catalogs loaded', 'success');
    } catch (error) {
        showStatus('Failed to load catalogs', 'error');
    }
}

async function onCatalogChange() {
    currentCatalog = catalogSelect.value;
    
    // Reset dependent selects
    schemaSelect.disabled = true;
    tableSelect.disabled = true;
    loadTableBtn.disabled = true;
    schemaSelect.innerHTML = '<option value="">Select Schema...</option>';
    tableSelect.innerHTML = '<option value="">Select Table...</option>';
    
    if (!currentCatalog) return;
    
    showStatus(`Loading schemas from ${currentCatalog}...`, 'loading');
    try {
        const data = await apiCall(`schemas/${currentCatalog}`);
        populateSelect(schemaSelect, data.schemas);
        schemaSelect.disabled = false;
        showStatus('Schemas loaded', 'success');
    } catch (error) {
        showStatus('Failed to load schemas', 'error');
    }
}

async function onSchemaChange() {
    currentSchema = schemaSelect.value;
    
    // Reset dependent selects
    tableSelect.disabled = true;
    loadTableBtn.disabled = true;
    tableSelect.innerHTML = '<option value="">Select Table...</option>';
    
    if (!currentSchema) return;
    
    showStatus(`Loading tables from ${currentCatalog}.${currentSchema}...`, 'loading');
    try {
        const data = await apiCall(`tables/${currentCatalog}/${currentSchema}`);
        populateSelect(tableSelect, data.tables);
        tableSelect.disabled = false;
        showStatus('Tables loaded', 'success');
    } catch (error) {
        showStatus('Failed to load tables', 'error');
    }
}

function onTableChange() {
    currentTable = tableSelect.value;
    loadTableBtn.disabled = !currentTable;
}

async function loadTableData() {
    if (!currentTable) return;
    
    const fullTableName = `${currentCatalog}.${currentSchema}.${currentTable}`;
    showStatus(`Loading data from ${fullTableName}...`, 'loading');
    
    try {
        const data = await apiCall('query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ table: fullTableName, limit: 100 })
        });
        
        displayResults(data);
        showStatus(`Loaded ${data.count} rows from ${fullTableName}`, 'success');
    } catch (error) {
        showStatus('Failed to load table data', 'error');
    }
}

function showCustomQuery() {
    querySection.style.display = 'block';
    queryInput.focus();
}

function hideCustomQuery() {
    querySection.style.display = 'none';
    queryInput.value = '';
}

async function executeCustomQuery() {
    const query = queryInput.value.trim();
    
    if (!query) {
        showStatus('Please enter a query', 'error');
        return;
    }
    
    showStatus('Executing query...', 'loading');
    
    try {
        const data = await apiCall('custom-query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        displayResults(data);
        showStatus(`Query executed successfully - ${data.count} rows returned`, 'success');
        hideCustomQuery();
    } catch (error) {
        showStatus('Query execution failed', 'error');
    }
}

// UI Helper Functions
function populateSelect(selectElement, items) {
    const defaultOption = selectElement.options[0].text;
    selectElement.innerHTML = `<option value="">${defaultOption}</option>`;
    
    items.forEach(item => {
        const option = document.createElement('option');
        option.value = item;
        option.textContent = item;
        selectElement.appendChild(option);
    });
}

function displayResults(data) {
    if (!data.columns || !data.rows || data.rows.length === 0) {
        resultsContainer.innerHTML = '<p class="empty-state">No results found</p>';
        rowCount.textContent = '';
        return;
    }
    
    // Update row count
    rowCount.textContent = `${data.count} rows`;
    
    // Create table
    let tableHTML = '<table class="results-table"><thead><tr>';
    
    // Add headers
    data.columns.forEach(col => {
        tableHTML += `<th>${escapeHtml(col)}</th>`;
    });
    tableHTML += '</tr></thead><tbody>';
    
    // Add rows
    data.rows.forEach(row => {
        tableHTML += '<tr>';
        row.forEach(cell => {
            const cellValue = cell === null ? '<em>NULL</em>' : escapeHtml(String(cell));
            tableHTML += `<td>${cellValue}</td>`;
        });
        tableHTML += '</tr>';
    });
    
    tableHTML += '</tbody></table>';
    resultsContainer.innerHTML = tableHTML;
}

function showStatus(message, type = '') {
    statusMessage.textContent = message;
    statusBar.className = 'status-bar';
    
    if (type) {
        statusBar.classList.add(type);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}