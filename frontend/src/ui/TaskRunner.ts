import { SessionComposer, TaskRequestPayload } from '../engine/AdaptiveEngine';
import { AssessmentEngine } from '../engine/AssessmentEngine';
import { RepetitionGuard } from '../engine/RepetitionGuard';
import { TelemetryQueue } from '../storage/telemetry_queue';
import { MapScreen } from './MapScreen';
import { soundFX } from '../utils/SoundFX';
import { resolveAssetUrl } from '../utils/assets';
import { DailyQuestManager } from '../engine/DailyQuestManager';
import { QuestionPresentationLog } from '../storage/QuestionPresentationLog';

const GENERIC_HINTS = new Set([
  "Look closely at the picture and count each item.",
  "Observe the color, shape, and clues shown in the illustration.",
  "Remember the foundational rule: observe, compare, and verify."
]);

export class TaskRunner {
  private container: HTMLElement;
  private currentSession: TaskRequestPayload[] = [];
  private currentTaskIndex = 0;
  private sessionErrors = 0;
  private composer: SessionComposer;
  private assessmentEngine: AssessmentEngine;
  private telemetry: TelemetryQueue;

  private app: any;
  private currentValidHint: string | null = null;
  private flagPressTimer: any = null;
  private currentTaskWrongAttempts = 0;

  constructor(_app: any) {
    this.app = _app;
    this.container = document.getElementById('modal-task-runner') as HTMLElement;
    this.composer = new SessionComposer();
    this.assessmentEngine = new AssessmentEngine();
    this.telemetry = new TelemetryQueue();
  }

  public render() {
    this.container.innerHTML = `
      <div class="modal-content task-modal-content" style="position: relative;">
        <header class="task-header" style="display: flex; justify-content: space-between; align-items: center;">
          <div class="quest-status" id="task-progress-indicator">Task 1 of X</div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <button id="btn-report-flag" class="btn-flag" title="Press and hold for 2s to report a problem" style="background: transparent; border: none; font-size: 1.15rem; cursor: pointer; opacity: 0.6; padding: 4px 6px; border-radius: 6px; user-select: none; -webkit-user-select: none;">🚩</button>
            <button id="btn-quit-task" class="btn btn-small">Quit</button>
          </div>
        </header>
        <main class="task-container">
          <div class="prompt-container">
            <button id="btn-play-audio" class="btn-audio" title="Listen to prompt">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M13.5 4.06c0-1.336-1.616-2.005-2.56-1.06l-4.5 4.5H4.508c-1.141 0-2.318.664-2.66 1.905A9.76 9.76 0 001.5 12c0 .898.121 1.768.35 2.595.341 1.24 1.518 1.905 2.659 1.905h1.93l4.5 4.5c.945.945 2.561.276 2.561-1.06V4.06zM18.584 5.106a.75.75 0 011.06 0c3.808 3.807 3.808 9.98 0 13.788a.75.75 0 11-1.06-1.06 8.25 8.25 0 000-11.668.75.75 0 010-1.06z" />
                <path d="M15.932 7.757a.75.75 0 011.061 0 6 6 0 010 8.486.75.75 0 01-1.06-1.061 4.5 4.5 0 000-6.364.75.75 0 010-1.06z" />
              </svg>
            </button>
            <h2 id="task-prompt-text">Loading...</h2>
          </div>
          <div id="task-visual" class="visual-container">
            <!-- Inline SVG/Visual Placeholder -->
          </div>
          <div id="scaffolding-hint" class="hint-container hidden">
            <!-- Hint text injected here on incorrect attempts -->
          </div>
          <div id="options-container" class="options-grid">
            <!-- Chunky Buttons injected here -->
          </div>
        </main>

        <!-- Problem Report Overlay (Appears on 2s Long-Press of 🚩) -->
        <div id="problem-report-overlay" class="hidden" style="position: absolute; inset: 0; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 200; padding: 16px; border-radius: 20px;">
          <div style="background: white; border-radius: 16px; padding: 20px; max-width: 440px; width: 100%; box-shadow: 0 10px 25px rgba(0,0,0,0.3); color: #1e293b; text-align: left;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <h3 style="margin: 0; font-size: 1.15rem; font-weight: bold; color: #1e293b;">🚩 Parent Problem Report</h3>
              <button id="btn-close-report" style="background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #64748b; padding: 4px 8px;">✕</button>
            </div>
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">Copy this debug info and send it to the developer:</p>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; font-family: monospace; font-size: 0.85rem; margin-bottom: 16px; word-break: break-word;">
              <div><strong>Item ID:</strong> <span id="report-item-id">-</span></div>
              <div style="margin-top: 6px;"><strong>Subskill:</strong> <span id="report-subskill-id">-</span></div>
              <div style="margin-top: 6px;"><strong>Prompt:</strong> <span id="report-prompt-text">-</span></div>
            </div>
            <div style="display: flex; gap: 10px; justify-content: flex-end; align-items: center;">
              <span id="copy-confirmation" class="hidden" style="color: #16a34a; font-size: 0.85rem; font-weight: 500;">✓ Copied!</span>
              <button id="btn-copy-report" style="background: #2563eb; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: bold; cursor: pointer;">📋 Copy Info</button>
            </div>
          </div>
        </div>
      </div>
    `;

    this.bindEvents();
  }

