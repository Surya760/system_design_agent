/**
 * Frontend Application for Autonomous System Design Agent Dashboard.
 */

// Initialize Mermaid.js
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'strict',
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
  diagrams: [],
  activeDiagram: 0,
  canvasScale: 1,
  canvasX: 0,
  canvasY: 0,
  canvasPointer: null,
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
  modelSelect: document.getElementById('modelSelect'),
  
  // Buttons
  btnGenerate: document.getElementById('btnGenerate'),
  btnMockGenerate: document.getElementById('btnMockGenerate'),
  btnNewSpec: document.getElementById('btnNewSpec'),
  btnOpenSettings: document.getElementById('btnOpenSettings'),
  btnCloseSettings: document.getElementById('btnCloseSettings'),
  btnCancelSettings: document.getElementById('btnCancelSettings'),
  btnSaveSettings: document.getElementById('btnSaveSettings'),
  btnToggleAnthropicKey: document.getElementById('btnToggleAnthropicKey'),
  btnToggleGeminiKey: document.getElementById('btnToggleGeminiKey'),
  btnToggleOpenAIKey: document.getElementById('btnToggleOpenAIKey'),
  btnCopyMarkdown: document.getElementById('btnCopyMarkdown'),
  btnDownloadMarkdown: document.getElementById('btnDownloadMarkdown'),
  btnDownloadBundle: document.getElementById('btnDownloadBundle'),
  
  // Containers
  specHistoryList: document.getElementById('specHistoryList'),
  specSearchInput: document.getElementById('specSearchInput'),
  settingsModal: document.getElementById('settingsModal'),
  settingsAnthropicKey: document.getElementById('settingsAnthropicKey'),
  settingsGeminiKey: document.getElementById('settingsGeminiKey'),
  settingsOpenAIKey: document.getElementById('settingsOpenAIKey'),
  settingsOpenAIBaseUrl: document.getElementById('settingsOpenAIBaseUrl'),
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
  visualDesignPanel: document.getElementById('visualDesignPanel'),
  diagramSelect: document.getElementById('diagramSelect'),
  diagramViewport: document.getElementById('diagramViewport'),
  diagramCanvasLayer: document.getElementById('diagramCanvasLayer'),
  diagramEmpty: document.getElementById('diagramEmpty'),
  diagramNodeTitle: document.getElementById('diagramNodeTitle'),
  diagramNodeDescription: document.getElementById('diagramNodeDescription'),
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
      <span>${date} · ${s.target_dau ? `${s.target_dau.toLocaleString()} DAU` : 'Scale open'}</span>
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
  elements.specMetaDau.textContent = specObj.target_dau ? `${specObj.target_dau.toLocaleString()} DAU` : 'Scale unspecified';
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
  collectDiagrams(fullMarkdown);

  // Render full tab by default
  displayTabContent('full');
  showView('spec');
  renderHistoryList(state.specs); // refresh active item indicator
}

