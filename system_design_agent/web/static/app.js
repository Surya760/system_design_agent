/**
 * Frontend Application for Autonomous System Design Agent Dashboard.
 */

// Initialize Mermaid.js
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  fontFamily: 'Inter, sans-serif',
});

// App State
const state = {
  activeView: 'pitchView',
  specs: [],
  currentSpec: null,
  currentSpecMarkdown: '',
  timerInterval: null,
  timerSeconds: 0,
};

// DOM Elements
const views = {
  pitch: document.getElementById('pitchView'),
  progress: document.getElementById('progressView'),
  spec: document.getElementById('specView'),
};

const elements = {
  // Inputs
  pitchTitle: document.getElementById('pitchTitleInput'),
  pitchText: document.getElementById('pitchTextInput'),
  targetDau: document.getElementById('targetDauInput'),
  geminiModel: document.getElementById('geminiModelSelect'),
  
  // Buttons
  btnGenerate: document.getElementById('btnGenerate'),
  btnMockGenerate: document.getElementById('btnMockGenerate'),
  btnNewSpec: document.getElementById('btnNewSpec'),
  btnOpenSettings: document.getElementById('btnOpenSettings'),
  btnCloseSettings: document.getElementById('btnCloseSettings'),
  btnCancelSettings: document.getElementById('btnCancelSettings'),
  btnSaveSettings: document.getElementById('btnSaveSettings'),
  btnToggleKey: document.getElementById('btnToggleKey'),
  btnCopyMarkdown: document.getElementById('btnCopyMarkdown'),
  btnDownloadMarkdown: document.getElementById('btnDownloadMarkdown'),
  
  // Containers
  specHistoryList: document.getElementById('specHistoryList'),
  specSearchInput: document.getElementById('specSearchInput'),
  settingsModal: document.getElementById('settingsModal'),
  settingsGeminiKey: document.getElementById('settingsGeminiKey'),
  settingsDefaultModel: document.getElementById('settingsDefaultModel'),
  settingsDefaultDau: document.getElementById('settingsDefaultDau'),
  
  // Progress elements
  currentStageTitle: document.getElementById('currentStageTitle'),
  currentStageMessage: document.getElementById('currentStageMessage'),
  pipelineTimer: document.getElementById('pipelineTimer'),
  
  // Spec viewer elements
  specViewerTitle: document.getElementById('specViewerTitle'),
  specMetaDau: document.getElementById('specMetaDau'),
  specMetaDuration: document.getElementById('specMetaDuration'),
  specMetaTokens: document.getElementById('specMetaTokens'),
  specMetaStatus: document.getElementById('specMetaStatus'),
  specRenderedOutput: document.getElementById('specRenderedOutput'),
  providerText: document.getElementById('providerText'),
};

// Switch Views
function showView(viewName) {
  state.activeView = viewName;
  Object.keys(views).forEach(k => {
    views[k].classList.toggle('active', k === viewName);
  });
}

