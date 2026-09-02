import { App } from '../app';

export const UNLOCKED_STICKERS = ['🐉', '💎', '🍄', '✨', '🏰', '🛡️', '⚔️'];

export class ToyboxScreen {
  private container: HTMLElement;
  private app: App;

  constructor(app: App) {
    this.app = app;
    this.container = document.getElementById('screen-sandbox') as HTMLElement;
  }

  public render() {
    this.container.innerHTML = `
      <header>
        <h2>Treasures</h2>
        <button id="btn-back-map-sandbox" class="header-btn">Back to Map</button>
      </header>
      <div class="treasures-layout">
        <div class="treasure-grid" id="treasure-grid-container">
           <!-- Grid injected here -->
        </div>
      </div>
    `;

    this.bindEvents();
    this.renderGrid();
  }

  private bindEvents() {
    const btnBack = this.container.querySelector('#btn-back-map-sandbox');
    if (btnBack) {
      btnBack.addEventListener('click', () => {
        this.app.showScreen('screen-map');
      });
    }
  }

  private renderGrid() {
    const grid = this.container.querySelector('#treasure-grid-container');
    if (!grid) return;
    
    // Calculate how many nodes have been completed
    const nodesCompleted = parseInt(localStorage.getItem('alp_nodes_completed') || '0', 10);
    
    grid.innerHTML = '';
    
    UNLOCKED_STICKERS.forEach((emoji, idx) => {
      const isUnlocked = idx < nodesCompleted;
      
      const slot = document.createElement('div');
      slot.className = `treasure-slot ${isUnlocked ? 'unlocked' : 'locked'}`;
      
      const inner = document.createElement('div');
      inner.className = 'emoji';
      inner.textContent = emoji;
      
      slot.appendChild(inner);
      
      if (isUnlocked) {
        slot.onclick = () => {
          // Play a small animation or sound when clicking an unlocked treasure
          inner.style.animation = 'none';
          void inner.offsetWidth; // trigger reflow
          inner.style.animation = 'pulse-correct 0.5s ease';
        };
      }
      
      grid.appendChild(slot);
    });
  }
}
