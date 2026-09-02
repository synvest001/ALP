import { App } from '../app';

export class AccountScreen {
  private container: HTMLElement;
  private app: App;

  constructor(app: App) {
    this.app = app;
    this.container = document.getElementById('screen-account') as HTMLElement;
  }

  public render() {
    this.container.innerHTML = `
      <header class="parents-header">
        <div class="parents-header-title">
          <h2>Account Management</h2>
          <p>Manage saved profiles on this device.</p>
        </div>
        <button id="btn-close-account" class="parents-btn">Back</button>
      </header>
      <main style="padding: 40px; max-width: 800px; margin: 0 auto; width: 100%;">
        
        <!-- New Player Form -->
        <div class="parents-card" style="margin-bottom: 20px; text-align: center;">
          <button id="btn-show-new-player" class="btn btn-large cta-glow" style="margin-bottom: 20px;">➕ Create New Profile</button>
          <div id="new-player-form" class="hidden" style="margin-top: 10px; background: rgba(0,0,0,0.05); padding: 20px; border-radius: 15px;">
            <h2>Create New Profile</h2>
            <div class="name-entry-container">
              <input type="text" id="player-name-input" placeholder="Enter magical name..." style="padding: 10px; font-size: 1.2em; border-radius: 10px; border: 2px solid #ccc; width: 80%; max-width: 300px;" />
            </div>
            <h3 style="margin-bottom: 15px;">Select your avatar:</h3>
            <div id="profiles-container"></div>
          </div>
        </div>
        
        <div class="parents-card">
          <p style="color: #e74c3c; margin-top: 0;"><strong>Warning:</strong> Actions taken here cannot be undone.</p>
          <div id="account-profiles-list"></div>
        </div>
      </main>
    `;

    this.bindEvents();
    this.renderProfileList();
  }

  private bindEvents() {
    const btnClose = this.container.querySelector('#btn-close-account');
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

    const btnShowNewPlayer = this.container.querySelector('#btn-show-new-player');
    const newPlayerForm = this.container.querySelector('#new-player-form');
    if (btnShowNewPlayer && newPlayerForm) {
      btnShowNewPlayer.addEventListener('click', () => {
        newPlayerForm.classList.remove('hidden');
        btnShowNewPlayer.classList.add('hidden');
        this.renderNewPlayerAvatars();
      });
    }
  }

  private getAvatarSrc(avatar: string) {
    const map: Record<string, string> = {
      princess: '/art/princess_avatar.jpg',
      knight: '/art/knight_avatar.jpg',
      magician: '/art/magician_avatar.jpg',
      explorer: '/art/explorer_avatar.jpg'
    };
    return map[avatar] || map['princess'];
  }

  private renderNewPlayerAvatars() {
    const profilesContainer = this.container.querySelector('#profiles-container') as HTMLElement;
    if (!profilesContainer) return;
    
    profilesContainer.innerHTML = '';
    const avatars = this.app.profileSwitcher.getAvailableAvatars();
    
    avatars.forEach((avatar: string) => {
      const card = document.createElement('div');
      card.className = 'profile-card cursor-pointer';
      card.innerHTML = `
        <img src="${this.getAvatarSrc(avatar)}" class="profile-avatar-img" alt="${avatar}">
        <div class="profile-name" style="text-transform: capitalize;">${avatar}</div>
      `;
      card.addEventListener('click', () => {
        const nameInput = this.container.querySelector('#player-name-input') as HTMLInputElement;
        const playerName = nameInput && nameInput.value.trim() !== '' ? nameInput.value.trim() : 'Guest';
        this.app.profileSwitcher.login(playerName, avatar);
        
        // Return to landing screen so they can click their new card
        this.app.landingScreen.render();
        this.app.showScreen('screen-landing');
      });
      profilesContainer.appendChild(card);
    });
  }

  private renderProfileList() {
    const accountProfilesList = this.container.querySelector('#account-profiles-list') as HTMLElement;
    if (!accountProfilesList) return;
    
    accountProfilesList.innerHTML = '';
    const profiles = this.app.profileSwitcher.getSavedProfiles();
    
    if (profiles.length === 0) {
      accountProfilesList.innerHTML = '<p>No profiles found.</p>';
      return;
    }
    
    profiles.forEach((p: any) => {
      const item = document.createElement('div');
      item.className = 'account-list-item';
      
      item.innerHTML = `
        <div class="account-list-info">
          <img src="${this.getAvatarSrc(p.avatar)}" alt="${p.name}" />
          <span style="font-weight: bold; font-size: 1.2em; color: #2c3e50;">${p.name}</span>
        </div>
        <div style="display: flex; gap: 10px;">
          <button class="parents-btn reset-btn" data-name="${p.name}" style="border-color: #f39c12; color: #d35400;">Reset Progress</button>
          <button class="parents-btn delete-btn" data-name="${p.name}" style="border-color: #e74c3c; color: #c0392b;">Delete</button>
        </div>
      `;
      
      accountProfilesList.appendChild(item);
    });
    
    accountProfilesList.querySelectorAll('.reset-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const name = (e.target as HTMLElement).getAttribute('data-name');
        if (name && confirm(`Are you sure you want to reset all progress for ${name}? This will wipe their map and stickers.`)) {
          this.app.profileSwitcher.resetProgress(name);
          alert(`${name}'s progress has been reset.`);
          this.renderProfileList();
        }
      });
    });
    
    accountProfilesList.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const name = (e.target as HTMLElement).getAttribute('data-name');
        if (name && confirm(`DANGER: Are you sure you want to permanently delete the profile ${name}?`)) {
          this.app.profileSwitcher.deleteProfile(name);
          alert(`${name} has been deleted.`);
          this.renderProfileList();
          // Update landing screen in case the deleted profile was active
          this.app.landingScreen.render();
        }
      });
    });
  }
}