  private cancelSpeech() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
      } catch (e) {}
    }
  }

  private speakPrompt(text: string) {
    if (!text || typeof window === 'undefined' || !('speechSynthesis' in window) || typeof SpeechSynthesisUtterance === 'undefined') {
      return;
    }
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 0.85;

      const voices = window.speechSynthesis.getVoices();
      const enVoice = voices.find(v => v.lang.startsWith('en')) || null;
      if (enVoice) utterance.voice = enVoice;

      console.log('[TaskRunner] SpeechSynthesis speak called for prompt:', text);
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn('[TaskRunner] Speech synthesis failed or blocked:', e);
    }
  }

  private computeValidHint(item: any): string | null {
    if (!item?.scaffolding_protocol) return null;
    const hasVisual = Boolean(item.representation_type === 'VISUAL' && item.prompt_structure?.visual_assets?.[0]?.uri);

    const candidates: string[] = [
      item.scaffolding_protocol.level_1_reflection_prompt?.prompt || '',
      item.scaffolding_protocol.level_2_representation_shift?.hint || '',
      item.scaffolding_protocol.level_3_prerequisite_bridge?.hint || ''
    ];

    for (const text of candidates) {
      const trimmed = text.trim();
      if (!trimmed) continue;
      if (GENERIC_HINTS.has(trimmed)) continue;
      if (!hasVisual && /\b(illustration|picture)\b/i.test(trimmed)) continue;
      return trimmed;
    }
    return null;
  }

  private showProblemReport() {
    console.log('[TaskRunner] Opening Parent Problem Report overlay.');
    const overlay = this.container.querySelector('#problem-report-overlay');
    if (!overlay) return;
    const item = this.currentSession[this.currentTaskIndex]?.question_item;
    const elItemId = overlay.querySelector('#report-item-id');
    const elSubskill = overlay.querySelector('#report-subskill-id');
    const elPrompt = overlay.querySelector('#report-prompt-text');
    const copyConfirm = overlay.querySelector('#copy-confirmation');

    if (elItemId) elItemId.textContent = item?.item_id || 'UNKNOWN';
    if (elSubskill) elSubskill.textContent = item?.target_subskill_id || 'UNKNOWN';
    if (elPrompt) elPrompt.textContent = item?.prompt_structure?.display_text || 'UNKNOWN';
    if (copyConfirm) copyConfirm.classList.add('hidden');

    overlay.classList.remove('hidden');
  }

  private copyProblemReport() {
    const item = this.currentSession[this.currentTaskIndex]?.question_item;
    const text = `Item ID: ${item?.item_id || 'UNKNOWN'}\nSubskill: ${item?.target_subskill_id || 'UNKNOWN'}\nPrompt: ${item?.prompt_structure?.display_text || 'UNKNOWN'}`;

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => {
        const confirm = this.container.querySelector('#copy-confirmation');
        if (confirm) confirm.classList.remove('hidden');
        console.log('[TaskRunner] Problem report info copied to clipboard.');
      }).catch(() => {
        this.fallbackCopy(text);
      });
    } else {
      this.fallbackCopy(text);
    }
  }

  private fallbackCopy(text: string) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      const confirm = this.container.querySelector('#copy-confirmation');
      if (confirm) confirm.classList.remove('hidden');
      console.log('[TaskRunner] Problem report info copied via execCommand fallback.');
    } catch (e) {}
    document.body.removeChild(ta);
  }

  private showEmptyBankError() {
    this.cancelSpeech();
    this.container.classList.add('active');
    this.container.innerHTML = `
      <div class="modal-content task-modal-content" style="text-align: center; padding: 40px 20px;">
        <header class="task-header" style="justify-content: flex-end; display: flex;">
          <button id="btn-quit-task" class="btn btn-small">✕</button>
        </header>
        <main class="task-container" style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 250px;">
          <div style="font-size: 3rem; margin-bottom: 16px;">🏰✨</div>
          <h2 style="font-size: 1.4rem; color: #1e293b; margin-bottom: 12px; font-weight: 700;">Couldn't load the questions.</h2>
          <p style="color: #64748b; font-size: 1.05rem; margin-bottom: 24px; max-width: 400px; line-height: 1.5;">Check your connection and reload.</p>
          <p style="color: #94a3b8; font-size: 0.8rem; margin: -12px 0 20px; max-width: 420px; word-break: break-word;">${(this.composer.questionBank.getLoadErrors?.() || []).join(' · ') || 'No error details recorded.'}</p>
          <button id="btn-reload-app" class="btn btn-large cta-glow" style="padding: 12px 32px; font-size: 1.1rem; border-radius: 12px; background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border: none; cursor: pointer; font-weight: bold;">Reload</button>
        </main>
      </div>
    `;
    const btnReload = this.container.querySelector('#btn-reload-app');
    if (btnReload) {
      btnReload.addEventListener('click', () => {
        window.location.reload();
      });
    }
    const btnQuit = this.container.querySelector('#btn-quit-task');
    if (btnQuit) {
      btnQuit.addEventListener('click', () => {
        this.container.classList.remove('active');
        this.render();
      });
    }
  }

  private bindEvents() {
    const hasSpeech = typeof window !== 'undefined' && 'speechSynthesis' in window && typeof SpeechSynthesisUtterance !== 'undefined';
    const btnAudio = this.container.querySelector('#btn-play-audio') as HTMLElement | null;
    if (btnAudio) {
      if (!hasSpeech) {
        btnAudio.style.display = 'none';
      } else {
        btnAudio.addEventListener('click', (e) => {
          e.stopPropagation();
          const item = this.currentSession[this.currentTaskIndex]?.question_item;
          const text = item?.prompt_structure?.display_text;
          if (text) {
            console.log('[TaskRunner] Audio button clicked by user.');
            this.speakPrompt(text);
          }
        });
      }
    }

    const btnQuit = this.container.querySelector('#btn-quit-task');
    if (btnQuit) {
      btnQuit.addEventListener('click', () => {
        this.cancelSpeech();
        this.container.classList.remove('active');
      });
    }

    // Flag button long-press (2 seconds)
    const btnFlag = this.container.querySelector('#btn-report-flag') as HTMLElement | null;
    if (btnFlag) {
      const startPress = (_e: Event) => {
        console.log('[TaskRunner] Flag press started (2s timer initiated).');
        btnFlag.style.opacity = '1';
        btnFlag.style.transform = 'scale(1.25)';
        if (!this.flagPressTimer) {
          this.flagPressTimer = setTimeout(() => {
            console.log('[TaskRunner] 2s long-press elapsed on flag.');
            btnFlag.style.transform = 'none';
            this.showProblemReport();
            this.flagPressTimer = null;
          }, 2000);
        }
      };
      const cancelPress = () => {
        if (this.flagPressTimer) {
          console.log('[TaskRunner] Flag press released before 2s.');
          clearTimeout(this.flagPressTimer);
          this.flagPressTimer = null;
        }
        btnFlag.style.opacity = '0.6';
        btnFlag.style.transform = 'none';
      };
      btnFlag.addEventListener('pointerdown', startPress);
      btnFlag.addEventListener('mousedown', startPress);
      btnFlag.addEventListener('touchstart', startPress, {passive: true});
      btnFlag.addEventListener('pointerup', cancelPress);
      btnFlag.addEventListener('mouseup', cancelPress);
      btnFlag.addEventListener('touchend', cancelPress);
      btnFlag.addEventListener('pointerleave', cancelPress);
      btnFlag.addEventListener('pointercancel', cancelPress);
    }

    // Problem report close & copy
    const btnCloseReport = this.container.querySelector('#btn-close-report');
    if (btnCloseReport) {
      btnCloseReport.addEventListener('click', () => {
        const overlay = this.container.querySelector('#problem-report-overlay');
        if (overlay) overlay.classList.add('hidden');
      });
    }
    const btnCopyReport = this.container.querySelector('#btn-copy-report');
    if (btnCopyReport) {
      btnCopyReport.addEventListener('click', () => {
        this.copyProblemReport();
      });
    }
  }

  public async startSession(sessionData?: TaskRequestPayload[], focusedDomain?: string) {
    const kidName = this.app?.profileSwitcher?.getCurrentPlayerName() || 'default_player';
    await this.composer.ensureReady();

    // Empty Question Bank Guard
    if (this.composer.questionBank.getLoadedCount() === 0) {
      this.showEmptyBankError();
      return;
    }

    // Ensure task runner DOM structure is rendered
    this.render();

    // If not provided, dynamically compose using AdaptiveEngine
    if (sessionData && sessionData.length > 0) {
      this.currentSession = RepetitionGuard.validateAndEnforce(sessionData, kidName, this.composer.questionBank);
    } else {
      this.currentSession = this.composer.generateSession(kidName, focusedDomain);
    }
    
    this.currentTaskIndex = 0;
    this.sessionErrors = 0;
    this.currentTaskWrongAttempts = 0;
    this.container.classList.add('active');
    this.renderTask();
  }

  private renderTask() {
    this.cancelSpeech();
    this.currentTaskWrongAttempts = 0;

    if (this.currentTaskIndex >= this.currentSession.length) {
      this.finishSession();
      return;
    }
    
    const taskRequest = this.currentSession[this.currentTaskIndex];
    const item = taskRequest.question_item;
    
    const progress = this.container.querySelector('#task-progress-indicator');
    const promptText = this.container.querySelector('#task-prompt-text');
    const visual = this.container.querySelector('#task-visual');
    const hint = this.container.querySelector('#scaffolding-hint');
    const options = this.container.querySelector('#options-container');
    
    const depth = taskRequest.required_cognitive_depth || item?.cognitive_depth || 'APPLY';
    if (progress) {
      progress.textContent = `Task ${this.currentTaskIndex + 1} of ${this.currentSession.length} (${taskRequest.task_function_type} • ${depth})`;
    }
    
    if (item && promptText) {
      promptText.textContent = item.prompt_structure.display_text;
      // Auto-read prompt
      this.speakPrompt(item.prompt_structure.display_text);
    } else if (promptText) {
      promptText.textContent = "Error loading task item.";
    }

    if (visual) {
      const visualEl = visual as HTMLElement;
      const visualAssets = item?.prompt_structure?.visual_assets;
      const firstAsset = visualAssets && visualAssets.length > 0 ? visualAssets[0] : undefined;
      const isVisual = item?.representation_type === 'VISUAL' && Boolean(firstAsset?.uri);

      // Default hidden
      visualEl.style.display = 'none';
      visualEl.innerHTML = '';

      if (isVisual && firstAsset) {
        const assetUri = resolveAssetUrl(firstAsset.uri || '');
        const wrapper = document.createElement('div');
        wrapper.className = 'task-visual-wrapper';

        const img = document.createElement('img');
        img.src = assetUri;
        img.alt = 'Visual context clue';
        img.className = 'task-visual-img';
        img.onload = () => {
          img.style.background = '#ffffff';
          visualEl.style.display = 'flex';
        };
        img.onerror = () => {
          visualEl.style.display = 'none';
          visualEl.innerHTML = '';
        };

        wrapper.appendChild(img);
        visualEl.appendChild(wrapper);
      }
    }
    
    // Compute valid non-generic hint
    this.currentValidHint = this.computeValidHint(item);
    if (hint) {
      hint.classList.add('hidden');
      hint.textContent = this.currentValidHint || '';
    }
    
    if (options && item) {
      options.innerHTML = '';
      
      let optionsData: { id: string, text: string, assetUri?: string }[] = [];
      const tapSelectOptions = item.interaction_model?.modality_configurations?.tap_select?.options;
      
      if (tapSelectOptions && tapSelectOptions.length > 0) {
        optionsData = tapSelectOptions.map((o: any) => ({
          id: o.option_id,
          text: o.display_value,
          assetUri: o.asset_uri
        }));
      } else if (item.options && item.options.length > 0) {
        optionsData = item.options;
      } else {
        optionsData = [
          { id: 'opt_1', text: 'Option A' },
          { id: 'opt_2', text: 'Option B' },
          { id: 'opt_3', text: 'Option C' },
          { id: 'opt_4', text: 'Option D' }
        ];
      }
      
      // Shuffle options to prevent correct answer from always being first
      for (let i = optionsData.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [optionsData[i], optionsData[j]] = [optionsData[j], optionsData[i]];
      }
      
      let correctIndex = 0;
      const correctId = item.rubric?.correct_criteria?.selected_option_id;
      
      if (correctId) {
        const foundIndex = optionsData.findIndex(o => o.id === correctId);
        if (foundIndex !== -1) {
          correctIndex = foundIndex;
        }
      }

      optionsData.forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = 'btn-option';
        
        let optHtml = `<span>${opt.text}</span>`;
        if (opt.assetUri) {
          const uri = resolveAssetUrl(opt.assetUri);
          optHtml = `<div style="display:flex; flex-direction:column; align-items:center; gap:6px;">
            <img src="${uri}" alt="Option ${opt.text}" style="height:35px; min-height: 35px; min-width: 35px; max-width:80px; object-fit:contain;" />
            <span style="font-size:1.2em; font-weight:bold;">${opt.text}</span>
          </div>`;
        }
        btn.innerHTML = optHtml;
        btn.onclick = () => this.handleAnswer(idx, correctIndex, btn);
        options.appendChild(btn);
      });

      // Record presentation in persistent audit log
      try {
        const correctOptText = optionsData[correctIndex]?.text || '';
        const currentKid = (this.app?.profileSwitcher?.getCurrentPlayerName() || 'default_player').toLowerCase().trim();
        const currentSessionId = this.currentSession[0]?.session_id || `sess_${Date.now()}`;
        QuestionPresentationLog.recordPresentation({
          kidName: currentKid,
          sessionId: currentSessionId,
          taskIndex: this.currentTaskIndex + 1,
          totalSessionTasks: this.currentSession.length,
          domainId: taskRequest.domain_id || item?.domain_id || 'UNKNOWN',
          subskillId: taskRequest.target_subskill_id || item?.target_subskill_id || 'UNKNOWN',
          cognitiveDepth: depth,
          itemId: item?.item_id || 'UNKNOWN',
          promptText: item?.prompt_structure?.display_text || '',
          options: optionsData.map(o => ({ id: o.id, text: o.text })),
          correctOptionId: item?.rubric?.correct_criteria?.selected_option_id || `opt_${correctIndex + 1}`,
          correctOptionText: correctOptText
        });
      } catch (e) {
        console.error("[TaskRunner] Failed to log presentation:", e);
      }
    }
  }

  private handleAnswer(selectedIndex: number, correctIndex: number, btnElement: HTMLButtonElement) {
    const isCorrect = selectedIndex === correctIndex;
    const kidName = (this.app?.profileSwitcher?.getCurrentPlayerName() || 'default_player').toLowerCase().trim();
    this.assessmentEngine.setKidId(kidName);
    
    const item = this.currentSession[this.currentTaskIndex].question_item;
    if (item) {
      // Audit log the kid's answer
      try {
        const currentSessionId = this.currentSession[0]?.session_id || `sess_${Date.now()}`;
        const selectedText = btnElement.textContent?.trim() || '';
        QuestionPresentationLog.recordAnswer(
          kidName,
          currentSessionId,
          this.currentTaskIndex + 1,
          selectedText,
          isCorrect
        );
      } catch (e) {}

      this.assessmentEngine.recordAttempt(item.target_subskill_id, isCorrect, item.evidence_archetype);
      this.telemetry.trackEvent('TASK_ANSWERED', {
        subskill_id: item.target_subskill_id,
        isCorrect: isCorrect,
        archetype: item.evidence_archetype
      });

      // Update domain counts dynamically for rolling deficit balancing per kid and globally
      try {
        const domainCounts = JSON.parse(localStorage.getItem(`alp_${kidName}_domain_counts`) || localStorage.getItem('alp_domain_counts') || '{}');
        domainCounts[item.domain_id] = (domainCounts[item.domain_id] || 0) + 1;
        localStorage.setItem(`alp_${kidName}_domain_counts`, JSON.stringify(domainCounts));
        localStorage.setItem('alp_domain_counts', JSON.stringify(domainCounts));

        // Mark item as seen immediately in kid-specific cooldown and global set
        const currentSessionId = this.currentSession[0]?.session_id || `sess_${Date.now()}`;
        const promptText = item.prompt_structure?.display_text;
        RepetitionGuard.recordSession(kidName, currentSessionId, [item.item_id], promptText ? [promptText] : []);

        const seen = JSON.parse(localStorage.getItem('alp_seen_items') || '[]');
        if (!seen.includes(item.item_id)) {
          seen.push(item.item_id);
          localStorage.setItem('alp_seen_items', JSON.stringify(seen));
        }
      } catch (e) {}
    }
    
    if (isCorrect) {
      const options = this.container.querySelector('#options-container');
      if (options) {
        const allBtns = options.querySelectorAll('.btn-option') as NodeListOf<HTMLButtonElement>;
        allBtns.forEach(b => b.disabled = true);
      }
      btnElement.classList.add('correct');
      setTimeout(() => {
        this.currentTaskIndex++;
        this.renderTask();
      }, 1000);
    } else {
      this.currentTaskWrongAttempts++;
      this.sessionErrors++;
      btnElement.classList.add('incorrect');
      btnElement.disabled = true;

      const hint = this.container.querySelector('#scaffolding-hint');

      if (this.currentTaskWrongAttempts === 1) {
        // First wrong attempt: show only neutral "Try again!" with no hint text
        console.log('[TaskRunner] First wrong attempt on task: showing neutral "Try again!".');
        if (hint) {
          hint.textContent = 'Try again!';
          hint.classList.remove('hidden');
        }
      } else {
        // Second (or subsequent) wrong attempt on the same task: show scaffolding hint (if valid)
        console.log('[TaskRunner] Second wrong attempt on task: displaying scaffolding hint.');
        if (hint) {
          if (this.currentValidHint) {
            hint.textContent = this.currentValidHint;
            hint.classList.remove('hidden');
          } else {
            hint.classList.add('hidden');
          }
        }

        const options = this.container.querySelector('#options-container');
        if (options) {
          const allBtns = options.querySelectorAll('.btn-option') as NodeListOf<HTMLButtonElement>;
          allBtns.forEach(b => b.disabled = true);
        }

        // Graceful failure routing: Move to the next question after 2.5 seconds
        setTimeout(() => {
          btnElement.classList.remove('incorrect');
          this.currentTaskIndex++;
          this.renderTask();
        }, 2500);
      }
    }
  }

  private finishSession() {
    this.cancelSpeech();
    this.container.classList.remove('active');
    const kidName = (this.app?.profileSwitcher?.getCurrentPlayerName() || 'default_player').toLowerCase().trim();
    
    // Save seen items and prompts to prevent repetition across sessions
    try {
      const currentSessionId = this.currentSession[0]?.session_id || `sess_${Date.now()}`;
      const newSeen = this.currentSession.map(t => t.question_item?.item_id).filter(Boolean) as string[];
      const newPrompts = this.currentSession.map(t => t.question_item?.prompt_structure?.display_text).filter(Boolean) as string[];
      RepetitionGuard.recordSession(kidName, currentSessionId, newSeen, newPrompts);

      const seenItems = JSON.parse(localStorage.getItem('alp_seen_items') || '[]');
      const combined = Array.from(new Set([...seenItems, ...newSeen]));
      localStorage.setItem('alp_seen_items', JSON.stringify(combined));
    } catch (e) {
      console.error(e);
    }

    let celebrationHTML = '';
    
    // Read kid-specific progress (with fallback to global)
    const currentNodes = parseInt(
      localStorage.getItem(`alp_${kidName}_nodes_completed`) ||
      localStorage.getItem('alp_nodes_completed') || '0',
      10
    );
    const currentStars = parseInt(
      localStorage.getItem(`alp_${kidName}_stars`) ||
      localStorage.getItem('alp_stars') || '0',
      10
    );

    if (this.sessionErrors === 0) {
      // Flawless session: All correct answers!
      // Strictly advance +1 node (step-by-step path) and award 2 stars!
      const nodesToAdd = 1;
      const starsToAdd = 2;
      const nextNodes = currentNodes + nodesToAdd;
      const newStars = currentStars + starsToAdd;

      localStorage.setItem(`alp_${kidName}_nodes_completed`, nextNodes.toString());
      localStorage.setItem('alp_nodes_completed', nextNodes.toString());
      localStorage.setItem(`alp_${kidName}_stars`, newStars.toString());
      localStorage.setItem('alp_stars', newStars.toString());
      
      const starBadge = document.getElementById('player-stars');
      if (starBadge) {
        starBadge.textContent = `⭐ ${newStars}`;
      }

      soundFX.playStar();

      // Record daily quest progress
      const questStatus = DailyQuestManager.recordSessionCompleted(kidName);
      if (questStatus.justCompleted) {
        const bonusStars = 3;
        const currentStarsNow = parseInt(localStorage.getItem(`alp_${kidName}_stars`) || '0', 10);
        const starsWithBonus = currentStarsNow + bonusStars;
        localStorage.setItem(`alp_${kidName}_stars`, starsWithBonus.toString());
        localStorage.setItem('alp_stars', starsWithBonus.toString());
        const starBadge = document.getElementById('player-stars');
        if (starBadge) {
          starBadge.textContent = `⭐ ${starsWithBonus}`;
        }
        soundFX.playFanfare();
      }

      // Check if this step completed the full realm path
      const oldRealm = Math.floor(currentNodes / MapScreen.NODES_PER_MAP);
      const newRealm = Math.floor(nextNodes / MapScreen.NODES_PER_MAP);
      const isRealmComplete = newRealm > oldRealm || (nextNodes % MapScreen.NODES_PER_MAP === 0);

      if (isRealmComplete && this.app && this.app.mapScreen) {
        // Grand realm completion: Fairy Castle upgrade & Grand Treasure ceremony
        this.app.mapScreen.showRealmCompletion(oldRealm, nextNodes, () => {
          this.app.mapScreen.onShow();
        });
        return; // Skip standard small toast
      }

      const questPill = questStatus.justCompleted
        ? `<div class="quest-progress-pill" style="margin-top: 10px; font-size: 1em; color: #ffffff; font-weight: bold; background: linear-gradient(135deg, #10b981, #059669); padding: 8px 16px; border-radius: 20px; display: inline-block; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);">
            🏆 Daily Quest Conquered (3/3)! +3 Bonus Stars ⭐⭐⭐
          </div>`
        : `<div class="quest-progress-pill" style="margin-top: 10px; font-size: 0.95em; color: #fde047; font-weight: bold; background: rgba(0,0,0,0.4); padding: 6px 14px; border-radius: 20px; display: inline-block;">
            Daily Quest: ${questStatus.count} / ${questStatus.target} 🎯
          </div>`;

      // Regular node completion: Flawless Mastery (+1 node, 2 stars)
      const localProgress = (nextNodes % MapScreen.NODES_PER_MAP) || MapScreen.NODES_PER_MAP;
      celebrationHTML = `
        <div class="celebration-content">
          <div class="celebration-stars">⭐ ⭐</div>
          <h2>Flawless Mastery!</h2>
          <p>Super fast learner! All correct answers earned <strong>2 Stars</strong> and unlocked the next path node!</p>
          <div class="path-progress-pill" style="margin-top: 15px; font-size: 1.1em; color: #facc15; font-weight: bold; background: rgba(0,0,0,0.4); padding: 8px 16px; border-radius: 20px; display: inline-block;">
            Path Progress: Step ${localProgress} of ${MapScreen.NODES_PER_MAP} 🌟 (+1 Step)
          </div>
          <br/>
          ${questPill}
        </div>
      `;

      if (this.app && this.app.mapScreen) {
        this.app.mapScreen.onShow();
      }
    } else if (this.sessionErrors === 1) {
      // Standard progression: 1 mistake, still passes with 1 node advance and 1 star
      const nextNodes = currentNodes + 1;
      const newStars = currentStars + 1;

      localStorage.setItem(`alp_${kidName}_nodes_completed`, nextNodes.toString());
      localStorage.setItem('alp_nodes_completed', nextNodes.toString());
      localStorage.setItem(`alp_${kidName}_stars`, newStars.toString());
      localStorage.setItem('alp_stars', newStars.toString());
      
      const starBadge = document.getElementById('player-stars');
      if (starBadge) {
        starBadge.textContent = `⭐ ${newStars}`;
      }

      soundFX.playStar();

      // Record daily quest progress
      const questStatus = DailyQuestManager.recordSessionCompleted(kidName);
      if (questStatus.justCompleted) {
        const bonusStars = 3;
        const currentStarsNow = parseInt(localStorage.getItem(`alp_${kidName}_stars`) || '0', 10);
        const starsWithBonus = currentStarsNow + bonusStars;
        localStorage.setItem(`alp_${kidName}_stars`, starsWithBonus.toString());
        localStorage.setItem('alp_stars', starsWithBonus.toString());
        const starBadge = document.getElementById('player-stars');
        if (starBadge) {
          starBadge.textContent = `⭐ ${starsWithBonus}`;
        }
        soundFX.playFanfare();
      }

      const isRealmComplete = (nextNodes % MapScreen.NODES_PER_MAP === 0);
      if (isRealmComplete && this.app && this.app.mapScreen) {
        const realmIndex = Math.floor(currentNodes / MapScreen.NODES_PER_MAP);
        this.app.mapScreen.showRealmCompletion(realmIndex, nextNodes, () => {
          this.app.mapScreen.onShow();
        });
        return;
      }

      const questPill = questStatus.justCompleted
        ? `<div class="quest-progress-pill" style="margin-top: 10px; font-size: 1em; color: #ffffff; font-weight: bold; background: linear-gradient(135deg, #10b981, #059669); padding: 8px 16px; border-radius: 20px; display: inline-block; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);">
            🏆 Daily Quest Conquered (3/3)! +3 Bonus Stars ⭐⭐⭐
          </div>`
        : `<div class="quest-progress-pill" style="margin-top: 10px; font-size: 0.95em; color: #fde047; font-weight: bold; background: rgba(0,0,0,0.4); padding: 6px 14px; border-radius: 20px; display: inline-block;">
            Daily Quest: ${questStatus.count} / ${questStatus.target} 🎯
          </div>`;

      const localProgress = (nextNodes % MapScreen.NODES_PER_MAP);
      celebrationHTML = `
        <div class="celebration-content">
          <div class="celebration-stars">⭐</div>
          <h2>Step Completed!</h2>
          <p>Great effort! You earned a new star!</p>
          <div class="path-progress-pill" style="margin-top: 15px; font-size: 1.1em; color: #facc15; font-weight: bold; background: rgba(0,0,0,0.4); padding: 8px 16px; border-radius: 20px; display: inline-block;">
            Path Progress: Step ${localProgress} of ${MapScreen.NODES_PER_MAP} 🌟
          </div>
          <br/>
          ${questPill}
        </div>
      `;

      if (this.app && this.app.mapScreen) {
        this.app.mapScreen.onShow();
      }
    } else {
      // Imperfect session (2+ mistakes): strict gating, encourage practice
      celebrationHTML = `
        <div class="celebration-content" style="background: rgba(255,255,255,0.95); border: 2px solid #3498db;">
          <div class="celebration-stars" style="color: #3498db;">💡</div>
          <h2 style="color: #2c3e50;">Keep Practicing!</h2>
          <p style="color: #34495e;">You made a few mistakes. Let's try another path on the map!</p>
        </div>
      `;
    }

    // Show custom celebration overlay
    const overlay = document.createElement('div');
    overlay.className = 'celebration-overlay';
    overlay.innerHTML = celebrationHTML;
    document.body.appendChild(overlay);

    // Auto-remove after 3 seconds
    setTimeout(() => {
      if (document.body.contains(overlay)) {
        overlay.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
          if (document.body.contains(overlay)) {
            document.body.removeChild(overlay);
          }
        }, 300);
      }
    }, 3000);
  }
}
