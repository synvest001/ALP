import { App } from '../app';
import { GRAND_TREASURES, Treasure } from '../data/Treasures';
import { soundFX } from '../utils/SoundFX';

// Backwards compatibility export
export const UNLOCKED_STICKERS = GRAND_TREASURES.map(t => t.name);

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
        <div class="header-titles">
          <h2>💎 Realm Treasures & Stickers</h2>
          <span class="header-subtitle">Earn grand treasures by completing magical kingdom paths!</span>
        </div>
        <div class="header-actions">
          <button id="btn-back-map-sandbox" class="header-btn">🗺️ Back to Map</button>
        </div>
      </header>
      <div class="treasures-layout">
        <div class="treasure-grid" id="treasure-grid-container">
           <!-- Grid injected here -->
        </div>
      </div>
      <div id="treasure-detail-modal" class="treasure-modal hidden">
        <div class="treasure-modal-card">
          <button id="btn-close-treasure" class="btn-close-modal">✕</button>
          <div id="treasure-modal-content"></div>
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

    const btnClose = this.container.querySelector('#btn-close-treasure');
    const modal = this.container.querySelector('#treasure-detail-modal');
    if (btnClose && modal) {
      btnClose.addEventListener('click', () => {
        modal.classList.add('hidden');
      });
    }
  }

  public renderGrid() {
    const grid = this.container.querySelector('#treasure-grid-container');
    if (!grid) return;
    
    // Each realm is 5 nodes
    const kidName = (this.app?.profileSwitcher?.getCurrentPlayerName() || 'default_player').toLowerCase().trim();
    const nodesCompleted = parseInt(
      localStorage.getItem(`alp_${kidName}_nodes_completed`) ||
      localStorage.getItem('alp_nodes_completed') || '0',
      10
    );
    const realmsCompleted = Math.floor(nodesCompleted / 5);
    
    grid.innerHTML = '';
    
    GRAND_TREASURES.forEach((treasure, idx) => {
      const isUnlocked = idx < realmsCompleted;
      
      const card = document.createElement('div');
      card.className = `treasure-card ${isUnlocked ? 'unlocked' : 'locked'}`;
      card.setAttribute('data-rarity', treasure.rarity.toLowerCase());
      
      card.innerHTML = `
        <div class="treasure-badge ${treasure.rarity.toLowerCase()}">${treasure.rarity}</div>
        <div class="treasure-art-container">
          ${isUnlocked ? treasure.svg : `
            <div class="locked-icon-placeholder">
              <span class="lock-symbol">🔒</span>
            </div>
          `}
        </div>
        <div class="treasure-info">
          <h3 class="treasure-title">${isUnlocked ? treasure.name : 'Mystery Treasure'}</h3>
          <p class="treasure-realm">${isUnlocked ? 'From ' + treasure.realm : 'Realm ' + (idx + 1) + ': ' + treasure.realm}</p>
        </div>
      `;
      
      if (isUnlocked) {
        card.addEventListener('click', () => {
          soundFX.playTreasureUnlock();
          this.showTreasureDetail(treasure);
        });
      }
      
      grid.appendChild(card);
    });
  }

  private showTreasureDetail(treasure: Treasure) {
    const modal = this.container.querySelector('#treasure-detail-modal');
    const content = this.container.querySelector('#treasure-modal-content');
    if (!modal || !content) return;

    content.innerHTML = `
      <div class="detail-art-wrap">
        ${treasure.svg}
      </div>
      <div class="treasure-badge ${treasure.rarity.toLowerCase()} large">${treasure.rarity}</div>
      <h2 class="detail-title">${treasure.name}</h2>
      <p class="detail-realm">Discovered in <strong>${treasure.realm}</strong></p>
      <div class="detail-desc-box">
        <p>${treasure.description}</p>
      </div>
    `;

    modal.classList.remove('hidden');
  }
}
