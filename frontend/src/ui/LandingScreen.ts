import { App } from '../app';

export class LandingScreen {
  private container: HTMLElement;
  private app: App;

  constructor(app: App) {
    this.app = app;
    this.container = document.getElementById('screen-landing') as HTMLElement;
  }

  public render() {
    this.container.classList.add('landing-bg'); // Ensure it has the collage bg
    
    this.container.innerHTML = `
      <header class="admin-header">
         <button id="btn-parents-link" class="admin-link">Parents Area</button>
         <button id="btn-account-link" class="admin-link">Account Mgmt</button>
      </header>
      
      <div class="landing-content">
        <h1 class="glow-title">Magical Kingdom</h1>
        <p class="glow-subtitle">Choose Your Hero...</p>
        
        <div id="landing-profile-container" class="avatar-grid magical-grid">
           <!-- Rendered via JS -->
        </div>
      </div>
    `;

    this.bindEvents();
    this.renderProfile();
  }

  private bindEvents() {
    const btnParents = this.container.querySelector('#btn-parents-link');
    const btnAccount = this.container.querySelector('#btn-account-link');

    if (btnParents) {
      btnParents.addEventListener('click', () => {
        this.app.parentsDashboard.render();
        this.app.showScreen('screen-parents');
      });
    }

    if (btnAccount) {
      btnAccount.addEventListener('click', () => {
        this.app.accountScreen.render();
        this.app.showScreen('screen-account');
      });
    }
  }

  private renderProfile() {
    const container = this.container.querySelector('#landing-profile-container') as HTMLElement;
    if (!container) return;
    
    container.innerHTML = '';
    const profiles = this.app.profileSwitcher.getSavedProfiles();
    
    if (profiles.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; max-width: 480px; margin: 20px auto; color: white; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 12px;">
          <p style="font-size: 1.1em; margin-bottom: 15px;">Restore this child from your family code or a backup file.</p>
          <button id="btn-landing-to-account" class="parents-btn" style="padding: 10px 20px; font-size: 1rem; color: #27ae60; border-color: #27ae60;">Go to Account Management</button>
        </div>
      `;
      var btnToAccount = container.querySelector('#btn-landing-to-account');
      if (btnToAccount) {
        btnToAccount.addEventListener('click', () => {
          this.app.accountScreen.render();
          this.app.showScreen('screen-account');
        });
      }
      return;
    }

    // Move avatarImages import or redefine it later. For now, assuming it's available.
    // We'll hardcode paths for safety in this module until constants are set up.
    const base = import.meta.env.BASE_URL;
    const getAvatarSrc = (avatar: string) => {
      const map: Record<string, string> = {
        princess: `${base}art/princess_avatar.jpg`,
        knight: `${base}art/knight_avatar.jpg`,
        magician: `${base}art/magician_avatar.jpg`,
        explorer: `${base}art/explorer_avatar.jpg`
      };
      return map[avatar] || map['princess'];
    };

    profiles.forEach((profile: any) => {
      const card = document.createElement('div');
      card.className = 'profile-card cursor-pointer';
      card.innerHTML = `
        <img src="${getAvatarSrc(profile.avatar)}" alt="${profile.name}" class="profile-avatar-img" />
        <div class="profile-name" style="text-transform: capitalize;">${profile.name}</div>
      `;
      card.addEventListener('click', () => {
        this.app.profileSwitcher.login(profile.name, profile.avatar);
        this.app.mapScreen.updateHeader(profile.name, profile.avatar);
        this.app.showScreen('screen-map');
      });
      
      container.appendChild(card);
    });
  }
}
