import { App } from '../app';
import { AssessmentEngine } from '../engine/AssessmentEngine';

export class ParentsDashboard {
  private container: HTMLElement;
  private app: App;
  private assessmentEngine: AssessmentEngine;
  private curriculumMap: any = null;
  private showAllSkills = false;

  constructor(app: App) {
    this.app = app;
    this.container = document.getElementById('screen-parents') as HTMLElement;
    this.assessmentEngine = new AssessmentEngine();
  }

  public render() {
    this.fetchCurriculumMap().then(() => this.renderDashboard());
  }

  private async fetchCurriculumMap() {
    if (!this.curriculumMap) {
      try {
        const res = await fetch('/data/curriculum_map.json');
        this.curriculumMap = await res.json();
      } catch (e) {
        console.error('Failed to load curriculum map', e);
      }
    }
  }

  private getSkillTitle(subskillId: string): string {
    if (!this.curriculumMap) return subskillId;
    for (const domain of this.curriculumMap.domains || []) {
      for (const strand of domain.strands || []) {
        for (const skill of strand.skills || []) {
          if (skill.code === subskillId) return skill.title;
        }
      }
    }
    return subskillId;
  }

  private renderDashboard() {
    const playerName = this.app.profileSwitcher.getCurrentPlayerName() || "Guest";
    const nodesCompleted = localStorage.getItem('alp_nodes_completed') || '0';
    
    const allStates = this.assessmentEngine.getAllStates();
    allStates.sort((a, b) => b.last_active - a.last_active);
    
    const displayStates = this.showAllSkills ? allStates : allStates.slice(0, 5);

    let rowsHtml = '';
    if (displayStates.length === 0) {
      rowsHtml = '<p style="color: #bbb;">No skills practiced yet. Start playing to see progress!</p>';
    } else {
      rowsHtml = displayStates.map(state => {
        const title = this.getSkillTitle(state.subskill_id);
        let color = '#e74c3c'; // INTRODUCED
        if (state.state === 'DEVELOPING') color = '#f1c40f';
        if (state.state === 'SECURE' || state.state === 'FLEXIBLE' || state.state === 'GENERALIZED') color = '#2ecc71';

        return `
          <div class="skill-row" style="margin-bottom: 15px;">
            <div class="skill-info">
              <span class="skill-name">${title}</span>
              <span class="skill-pct" style="color: ${color};">${state.state}</span>
            </div>
            <p style="font-size: 0.9em; color: #bbb; margin-top: 5px;">ID: ${state.subskill_id} | Attempts: ${state.attempts}</p>
          </div>
        `;
      }).join('');
    }

    const toggleBtnHtml = allStates.length > 5 
      ? `<button id="btn-toggle-report" class="btn btn-small" style="margin-top: 15px; width: 100%;">${this.showAllSkills ? 'View Top 5' : 'View Full Report'}</button>` 
      : '';
    
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
              <span class="kpi-val" id="kpi-accuracy">${allStates.length}</span>
              <span class="kpi-lbl">Skills Explored</span>
            </div>
          </div>
        </div>
        
        <!-- Qualitative Mastery -->
        <div class="parents-card">
          <h3>Curriculum Progression</h3>
          ${rowsHtml}
          ${toggleBtnHtml}
        </div>
        
        <!-- Actionable Insights -->
        <div class="parents-card">
          <h3>Real-World Connections</h3>
          <div class="insight-item">
            <strong>Current Focus: ${displayStates.length > 0 ? this.getSkillTitle(displayStates[0].subskill_id) : 'Exploration'}</strong>
            <p>Your child is actively working on this skill in the app. Try pointing out examples of this concept in real life to reinforce their learning naturally.</p>
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
        if (this.app.profileSwitcher.getCurrentPlayerName()) {
          this.app.showScreen('screen-map');
        } else {
          this.app.landingScreen.render();
          this.app.showScreen('screen-landing');
        }
      });
    }

    const btnToggle = this.container.querySelector('#btn-toggle-report');
    if (btnToggle) {
      btnToggle.addEventListener('click', () => {
        this.showAllSkills = !this.showAllSkills;
        this.renderDashboard();
      });
    }
  }
}
