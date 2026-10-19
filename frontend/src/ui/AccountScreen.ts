import { App } from '../app';
import { SyncEngine, syncCurrentPlayer, FamilyKid } from '../engine/SyncEngine';
import { EventLog } from '../engine/EventLog';
import {
  exportBackup,
  restoreBackup,
  isWebCryptoAvailable,
  decryptPayload
} from '../engine/BackupRestore';

export class AccountScreen {
  private container: HTMLElement;
  private app: App;

  constructor(app: App) {
    this.app = app;
    this.container = document.getElementById('screen-account') as HTMLElement;
  }

  public render() {
    const currentKid = (this.app?.profileSwitcher?.getCurrentPlayerName() || 'default_player').toLowerCase().trim();
    const isLargeLog = EventLog.isOver3MB(currentKid);
    const logBytes = EventLog.getTotalBytes(currentKid);
    const logMB = (logBytes / (1024 * 1024)).toFixed(1);
    const largeLogNotice = isLargeLog
      ? `<div class="parents-card" style="margin-bottom: 20px; background: #fefce8; border: 1px solid #fef08a; color: #713f12;">
           <p style="margin: 0; font-size: 0.95rem;">Notice: Saved progress events on this device are large (~${logMB} MB). Tip: sync or export now and then so progress is backed up.</p>
         </div>`
      : '';

    this.container.innerHTML = `
      <header class="parents-header">
        <div class="parents-header-title">
          <h2>Account Management</h2>
          <p>Manage saved profiles on this device.</p>
        </div>
        <button id="btn-close-account" class="parents-btn">Back</button>
      </header>
      <main style="padding: 40px; max-width: 800px; margin: 0 auto; width: 100%;">
        ${largeLogNotice}
        
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

        <!-- Backup & Restore -->
        <div class="parents-card" style="margin-bottom: 20px;">
          <h3 style="margin-top: 0; margin-bottom: 8px;">Backup & Restore</h3>
          <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 15px;">Tip: sync or export now and then so progress is backed up.</p>
          
          <!-- Export Section -->
          <div style="background: rgba(0,0,0,0.02); padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 15px;">
            <h4 style="margin-top: 0; margin-bottom: 10px;">Export Backup</h4>
            <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px; flex-wrap: wrap;">
              <select id="export-kid-select" style="padding: 8px 12px; font-size: 1rem; border-radius: 8px; border: 2px solid #ccc; min-width: 160px;"></select>
              <input type="password" id="export-passphrase-input" placeholder="Passphrase (optional)" style="padding: 8px 12px; font-size: 1rem; border-radius: 8px; border: 2px solid #ccc; flex: 1; min-width: 160px; max-width: 250px;" />
              <button id="btn-export-backup" class="parents-btn" style="padding: 8px 16px;">Export Backup</button>
            </div>
            <div id="export-notice" style="font-size: 0.85rem; color: #64748b; margin-bottom: 8px; min-height: 1.2em;"></div>
            <textarea id="export-text-output" readonly rows="4" placeholder="Exported backup data will appear here..." style="width: 100%; box-sizing: border-box; font-family: monospace; font-size: 0.85rem; padding: 8px; border-radius: 8px; border: 1px solid #ccc; margin-bottom: 8px;"></textarea>
            <div>
              <button id="btn-select-all-export" class="parents-btn" style="padding: 6px 12px; font-size: 0.85rem;">Select all</button>
            </div>
          </div>

          <!-- Restore Section -->
          <div style="background: rgba(0,0,0,0.02); padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0;">
            <h4 style="margin-top: 0; margin-bottom: 10px;">Restore Backup</h4>
            <div style="margin-bottom: 10px;">
              <input type="file" id="restore-file-input" accept=".json,text/plain" style="margin-bottom: 8px;" />
            </div>
            <textarea id="restore-text-input" placeholder="Or paste backup data here..." rows="4" style="width: 100%; box-sizing: border-box; font-family: monospace; font-size: 0.85rem; padding: 8px; border-radius: 8px; border: 1px solid #ccc; margin-bottom: 8px;"></textarea>
            <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 8px; flex-wrap: wrap;">
              <input type="password" id="restore-passphrase-input" placeholder="Passphrase (if encrypted)" style="padding: 8px 12px; font-size: 1rem; border-radius: 8px; border: 2px solid #ccc; flex: 1; min-width: 160px; max-width: 250px;" />
              <button id="btn-restore-backup" class="parents-btn" style="padding: 8px 16px; border-color: #27ae60; color: #27ae60;">Restore Backup</button>
            </div>
            <div id="restore-status" style="font-size: 0.9rem; min-height: 1.2em; color: #2c3e50;"></div>
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
    this.renderExportKidOptions();
  }

  private renderExportKidOptions() {
    const select = this.container.querySelector('#export-kid-select') as HTMLSelectElement | null;
    if (!select) return;

    select.innerHTML = '';
    const profiles = this.app.profileSwitcher.getSavedProfiles();
    const currentName = this.app.profileSwitcher.getCurrentPlayerName() || '';

    if (profiles.length === 0) {
      const opt = document.createElement('option');
      opt.value = 'default_player';
      opt.textContent = 'default_player';
      select.appendChild(opt);
      return;
    }

    profiles.forEach((p: any) => {
      const opt = document.createElement('option');
      opt.value = p.name;
      opt.textContent = p.name;
      if (p.name.toLowerCase() === currentName.toLowerCase()) {
        opt.selected = true;
      }
      select.appendChild(opt);
    });
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
      if (syncStatusEl) syncStatusEl.textContent = "Sync isn't set up yet.";
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
            const isLocal = this.app.profileSwitcher.getSavedProfiles().some(
              (p: any) => p.name.toLowerCase() === kid.name.toLowerCase()
            );

            if (kid.tombstoned) {
              if (isLocal) {
                const row = document.createElement('div');
                row.className = 'account-list-item';
                row.style.marginTop = '8px';
                row.innerHTML = `
                  <div class="account-list-info">
                    <img src="${this.getAvatarSrc(kid.avatar || 'princess')}" alt="${kid.name}" />
                    <span style="color: #64748b;">${kid.name} (Removed on another device)</span>
                  </div>
                  <button class="parents-btn btn-remove-tombstoned" style="border-color: #e74c3c; color: #c0392b;">Remove from this device</button>
                `;
                const btnRemove = row.querySelector('.btn-remove-tombstoned');
                if (btnRemove) {
                  btnRemove.addEventListener('click', () => {
                    if (confirm(`This child was removed on another device. Remove ${kid.name} from this device as well?`)) {
                      this.app.profileSwitcher.deleteProfile(kid.name);
                      this.renderProfileList();
                      this.renderExportKidOptions();
                      this.app.landingScreen.render();
                      row.remove();
                    }
                  });
                }
                familyKidsList.appendChild(row);
              }
              return;
            }

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
                this.renderExportKidOptions();
                if (syncStatusEl) syncStatusEl.textContent = 'Syncing...';
                syncCurrentPlayer(this.app).then((syncRes) => {
                  if (syncStatusEl) syncStatusEl.textContent = syncRes.message;
                  this.renderProfileList();
                  this.renderExportKidOptions();
                });
              });
            }
            familyKidsList.appendChild(row);
          });
        });
      });
    }

    // -------------------------------------------------------------------------
    // Backup & Restore Event Handlers
    // -------------------------------------------------------------------------
    const btnExport = this.container.querySelector('#btn-export-backup') as HTMLButtonElement | null;
    const exportKidSelect = this.container.querySelector('#export-kid-select') as HTMLSelectElement | null;
    const exportPassInput = this.container.querySelector('#export-passphrase-input') as HTMLInputElement | null;
    const exportNotice = this.container.querySelector('#export-notice') as HTMLElement | null;
    const exportTextOutput = this.container.querySelector('#export-text-output') as HTMLTextAreaElement | null;
    const btnSelectAllExport = this.container.querySelector('#btn-select-all-export') as HTMLButtonElement | null;

    if (btnExport && exportKidSelect && exportTextOutput && exportNotice) {
      btnExport.addEventListener('click', () => {
        const kid = exportKidSelect.value || 'default_player';
        const pass = exportPassInput ? exportPassInput.value : '';

        // Find display name and avatar
        const profiles = this.app.profileSwitcher.getSavedProfiles();
        let name = kid;
        let avatar = 'princess';
        for (let i = 0; i < profiles.length; i++) {
          if (profiles[i].name.toLowerCase() === kid.toLowerCase()) {
            name = profiles[i].name;
            avatar = profiles[i].avatar || 'princess';
            break;
          }
        }

        exportBackup(kid, pass, name, avatar).then((res) => {
          exportTextOutput.value = res.text;
          exportNotice.textContent = res.notice;

          // Attempt Blob download if supported
          try {
            if (typeof Blob !== 'undefined' && typeof URL !== 'undefined' && URL.createObjectURL) {
              const blob = new Blob([res.text], { type: 'application/json' });
              const a = document.createElement('a');
              a.href = URL.createObjectURL(blob);
              a.download = kid + '-alp-backup.json';
              document.body.appendChild(a);
              a.click();
              document.body.removeChild(a);
              URL.revokeObjectURL(a.href);
            }
          } catch (e) {
            // Fallback to textarea only
          }
        });
      });
    }

    if (btnSelectAllExport && exportTextOutput) {
      btnSelectAllExport.addEventListener('click', () => {
        exportTextOutput.focus();
        exportTextOutput.select();
        exportTextOutput.setSelectionRange(0, 999999);
      });
    }

    const btnRestore = this.container.querySelector('#btn-restore-backup') as HTMLButtonElement | null;
    const restoreFileInput = this.container.querySelector('#restore-file-input') as HTMLInputElement | null;
    const restoreTextInput = this.container.querySelector('#restore-text-input') as HTMLTextAreaElement | null;
    const restorePassInput = this.container.querySelector('#restore-passphrase-input') as HTMLInputElement | null;
    const restoreStatus = this.container.querySelector('#restore-status') as HTMLElement | null;

    if (btnRestore && restoreTextInput && restoreStatus) {
      btnRestore.addEventListener('click', () => {
        const pass = restorePassInput ? restorePassInput.value : '';
        const applyRawJson = (rawText: string) => {
          if (!rawText || !rawText.trim()) {
            restoreStatus.textContent = 'This backup file looks damaged. Nothing was changed.';
            return;
          }

          let parsed: any = null;
          try {
            parsed = JSON.parse(rawText.trim());
          } catch (ex) {
            restoreStatus.textContent = 'This backup file looks damaged. Nothing was changed.';
            return;
          }

          if (parsed && parsed.encrypted === true) {
            if (!isWebCryptoAvailable()) {
              restoreStatus.textContent = 'This backup file is encrypted, but password decryption is not supported on this device. Nothing was changed.';
              return;
            }
            if (!pass) {
              restoreStatus.textContent = 'Please enter the passphrase to restore this backup.';
              return;
            }
            decryptPayload(parsed, pass)
              .then((decryptedPayload) => {
                this.executeRestore(decryptedPayload, restoreStatus, restoreTextInput, restoreFileInput);
              })
              .catch(() => {
                restoreStatus.textContent = 'This backup file looks damaged. Nothing was changed.';
              });
            return;
          }

          this.executeRestore(parsed, restoreStatus, restoreTextInput, restoreFileInput);
        };

        if (restoreFileInput && restoreFileInput.files && restoreFileInput.files[0]) {
          const file = restoreFileInput.files[0];
          const reader = new FileReader();
          reader.onload = (evt: any) => {
            const content = evt && evt.target ? evt.target.result : '';
            applyRawJson(content);
          };
          reader.onerror = () => {
            restoreStatus.textContent = 'This backup file looks damaged. Nothing was changed.';
          };
          reader.readAsText(file);
        } else {
          applyRawJson(restoreTextInput.value);
        }
      });
    }
  }

  private executeRestore(
    payload: any,
    restoreStatus: HTMLElement,
    restoreTextInput: HTMLTextAreaElement,
    restoreFileInput: HTMLInputElement | null
  ) {
    const activeKid = this.app.profileSwitcher.getCurrentPlayerName() || '';
    const res = restoreBackup(payload, Date.now(), activeKid);

    if (res.success) {
      restoreStatus.textContent = 'Everything is saved.';
      restoreTextInput.value = '';
      if (restoreFileInput) restoreFileInput.value = '';

      // Refresh screens
      this.renderProfileList();
      this.renderExportKidOptions();
      this.app.landingScreen.render();
      if (this.app.mapScreen) {
        this.app.mapScreen.render();
      }
    } else {
      restoreStatus.textContent = res.message;
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
          this.renderExportKidOptions();
        }
      });
    });
    
    accountProfilesList.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const name = (e.target as HTMLElement).getAttribute('data-name');
        if (name && confirm(`Are you sure you want to delete all data for ${name}? This will remove all local progress and server backup with no undo.`)) {
          if (SyncEngine.isConfigured()) {
            SyncEngine.deleteKid(name);
          }
          this.app.profileSwitcher.deleteProfile(name);
          this.renderProfileList();
          this.renderExportKidOptions();
          // Update landing screen in case the deleted profile was active
          this.app.landingScreen.render();
        }
      });
    });
  }
}