// Format Seconds into MM:SS
function formatTimer(seconds) {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = (seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

function startTimer() {
  state.timerSeconds = 0;
  elements.pipelineTimer.textContent = '00:00';
  clearInterval(state.timerInterval);
  state.timerInterval = setInterval(() => {
    state.timerSeconds += 1;
    elements.pipelineTimer.textContent = formatTimer(state.timerSeconds);
  }, 1000);
}

function stopTimer() {
  clearInterval(state.timerInterval);
}

// Reset Stepper UI
function resetStepper() {
  const steps = ['REQUIREMENTS', 'HLD', 'LLD', 'RESILIENCE', 'SCAFFOLDING', 'VALIDATING'];
  steps.forEach(s => {
    const el = document.getElementById(`step-${s}`);
    if (el) {
      el.className = 'step-item pending';
      const ind = el.querySelector('.step-indicator');
      if (ind) ind.textContent = steps.indexOf(s) + 1;
    }
  });
}

function updateStepper(activeStage, message) {
  const steps = ['REQUIREMENTS', 'HLD', 'LLD', 'RESILIENCE', 'SCAFFOLDING', 'VALIDATING'];
  const activeIdx = steps.indexOf(activeStage);

  steps.forEach((s, idx) => {
    const el = document.getElementById(`step-${s}`);
    if (!el) return;
    const ind = el.querySelector('.step-indicator');

    if (idx < activeIdx) {
      el.className = 'step-item completed';
      if (ind) ind.innerHTML = '✓';
    } else if (idx === activeIdx) {
      el.className = 'step-item active';
      if (ind) ind.textContent = idx + 1;
    } else {
      el.className = 'step-item pending';
      if (ind) ind.textContent = idx + 1;
    }
  });

  elements.currentStageTitle = document.getElementById('currentStageTitle');
  elements.currentStageMessage = document.getElementById('currentStageMessage');
  if (elements.currentStageTitle) {
    elements.currentStageTitle.textContent = `Executing Stage ${activeIdx + 1}: ${activeStage}`;
  }
  if (elements.currentStageMessage) {
    elements.currentStageMessage.textContent = message;
  }
}

// Fetch Specs History from API
async function loadSpecs() {
  try {
    const res = await fetch('/api/specs');
    const data = await res.json();
    state.specs = data.specs || [];
    renderHistoryList(state.specs);
  } catch (err) {
    console.error('Failed to load specs:', err);
    elements.specHistoryList.innerHTML = `<div class="p-4 text-xs dim">Error loading specs.</div>`;
  }
}

function renderHistoryList(specs) {
  if (!specs || specs.length === 0) {
    elements.specHistoryList.innerHTML = `<div class="p-4 text-xs dim" style="padding: 1rem; color: #64748b;">No specifications yet. Create your first!</div>`;
    return;
  }

  elements.specHistoryList.innerHTML = specs.map(s => {
    const date = s.created_at ? s.created_at.slice(0, 10) : '';
    const statusClass = s.is_valid ? 'valid' : 'warn';
    const statusText = s.is_valid ? 'Valid' : 'Warn';
    const isActive = state.currentSpec && state.currentSpec.id === s.id;
    return `
      <div class="history-item ${isActive ? 'active' : ''}" data-id="${s.id}">
        <div class="history-title" title="${escapeHtml(s.title)}">${escapeHtml(s.title)}</div>
        <div class="history-meta">
          <span>${date} · ${(s.target_dau || 50000).toLocaleString()} DAU</span>
          <span class="history-tag ${statusClass}">${statusText}</span>
        </div>
      </div>
    `;
  }).join('');

  // Attach click events
  document.querySelectorAll('.history-item').forEach(item => {
    item.addEventListener('click', () => {
      const id = item.getAttribute('data-id');
      loadSingleSpec(id);
    });
  });
}

// Load and View a Specific Spec
async function loadSingleSpec(id) {
  try {
    const res = await fetch(`/api/specs/${id}`);
    if (!res.ok) throw new Error('Spec not found');
    const data = await res.json();
    renderSpecDocument(data);
  } catch (err) {
    alert(`Failed to load spec: ${err.message}`);
  }
}

// Render Markdown and Mermaid in Viewer
async function renderSpecDocument(specData) {
  state.currentSpec = specData;
  const specObj = specData.spec || specData;
  const rawMarkdown = specData.markdown || specObj.raw_markdown || (new Function('return ' + JSON.stringify(specObj)))();
  
  // Update Header Meta
  elements.specViewerTitle.textContent = specObj.title || 'Technical Specification';
  elements.specMetaDau.textContent = `${(specObj.target_dau || 50000).toLocaleString()} DAU`;
  elements.specMetaDuration.textContent = `Duration: ${specData.duration_seconds || specObj.duration_seconds || 0}s`;
  elements.specMetaTokens.textContent = `Tokens: ${(specData.tokens_used || specObj.tokens_used || 0).toLocaleString()}`;
  
  const isValid = specData.is_valid !== undefined ? specData.is_valid : true;
  elements.specMetaStatus.textContent = isValid ? 'PASSED (STRICT ARCHITECTURE)' : 'PASSED WITH WARNINGS';
  elements.specMetaStatus.className = `meta-pill status-pill ${isValid ? 'valid' : 'warn'}`;

  // Store full markdown
  let fullMarkdown = specData.markdown;
  if (!fullMarkdown) {
    // Fetch directly from markdown endpoint
    try {
      const mdRes = await fetch(`/api/specs/${specData.id}/markdown`);
      fullMarkdown = await mdRes.text();
    } catch {
      fullMarkdown = `# ${specObj.title}\n\n${specObj.pitch}`;
    }
  }
  state.currentSpecMarkdown = fullMarkdown;

  // Render full tab by default
  displayTabContent('full');
  showView('spec');
  renderHistoryList(state.specs); // refresh active item indicator
}

function displayTabContent(tabName) {
  if (!state.currentSpecMarkdown) return;

  let contentToRender = state.currentSpecMarkdown;
  if (tabName !== 'full') {
    const sections = parseMarkdownSections(state.currentSpecMarkdown);
    contentToRender = sections[tabName] || `_Section ${tabName} not found in this document._`;
  }

  // Convert markdown to HTML using marked.js
  const html = marked.parse(contentToRender);
  elements.specRenderedOutput.innerHTML = html;

  // Replace ```mermaid code blocks with <div class="mermaid"> containers
  const codeBlocks = elements.specRenderedOutput.querySelectorAll('pre code.language-mermaid');
  codeBlocks.forEach(codeEl => {
    const preEl = codeEl.parentElement;
    const mermaidCode = codeEl.textContent.trim();
    const container = document.createElement('div');
    container.className = 'mermaid-diagram-wrapper';
    
    const preMermaid = document.createElement('pre');
    preMermaid.className = 'mermaid';
    preMermaid.textContent = mermaidCode;
    
    container.appendChild(preMermaid);
    preEl.replaceWith(container);
  });

  // Trigger Mermaid render
  try {
    mermaid.run({
      nodes: elements.specRenderedOutput.querySelectorAll('.mermaid')
    });
  } catch (err) {
    console.warn('Mermaid rendering notice:', err);
  }
}

// Helper: Split Markdown by 5 Sections
function parseMarkdownSections(md) {
  const result = {};
  const s1Match = md.match(/## 1\. Requirements & Core Assumptions([\s\S]*?)(?=## 2\. High-Level Design|$)/i);
  const s2Match = md.match(/## 2\. High-Level Design \(HLD\)([\s\S]*?)(?=## 3\. Low-Level Design|$)/i);
  const s3Match = md.match(/## 3\. Low-Level Design \(LLD\)([\s\S]*?)(?=## 4\. Resilience|$)/i);
  const s4Match = md.match(/## 4\. Resilience, Concurrency & Security([\s\S]*?)(?=## 5\. Developer Action Plan|$)/i);
  const s5Match = md.match(/## 5\. Developer Action Plan & Scaffolding([\s\S]*?)(?=_Generated by|$)/i);

  result['requirements'] = s1Match ? `## 1. Requirements & Core Assumptions\n` + s1Match[1].trim() : '';
  result['hld'] = s2Match ? `## 2. High-Level Design (HLD)\n` + s2Match[1].trim() : '';
  result['lld'] = s3Match ? `## 3. Low-Level Design (LLD)\n` + s3Match[1].trim() : '';
  result['resilience'] = s4Match ? `## 4. Resilience, Concurrency & Security\n` + s4Match[1].trim() : '';
  result['scaffolding'] = s5Match ? `## 5. Developer Action Plan & Scaffolding\n` + s5Match[1].trim() : '';
  return result;
}

// Generate Specification Pipeline Execution
async function startGeneration(isMock = false) {
  const pitch = elements.pitchText.value.trim();
  if (!pitch) {
    alert('Please enter a project pitch or select one from the quick examples.');
    elements.pitchText.focus();
    return;
  }

  const title = elements.pitchTitle.value.trim() || null;
  const dau = parseInt(elements.targetDau.value, 10) || 50000;
  const model = elements.geminiModel.value;
  const apiKey = localStorage.getItem('gemini_api_key') || '';

  // Switch to Stepper Progress View
  resetStepper();
  startTimer();
  showView('progress');

  const payload = {
    pitch,
    title,
    dau,
    provider: isMock ? 'mock' : 'gemini',
    model,
    gemini_api_key: apiKey,
    stream: true,
  };

  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || `HTTP error ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop(); // keep last unfinished line

      for (const block of lines) {
        if (!block.trim()) continue;
        const eventMatch = block.match(/event:\s*([^\n]+)/);
        const dataMatch = block.match(/data:\s*([^\n]+)/);

        const eventType = eventMatch ? eventMatch[1].trim() : 'message';
        const dataStr = dataMatch ? dataMatch[1].trim() : '{}';
        let data = {};
        try {
          data = JSON.parse(dataStr);
        } catch {
          continue;
        }

        if (eventType === 'stage') {
          updateStepper(data.stage, data.message);
        } else if (eventType === 'complete') {
          stopTimer();
          // Reload history and show spec
          await loadSpecs();
          renderSpecDocument(data);
          return;
        } else if (eventType === 'error') {
          stopTimer();
          alert(`Pipeline Error: ${data.message}`);
          showView('pitch');
          return;
        }
      }
    }
  } catch (err) {
    stopTimer();
    alert(`Failed to generate specification: ${err.message}`);
    showView('pitch');
  }
}

// Event Listeners
function setupEventListeners() {
  // Generate Buttons
  elements.btnGenerate.addEventListener('click', () => startGeneration(false));
  elements.btnMockGenerate.addEventListener('click', () => startGeneration(true));

  // New Spec Button
  elements.btnNewSpec.addEventListener('click', () => {
    elements.pitchText.value = '';
    elements.pitchTitle.value = '';
    showView('pitch');
  });

  // Example Chips
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      elements.pitchText.value = chip.getAttribute('data-pitch');
      elements.pitchTitle.value = chip.textContent.trim().replace(/^[^\w\s]+\s*/, '');
    });
  });

  // Section Tabs in Spec Viewer
  document.querySelectorAll('.spec-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.spec-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      displayTabContent(tab.getAttribute('data-tab'));
    });
  });

  // Copy Markdown
  elements.btnCopyMarkdown.addEventListener('click', async () => {
    if (!state.currentSpecMarkdown) return;
    try {
      await navigator.clipboard.writeText(state.currentSpecMarkdown);
      const originalText = elements.btnCopyMarkdown.textContent;
      elements.btnCopyMarkdown.textContent = '✅ Copied!';
      setTimeout(() => {
        elements.btnCopyMarkdown.textContent = originalText;
      }, 2000);
    } catch {
      alert('Failed to copy to clipboard.');
    }
  });

  // Download Markdown
  elements.btnDownloadMarkdown.addEventListener('click', () => {
    if (!state.currentSpec) return;
    const id = state.currentSpec.id;
    window.location.href = `/api/specs/${id}/download`;
  });

  // Search filter
  elements.specSearchInput.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase();
    const filtered = state.specs.filter(s =>
      s.title.toLowerCase().includes(q) || (s.pitch && s.pitch.toLowerCase().includes(q))
    );
    renderHistoryList(filtered);
  });

  // Settings Modal
  elements.btnOpenSettings.addEventListener('click', () => {
    elements.settingsGeminiKey.value = localStorage.getItem('gemini_api_key') || '';
    elements.settingsModal.classList.add('active');
  });

  const closeSettings = () => elements.settingsModal.classList.remove('active');
  elements.btnCloseSettings.addEventListener('click', closeSettings);
  elements.btnCancelSettings.addEventListener('click', closeSettings);

  elements.btnToggleKey.addEventListener('click', () => {
    const isPw = elements.settingsGeminiKey.type === 'password';
    elements.settingsGeminiKey.type = isPw ? 'text' : 'password';
    elements.btnToggleKey.textContent = isPw ? '🔒' : '👁️';
  });

  elements.btnSaveSettings.addEventListener('click', async () => {
    const key = elements.settingsGeminiKey.value.trim();
    if (key) {
      localStorage.setItem('gemini_api_key', key);
    }
    const model = elements.settingsDefaultModel.value;
    const dau = parseInt(elements.settingsDefaultDau.value, 10) || 50000;

    try {
      await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gemini_api_key: key,
          gemini_model: model,
          default_dau: dau,
        }),
      });
      elements.geminiModel.value = model;
      elements.targetDau.value = dau;
      updateProviderPill('Gemini ' + model.replace('gemini-', ''));
      closeSettings();
    } catch (err) {
      alert('Error updating config on server: ' + err.message);
    }
  });
}

function updateProviderPill(text) {
  elements.providerText.textContent = text;
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  await loadSpecs();

  // Load backend config
  try {
    const res = await fetch('/api/config');
    const conf = await res.json();
    if (conf.gemini_model) {
      elements.geminiModel.value = conf.gemini_model;
      elements.settingsDefaultModel.value = conf.gemini_model;
      updateProviderPill('Gemini ' + conf.gemini_model.replace('gemini-', ''));
    }
  } catch {}
});
