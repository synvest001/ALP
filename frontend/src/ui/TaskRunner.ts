import { SessionComposer, TaskRequestPayload } from '../engine/AdaptiveEngine';
import { AssessmentEngine } from '../engine/AssessmentEngine';
import { RepetitionGuard } from '../engine/RepetitionGuard';
import { TelemetryQueue } from '../storage/telemetry_queue';
import { MapScreen } from './MapScreen';
import { soundFX } from '../utils/SoundFX';
import { resolveAssetUrl } from '../utils/assets';
import { DailyQuestManager } from '../engine/DailyQuestManager';
import { QuestionPresentationLog } from '../storage/QuestionPresentationLog';

export class TaskRunner {
  private container: HTMLElement;
  private currentSession: TaskRequestPayload[] = [];
  private currentTaskIndex = 0;
  private sessionErrors = 0;
  private composer: SessionComposer;
  private assessmentEngine: AssessmentEngine;
  private telemetry: TelemetryQueue;

  private app: any;

  constructor(_app: any) {
    this.app = _app;
    this.container = document.getElementById('modal-task-runner') as HTMLElement;
    this.composer = new SessionComposer();
    this.assessmentEngine = new AssessmentEngine();
    this.telemetry = new TelemetryQueue();
  }

  public render() {
    this.container.innerHTML = `
      <div class="modal-content task-modal-content">
        <header class="task-header">
          <div class="quest-status" id="task-progress-indicator">Task 1 of X</div>
          <button id="btn-quit-task" class="btn btn-small">Quit</button>
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
      </div>
    `;

    this.bindEvents();
  }

  private bindEvents() {
    const btnQuit = this.container.querySelector('#btn-quit-task');
    if (btnQuit) {
      btnQuit.addEventListener('click', () => {
        this.container.classList.remove('active');
      });
    }
  }

  public async startSession(sessionData?: TaskRequestPayload[], focusedDomain?: string) {
    const kidName = this.app?.profileSwitcher?.getCurrentPlayerName() || 'default_player';
    await this.composer.ensureReady();

    // If not provided, dynamically compose using AdaptiveEngine
    if (sessionData && sessionData.length > 0) {
      this.currentSession = RepetitionGuard.validateAndEnforce(sessionData, kidName, this.composer.questionBank);
    } else {
      this.currentSession = this.composer.generateSession(kidName, focusedDomain);
    }
    
    this.currentTaskIndex = 0;
    this.sessionErrors = 0;
    this.container.classList.add('active');
    this.renderTask();
  }

  private renderTask() {
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
    
    if (hint) {
      hint.classList.add('hidden');
      hint.textContent = item?.scaffolding_protocol?.level_1_reflection_prompt?.prompt || 'Try again!';
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
    
    const options = this.container.querySelector('#options-container');
    if (options) {
      const allBtns = options.querySelectorAll('.btn-option') as NodeListOf<HTMLButtonElement>;
      allBtns.forEach(b => b.disabled = true);
    }
    
    if (isCorrect) {
      btnElement.classList.add('correct');
      setTimeout(() => {
        this.currentTaskIndex++;
        this.renderTask();
      }, 1000);
    } else {
      this.sessionErrors++;
      btnElement.classList.add('incorrect');
      const hint = this.container.querySelector('#scaffolding-hint');
      if (hint) hint.classList.remove('hidden');
      
      // Graceful failure routing: Move to the next question after 2.5 seconds
      setTimeout(() => {
        btnElement.classList.remove('incorrect');
        this.currentTaskIndex++;
        this.renderTask();
      }, 2500);
    }
  }

  private finishSession() {
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
