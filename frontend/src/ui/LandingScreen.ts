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
      container.innerHTML = '<p style="color: rgba(255,255,255,0.7); font-size: 1.2em;">No hero found. Create one in Account Mgmt!</p>';
      return;
    }

    // Move avatarImages import or redefine it later. For now, assuming it's available.
    // We'll hardcode paths for safety in this module until constants are set up.
    const getAvatarSrc = (avatar: string) => {
      const map: Record<string, string> = {
        princess: '/art/princess_avatar.jpg',
        knight: '/art/knight_avatar.jpg',
        magician: '/art/magician_avatar.jpg',
        explorer: '/art/explorer_avatar.jpg'
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
