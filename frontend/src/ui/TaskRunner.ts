import { SessionComposer, TaskRequestPayload } from '../engine/AdaptiveEngine';
import { MockProfile } from '../engine/LearnerProfileMock';
import { UNLOCKED_STICKERS } from './ToyboxScreen';
import { AssessmentEngine } from '../engine/AssessmentEngine';
import { TelemetryQueue } from '../storage/telemetry_queue';

export class TaskRunner {
  private container: HTMLElement;
  private currentSession: TaskRequestPayload[] = [];
  private currentTaskIndex = 0;
  private sessionErrors = 0;
  private composer: SessionComposer;
  private assessmentEngine: AssessmentEngine;
  private telemetry: TelemetryQueue;

  constructor(_app: any) {
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
            <button id="btn-play-audio" class="btn-audio">🔊</button>
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

  public startSession(sessionData?: TaskRequestPayload[]) {
    // If not provided, dynamically compose using AdaptiveEngine
    if (sessionData && sessionData.length > 0) {
      this.currentSession = sessionData;
    } else {
      this.currentSession = this.composer.generateSession(MockProfile);
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
    
    if (progress) progress.textContent = `Task ${this.currentTaskIndex + 1} of ${this.currentSession.length} (${taskRequest.task_function_type})`;
    
    if (item && promptText) {
      promptText.textContent = item.prompt_structure.display_text;
    } else if (promptText) {
      promptText.textContent = "Error loading task item.";
    }

    if (visual) {
      if (item?.prompt_structure?.visual_assets && item.prompt_structure.visual_assets.length > 0) {
        const asset = item.prompt_structure.visual_assets[0];
        visual.innerHTML = `<img src="${asset.uri}" alt="Visual context" style="max-width: 100%; max-height: 350px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);" />`;
      } else {
        // For now, render a mock placeholder based on domain/representation
        visual.innerHTML = `<div class="mock-visual">[${item?.domain_id || 'UNKNOWN'}]<br/>${item?.representation_type || ''} Visual Placeholder</div>`;
      }
    }
    
    if (hint) {
      hint.classList.add('hidden');
      hint.textContent = item?.scaffolding_protocol?.level_1_reflection_prompt?.prompt || 'Try again!';
    }
    
    if (options && item) {
      options.innerHTML = '';
      
      let optionsData: { id: string, text: string }[] = [];
      const tapSelectOptions = item.interaction_model?.modality_configurations?.tap_select?.options;
      
      if (tapSelectOptions && tapSelectOptions.length > 0) {
        optionsData = tapSelectOptions.map((o: any) => ({
          id: o.option_id,
          text: o.display_value
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
        btn.textContent = opt.text;
        btn.onclick = () => this.handleAnswer(idx, correctIndex, btn);
        options.appendChild(btn);
      });
    }
  }

  private handleAnswer(selectedIndex: number, correctIndex: number, btnElement: HTMLButtonElement) {
    const isCorrect = selectedIndex === correctIndex;
    
    const item = this.currentSession[this.currentTaskIndex].question_item;
    if (item) {
      this.assessmentEngine.recordAttempt(item.target_subskill_id, isCorrect, item.evidence_archetype);
      this.telemetry.trackEvent('TASK_ANSWERED', {
        subskill_id: item.target_subskill_id,
        isCorrect: isCorrect,
        archetype: item.evidence_archetype
      });
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
    
    let celebrationHTML = '';
    
    if (this.sessionErrors === 0) {
      // Perfect session: advance progress and award star
      const currentStars = parseInt(localStorage.getItem('alp_stars') || '0', 10);
      const newStars = currentStars + 1;
      localStorage.setItem('alp_stars', newStars.toString());
      
      const currentNodes = parseInt(localStorage.getItem('alp_nodes_completed') || '0', 10);
      localStorage.setItem('alp_nodes_completed', (currentNodes + 1).toString());

      const starBadge = document.getElementById('player-stars');
      if (starBadge) {
        starBadge.textContent = `⭐ ${newStars}`;
      }

      const unlockedTreasure = UNLOCKED_STICKERS[currentNodes];
      if (unlockedTreasure) {
        celebrationHTML = `
          <div class="celebration-content">
            <div class="celebration-stars">⭐</div>
            <h2>Milestone Reached!</h2>
            <p>You earned a new star!</p>
            <div class="treasure-reveal" style="margin-top: 20px; animation: popIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);">
              <div style="font-size: 1.2em; color: #f1c40f; margin-bottom: 10px; font-weight: bold;">New Treasure Unlocked!</div>
              <div style="font-size: 4em; filter: drop-shadow(0 0 20px rgba(241, 196, 15, 0.8)); text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);">${unlockedTreasure}</div>
            </div>
          </div>
        `;
      } else {
        celebrationHTML = `
          <div class="celebration-content">
            <div class="celebration-stars">⭐</div>
            <h2>Milestone Reached!</h2>
            <p>You earned a new star!</p>
          </div>
        `;
      }
    } else {
      // Imperfect session: strict gating, no progress awarded
      celebrationHTML = `
        <div class="celebration-content" style="background: rgba(255,255,255,0.95); border: 2px solid #3498db;">
          <div class="celebration-stars" style="color: #3498db;">💡</div>
          <h2 style="color: #2c3e50;">Keep Practicing!</h2>
          <p style="color: #34495e;">You made a few mistakes. Let's try another path on the map!</p>
        </div>
      `;
    }

    // Show custom celebration overlay instead of native alert
    const overlay = document.createElement('div');
    overlay.className = 'celebration-overlay';
    overlay.innerHTML = celebrationHTML;
    document.body.appendChild(overlay);

    // Auto-remove after 4 seconds
    setTimeout(() => {
      if (document.body.contains(overlay)) {
        overlay.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => document.body.removeChild(overlay), 300);
      }
    }, 4000);
  }
}
