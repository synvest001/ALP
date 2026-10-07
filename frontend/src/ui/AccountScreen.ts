import { App } from '../app';
import { SyncEngine, syncCurrentPlayer, FamilyKid } from '../engine/SyncEngine';

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

        <!-- Sync across devices -->
        <div class="parents-card" style="margin-bottom: 20px;">
          <h3 style="margin-top: 0; margin-bottom: 8px;">Sync across devices</h3>
          <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 15px;">Use a family code to sync progress across multiple devices.</p>
          <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 12px; flex-wrap: wrap;">
            <input type="text" id="family-code-input" placeholder="Family code" value="${SyncEngine.getFamilyCode()}" style="padding: 8px 12px; font-size: 1rem; border-radius: 8px; border: 2px solid #ccc; flex: 1; min-width: 180px; max-width: 300px;" />
            <button id="btn-save-family-code" class="parents-btn" style="padding: 8px 16px;">Save code</button>
            <button id="btn-list-kids" class="parents-btn" style="padding: 8px 16px;">Show children in this family</button>
          </div>
          <div id="sync-status" style="font-size: 0.9rem; color: #475569; margin-bottom: 10px; min-height: 1.2em;"></div>
          <div id="family-kids-list"></div>
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

    const syncStatusEl = this.container.querySelector('#sync-status') as HTMLElement | null;
    const btnSaveCode = this.container.querySelector('#btn-save-family-code') as HTMLButtonElement | null;
    const btnListKids = this.container.querySelector('#btn-list-kids') as HTMLButtonElement | null;
    const familyCodeInput = this.container.querySelector('#family-code-input') as HTMLInputElement | null;
    const familyKidsList = this.container.querySelector('#family-kids-list') as HTMLElement | null;

    if (!SyncEngine.endpointConfigured()) {
      if (syncStatusEl) syncStatusEl.textContent = 'Sync is not set up yet.';
      if (btnSaveCode) btnSaveCode.disabled = true;
      if (btnListKids) btnListKids.disabled = true;
    }

    if (btnSaveCode && familyCodeInput) {
      btnSaveCode.addEventListener('click', () => {
        const code = familyCodeInput.value;
        SyncEngine.setFamilyCode(code);
        if (syncStatusEl) syncStatusEl.textContent = 'Family code saved.';
      });
    }

    if (btnListKids) {
      btnListKids.addEventListener('click', () => {
        if (syncStatusEl) syncStatusEl.textContent = 'Checking family...';
        SyncEngine.listKids().then((res) => {
          if (!res.ok) {
            if (syncStatusEl) syncStatusEl.textContent = res.message;
            if (familyKidsList) familyKidsList.innerHTML = '';
            return;
          }
          if (syncStatusEl) syncStatusEl.textContent = '';
          if (!familyKidsList) return;
          familyKidsList.innerHTML = '';
          if (!res.kids || res.kids.length === 0) {
            familyKidsList.innerHTML = '<p style="color: #64748b; font-size: 0.9rem; margin-top: 8px;">No children found for this code yet.</p>';
            return;
          }
          res.kids.forEach((kid: FamilyKid) => {
            const row = document.createElement('div');
            row.className = 'account-list-item';
            row.style.marginTop = '8px';
            row.innerHTML = `
              <div class="account-list-info">
                <img src="${this.getAvatarSrc(kid.avatar || 'princess')}" alt="${kid.name}" />
                <span style="font-weight: bold; font-size: 1.1em; color: #2c3e50;">${kid.name}</span>
              </div>
              <button class="parents-btn btn-add-device" style="border-color: #27ae60; color: #27ae60;">Add to this device</button>
            `;
            const btnAdd = row.querySelector('.btn-add-device');
            if (btnAdd) {
              btnAdd.addEventListener('click', () => {
                this.app.profileSwitcher.login(kid.name, kid.avatar || 'princess');
                this.renderProfileList();
                if (syncStatusEl) syncStatusEl.textContent = 'Syncing ' + kid.name + '...';
                syncCurrentPlayer(this.app).then((syncRes) => {
                  if (syncStatusEl) syncStatusEl.textContent = syncRes.message;
                  this.renderProfileList();
                });
              });
            }
            familyKidsList.appendChild(row);
          });
        });
      });
    }
  }

  private getAvatarSrc(avatar: string) {
    const base = import.meta.env.BASE_URL;
    const map: Record<string, string> = {
      princess: `${base}art/princess_avatar.jpg`,
      knight: `${base}art/knight_avatar.jpg`,
      magician: `${base}art/magician_avatar.jpg`,
      explorer: `${base}art/explorer_avatar.jpg`
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
          SyncEngine.bumpEpoch(name);
          const clean = name.toLowerCase().trim();
          const epoch = localStorage.getItem(`alp_${clean}_sync_epoch`);
          const updated = localStorage.getItem(`alp_${clean}_sync_updated`);
          this.app.profileSwitcher.resetProgress(name);
          if (epoch !== null) localStorage.setItem(`alp_${clean}_sync_epoch`, epoch);
          if (updated !== null) localStorage.setItem(`alp_${clean}_sync_updated`, updated);
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
