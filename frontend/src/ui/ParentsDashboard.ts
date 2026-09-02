import { App } from '../app';

export class ParentsDashboard {
  private container: HTMLElement;
  private app: App;

  constructor(app: App) {
    this.app = app;
    this.container = document.getElementById('screen-parents') as HTMLElement;
  }

  public render() {
    const playerName = this.app.profileSwitcher.getCurrentPlayerName() || "Guest";
    const nodesCompleted = localStorage.getItem('alp_nodes_completed') || '0';
    
    // Per WS6 / Master Plan Section 23: No percentiles, grade levels, or single composite scores.
    this.container.innerHTML = `
      <header class="parents-header">
        <div class="parents-header-title">
          <h2>Parents Briefing <span style="color: #9b59b6; margin-left: 10px;">| ${playerName}</span></h2>
          <p>Qualitative Growth & Focus Areas</p>
        </div>
        <button id="btn-close-parents" class="parents-btn">Back to Game</button>
      </header>
      <main class="parents-grid">
        
        <!-- Activity Summary -->
        <div class="parents-card" style="grid-column: 1 / -1;">
          <h3>Activity Summary</h3>
          <div class="kpi-grid">
            <div class="kpi">
              <span class="kpi-val" id="kpi-quests">${nodesCompleted}</span>
              <span class="kpi-lbl">Milestones Completed</span>
            </div>
            <div class="kpi">
              <span class="kpi-val" id="kpi-accuracy">Developing</span>
              <span class="kpi-lbl">General Security</span>
            </div>
          </div>
        </div>
        
        <!-- Qualitative Mastery (WS6) -->
        <div class="parents-card">
          <h3>Curriculum Progression</h3>
          
          <div class="skill-row" style="margin-bottom: 15px;">
            <div class="skill-info">
              <span class="skill-name">Number Sense</span>
              <span class="skill-pct" style="color: #2ecc71;">SECURE</span>
            </div>
            <p style="font-size: 0.9em; color: #bbb; margin-top: 5px;">Consolidating foundational counting.</p>
          </div>
          
          <div class="skill-row" style="margin-bottom: 15px;">
            <div class="skill-info">
              <span class="skill-name">Spatial Logic</span>
              <span class="skill-pct" style="color: #f1c40f;">DEVELOPING</span>
            </div>
            <p style="font-size: 0.9em; color: #bbb; margin-top: 5px;">Practicing mental rotations and shapes.</p>
          </div>
          
          <div class="skill-row">
            <div class="skill-info">
              <span class="skill-name">Pattern Recognition</span>
              <span class="skill-pct" style="color: #e74c3c;">INTRODUCED</span>
            </div>
            <p style="font-size: 0.9em; color: #bbb; margin-top: 5px;">Currently exploring A-B-A repeating patterns.</p>
          </div>
        </div>
        
        <!-- Actionable Insights (WS6) -->
        <div class="parents-card">
          <h3>Real-World Connections</h3>
          <div class="insight-item">
            <strong>Current Focus: Pattern Recognition</strong>
            <p>Your child is actively working on repeating patterns. Try playing with colored blocks or sorting laundry by color and shape to reinforce this naturally at home.</p>
          </div>
        </div>
      </main>
    `;

    this.bindEvents();
  }

  private bindEvents() {
    const btnClose = this.container.querySelector('#btn-close-parents');
    if (btnClose) {
      btnClose.addEventListener('click', () => {
        // Go back to landing if no active profile, otherwise map
        if (this.app.profileSwitcher.getCurrentPlayerName()) {
          this.app.showScreen('screen-map');
        } else {
          this.app.landingScreen.render();
          this.app.showScreen('screen-landing');
        }
      });
    }
  }
}