function displayTabContent(tabName) {
  if (!state.currentSpecMarkdown) return;

  if (tabName === 'visual') {
    elements.specRenderedOutput.hidden = true;
    elements.visualDesignPanel.hidden = false;
    renderActiveDiagram();
    return;
  }
  elements.specRenderedOutput.hidden = false;
  elements.visualDesignPanel.hidden = true;

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

function collectDiagrams(markdown) {
  state.activeDiagram = 0;
  const matches = [...markdown.matchAll(/```mermaid\s*\n([\s\S]*?)```/gi)];
  state.diagrams = matches.map((match, index) => {
    const source = match[1].trim();
    const header = source.split('\n', 1)[0].trim();
    const lower = source.toLowerCase();
    let title = `Diagram ${index + 1}`;
    if (header.startsWith('sequenceDiagram')) title = 'Request / Data Flow';
    else if (header.startsWith('erDiagram')) title = 'Data Model';
    else if (lower.includes('deployment') || lower.includes('environment')) title = 'Deployment';
    else if (header.startsWith('graph') || header.startsWith('flowchart')) title = index === 0 ? 'Architecture' : title;
    return { title, source };
  });
  const select = elements.diagramSelect;
  select.replaceChildren();
  state.diagrams.forEach((diagram, index) => {
    const option = document.createElement('option');
    option.value = String(index);
    option.textContent = diagram.title;
    select.appendChild(option);
  });
  elements.diagramEmpty.hidden = state.diagrams.length > 0;
  select.disabled = state.diagrams.length === 0;
}

function updateCanvasTransform() {
  elements.diagramCanvasLayer.style.transform = `translate(${state.canvasX}px, ${state.canvasY}px) scale(${state.canvasScale})`;
}

function fitDiagram() {
  const svg = elements.diagramCanvasLayer.querySelector('svg');
  if (!svg) return;
  const viewBox = svg.viewBox.baseVal;
  const box = elements.diagramViewport.getBoundingClientRect();
  if (!viewBox.width || !viewBox.height || !box.width || !box.height) return;
  const padding = 48;
  state.canvasScale = Math.min((box.width - padding) / viewBox.width, (box.height - padding) / viewBox.height, 1.5);
  state.canvasX = (box.width - viewBox.width * state.canvasScale) / 2;
  state.canvasY = (box.height - viewBox.height * state.canvasScale) / 2;
  updateCanvasTransform();
}

async function renderActiveDiagram() {
  if (!state.diagrams.length) {
    elements.diagramEmpty.hidden = false;
    elements.diagramCanvasLayer.replaceChildren();
    return;
  }
  elements.diagramEmpty.hidden = true;
  const diagram = state.diagrams[state.activeDiagram];
  if (!diagram) return;
  elements.diagramSelect.value = String(state.activeDiagram);
  elements.diagramNodeTitle.textContent = 'Choose a node';
  elements.diagramNodeDescription.textContent = 'Click any diagram component to inspect its label.';
  const renderId = `system-design-diagram-${state.currentSpec?.id || 'active'}-${state.activeDiagram}`.replace(/[^a-zA-Z0-9_-]/g, '-');
  try {
    const rendered = await mermaid.render(renderId, diagram.source);
    const parsed = new DOMParser().parseFromString(rendered.svg, 'image/svg+xml');
    const svg = parsed.documentElement;
    if (parsed.querySelector('parsererror')) throw new Error('Could not parse the rendered diagram.');
    const viewBox = svg.viewBox?.baseVal;
    if (viewBox?.width && viewBox?.height) {
      svg.setAttribute('width', String(viewBox.width));
      svg.setAttribute('height', String(viewBox.height));
    }
    elements.diagramCanvasLayer.replaceChildren(document.importNode(svg, true));
    elements.diagramCanvasLayer.querySelectorAll('.node').forEach((node) => {
      node.setAttribute('tabindex', '0');
      node.setAttribute('role', 'button');
      const inspect = () => {
        const label = node.textContent.trim().replace(/\s+/g, ' ');
        elements.diagramNodeTitle.textContent = label || node.id || 'Diagram component';
        elements.diagramNodeDescription.textContent = `Diagram: ${diagram.title}. This component is shown as a node in the generated architecture.`;
      };
      node.addEventListener('click', inspect);
      node.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); inspect(); }
      });
    });
    state.canvasScale = 1;
    state.canvasX = 24;
    state.canvasY = 24;
    updateCanvasTransform();
    requestAnimationFrame(fitDiagram);
  } catch (error) {
    elements.diagramCanvasLayer.replaceChildren();
    elements.diagramEmpty.hidden = false;
    elements.diagramEmpty.textContent = `This diagram could not be rendered: ${error.message}`;
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
  const parsedDau = parseInt(elements.targetDau.value, 10);
  const dau = Number.isFinite(parsedDau) && parsedDau > 0 ? parsedDau : 0;
  const model = elements.modelSelect.value;
  const isClaude = model.startsWith('claude');
  const isOpenAI = model.startsWith('gpt') || model.startsWith('o1') || model.startsWith('o3');
  
  let provider = 'gemini';
  if (isMock) {
    provider = 'mock';
  } else if (isClaude) {
    provider = 'anthropic';
  } else if (isOpenAI) {
    provider = 'openai';
  }

  const geminiKey = localStorage.getItem('gemini_api_key') || '';
  const anthropicKey = localStorage.getItem('anthropic_api_key') || '';
  const openaiKey = localStorage.getItem('openai_api_key') || '';

  // Switch to Stepper Progress View
  resetStepper();
  startTimer();
  showView('progress');

  const payload = {
    pitch,
    title,
    dau,
    provider,
    model,
    gemini_api_key: geminiKey,
    anthropic_api_key: anthropicKey,
    openai_api_key: openaiKey,
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

  elements.diagramSelect.addEventListener('change', async (event) => {
    state.activeDiagram = Number(event.target.value) || 0;
    await renderActiveDiagram();
  });
  document.getElementById('diagramZoomIn').addEventListener('click', () => {
    state.canvasScale = Math.min(state.canvasScale * 1.2, 4);
    updateCanvasTransform();
  });
  document.getElementById('diagramZoomOut').addEventListener('click', () => {
    state.canvasScale = Math.max(state.canvasScale / 1.2, 0.25);
    updateCanvasTransform();
  });
  document.getElementById('diagramFit').addEventListener('click', fitDiagram);
  document.getElementById('diagramCopy').addEventListener('click', async () => {
    const source = state.diagrams[state.activeDiagram]?.source;
    if (!source) return;
    try {
      await navigator.clipboard.writeText(source);
    } catch {
      elements.diagramNodeDescription.textContent = 'Clipboard access is unavailable in this browser context.';
    }
  });
  document.getElementById('diagramDownload').addEventListener('click', () => {
    const svg = elements.diagramCanvasLayer.querySelector('svg');
    if (!svg) return;
    const source = new XMLSerializer().serializeToString(svg);
    const blobUrl = URL.createObjectURL(new Blob([source], { type: 'image/svg+xml;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = `${state.diagrams[state.activeDiagram]?.title.toLowerCase().replace(/[^a-z0-9]+/g, '-') || 'design'}.svg`;
    link.click();
    URL.revokeObjectURL(blobUrl);
  });
  elements.diagramViewport.addEventListener('wheel', (event) => {
    event.preventDefault();
    const factor = event.deltaY < 0 ? 1.1 : 0.9;
    const nextScale = Math.min(Math.max(state.canvasScale * factor, 0.25), 4);
    const bounds = elements.diagramViewport.getBoundingClientRect();
    const px = event.clientX - bounds.left;
    const py = event.clientY - bounds.top;
    const ratio = nextScale / state.canvasScale;
    state.canvasX = px - (px - state.canvasX) * ratio;
    state.canvasY = py - (py - state.canvasY) * ratio;
    state.canvasScale = nextScale;
    updateCanvasTransform();
  }, { passive: false });
  elements.diagramViewport.addEventListener('pointerdown', (event) => {
    if (event.target.closest('.node')) return;
    state.canvasPointer = { id: event.pointerId, x: event.clientX, y: event.clientY };
    elements.diagramViewport.setPointerCapture(event.pointerId);
  });
  elements.diagramViewport.addEventListener('pointermove', (event) => {
    if (!state.canvasPointer || state.canvasPointer.id !== event.pointerId) return;
    state.canvasX += event.clientX - state.canvasPointer.x;
    state.canvasY += event.clientY - state.canvasPointer.y;
    state.canvasPointer.x = event.clientX;
    state.canvasPointer.y = event.clientY;
    updateCanvasTransform();
  });
  const stopCanvasPan = () => { state.canvasPointer = null; };
  elements.diagramViewport.addEventListener('pointerup', stopCanvasPan);
  elements.diagramViewport.addEventListener('pointercancel', stopCanvasPan);
  window.addEventListener('resize', () => {
    if (!elements.visualDesignPanel.hidden) fitDiagram();
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
  elements.btnDownloadBundle.addEventListener('click', () => {
    if (!state.currentSpec) return;
    window.location.href = `/api/specs/${state.currentSpec.id}/bundle`;
  });

  // Search filter
  elements.specSearchInput.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase();
    const filtered = state.specs.filter(s =>
      s.title.toLowerCase().includes(q) || (s.pitch && s.pitch.toLowerCase().includes(q))
    );
    renderHistoryList(filtered);
  });

  // Model change listener
  elements.modelSelect.addEventListener('change', (e) => {
    const val = e.target.value;
    updateModelUI(val);
  });

  // Settings Modal
  elements.btnOpenSettings.addEventListener('click', () => {
    elements.settingsGeminiKey.value = localStorage.getItem('gemini_api_key') || '';
    elements.settingsAnthropicKey.value = localStorage.getItem('anthropic_api_key') || '';
    elements.settingsOpenAIKey.value = localStorage.getItem('openai_api_key') || '';
    elements.settingsOpenAIBaseUrl.value = localStorage.getItem('openai_base_url') || 'https://api.openai.com/v1';
    elements.settingsModal.classList.add('active');
  });

  const closeSettings = () => elements.settingsModal.classList.remove('active');
  elements.btnCloseSettings.addEventListener('click', closeSettings);
  elements.btnCancelSettings.addEventListener('click', closeSettings);

  elements.btnToggleGeminiKey.addEventListener('click', () => {
    const isPw = elements.settingsGeminiKey.type === 'password';
    elements.settingsGeminiKey.type = isPw ? 'text' : 'password';
    elements.btnToggleGeminiKey.textContent = isPw ? '🔒' : '👁️';
  });

  elements.btnToggleAnthropicKey.addEventListener('click', () => {
    const isPw = elements.settingsAnthropicKey.type === 'password';
    elements.settingsAnthropicKey.type = isPw ? 'text' : 'password';
    elements.btnToggleAnthropicKey.textContent = isPw ? '🔒' : '👁️';
  });

  elements.btnToggleOpenAIKey.addEventListener('click', () => {
    const isPw = elements.settingsOpenAIKey.type === 'password';
    elements.settingsOpenAIKey.type = isPw ? 'text' : 'password';
    elements.btnToggleOpenAIKey.textContent = isPw ? '🔒' : '👁️';
  });

  elements.btnSaveSettings.addEventListener('click', async () => {
    const gKey = elements.settingsGeminiKey.value.trim();
    if (gKey) localStorage.setItem('gemini_api_key', gKey);

    const aKey = elements.settingsAnthropicKey.value.trim();
    if (aKey) localStorage.setItem('anthropic_api_key', aKey);

    const oKey = elements.settingsOpenAIKey.value.trim();
    if (oKey) localStorage.setItem('openai_api_key', oKey);

    const oBaseUrl = elements.settingsOpenAIBaseUrl.value.trim();
    if (oBaseUrl) localStorage.setItem('openai_base_url', oBaseUrl);

    const model = elements.settingsDefaultModel.value;
    const parsedDau = parseInt(elements.settingsDefaultDau.value, 10);
    const dau = Number.isFinite(parsedDau) && parsedDau > 0 ? parsedDau : 0;

    try {
      await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gemini_api_key: gKey,
          anthropic_api_key: aKey,
          openai_api_key: oKey,
          openai_base_url: oBaseUrl,
          model: model,
          default_dau: dau,
        }),
      });
      elements.modelSelect.value = model;
      elements.targetDau.value = dau;
      updateModelUI(model);
      closeSettings();
    } catch (err) {
      alert('Error updating config on server: ' + err.message);
    }
  });
}

function updateModelUI(model) {
  if (model.startsWith('claude')) {
    const isOpus = model.includes('opus');
    const label = isOpus ? 'Claude 3 Opus' : (model.includes('sonnet') ? 'Claude Sonnet' : 'Claude Haiku');
    elements.btnGenerate.innerHTML = `<span>✨</span> Generate with ${label}`;
    updateProviderPill(label);
  } else if (model.startsWith('gpt') || model.startsWith('o1') || model.startsWith('o3')) {
    let label = model.toUpperCase();
    if (model === 'gpt-4o') label = 'GPT-4o';
    else if (model === 'gpt-4o-mini') label = 'GPT-4o Mini';
    else if (model === 'o3-mini') label = 'o3-mini';
    else if (model === 'o1') label = 'o1';
    elements.btnGenerate.innerHTML = `<span>✨</span> Generate with ${label}`;
    updateProviderPill('OpenAI ' + label);
  } else {
    elements.btnGenerate.innerHTML = `<span>✨</span> Generate with Gemini`;
    updateProviderPill('Gemini ' + model.replace('gemini-', ''));
  }
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
