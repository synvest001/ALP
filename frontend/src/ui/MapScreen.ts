import { App } from '../app';
import { SyncEngine } from '../engine/SyncEngine';

export class MapScreen {
  private container: HTMLElement;
  private app: App;
  
  // State
  private totalNodes = 10;
  private playerNodesCompleted = 0;
  private currentPathNodes: {x: number, y: number}[] = [];
  
  private backgrounds = [
    'magical_forest.jpg',
    'crystal_cave.jpg',
    'dragon_castle.jpg',
    'mushroom_village.jpg',
    'pixie_hollow.jpg',
    'whispering_woods.jpg',
    'candy_canyon.jpg',
    'clockwork_city.jpg',
    'cloud_kingdom.jpg',
    'dinosaur_valley.jpg',
    'enchanted_library.jpg',
    'fairy_treehouse.jpg',
    'floating_islands.jpg',
    'frozen_tundra.jpg',
    'mermaid_lagoon.jpg',
    'rainbow_peaks.jpg',
    'starlight_observatory.jpg',
    'volcano_forge.jpg'
  ];
  
  constructor(app: App) {
    this.app = app;
    this.container = document.getElementById('screen-map') as HTMLElement;
  }

  public render() {
    this.container.innerHTML = `
      <header>
        <div class="avatar-display cursor-pointer" id="map-avatar-display" title="Click to Change Avatar"></div>
        <div class="header-stats">
          <div class="greeting-display" id="map-greeting"></div>
          <div class="gamification-stats">
            <span id="player-level" class="badge-level">Level 1: Novice</span>
            <span id="player-stars" class="badge-stars">⭐ ${localStorage.getItem('alp_stars') || '0'}</span>
          </div>
        </div>
        <div class="quest-status" id="map-quest-status">Daily Quest: 0 / 3</div>
        <div class="header-actions">
          <button id="btn-parents-map" class="header-btn" title="Parents Area">Parents Area</button>
          <button id="btn-goto-sandbox" class="header-btn" title="View Treasures">💎 Treasures</button>
          <button id="btn-sync" class="header-btn">Sync Data</button>
          <button id="btn-logout" class="header-btn">Home</button>
        </div>
      </header>
      
      <main class="map-container" id="map-viewport">
        <div class="map-world" id="map-world">
          <!-- Dynamic SVG Path and Nodes will be injected here -->
        </div>
      </main>
    `;

    this.bindEvents();
    this.loadState();
  }

  private loadState() {
    const savedNodes = localStorage.getItem('alp_nodes_completed');
    if (savedNodes) {
      this.playerNodesCompleted = parseInt(savedNodes, 10) || 0;
    } else {
      this.playerNodesCompleted = 0;
    }
  }

  public saveState() {
    localStorage.setItem('alp_nodes_completed', this.playerNodesCompleted.toString());
  }

  private getCurrentWorldName(): string {
    const worldIndex = Math.floor(this.playerNodesCompleted / this.totalNodes);
    const bgIndex = worldIndex % this.backgrounds.length;
    let name = this.backgrounds[bgIndex].replace('.jpg', '').replace(/_/g, ' ');
    return name.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  }

  public updateHeader(playerName: string, avatar: string) {
    const avatarDisplay = this.container.querySelector('#map-avatar-display') as HTMLElement;
    const greeting = this.container.querySelector('#map-greeting') as HTMLElement;
    
    if (avatarDisplay) {
      const getAvatarSrc = (a: string) => {
        const map: Record<string, string> = {
          princess: '/art/princess_avatar.jpg',
          knight: '/art/knight_avatar.jpg',
          magician: '/art/magician_avatar.jpg',
          explorer: '/art/explorer_avatar.jpg'
        };
        return map[a] || map['princess'];
      };
      avatarDisplay.innerHTML = `<img src="${getAvatarSrc(avatar)}" alt="Avatar" class="header-avatar-img" />`;
    }
    
    if (greeting) {
      const worldName = this.getCurrentWorldName();
      const getGreeting = (a: string, n: string) => {
        const map: Record<string, (n: string) => string> = {
          princess: (n) => `Welcome, Royal Highness ${n} to ${worldName}!`,
          knight: (n) => `Welcome, Brave Dame ${n} to ${worldName}!`, 
          magician: (n) => `Welcome, Grand Sorceress ${n} to ${worldName}!`,
          explorer: (n) => `Welcome, Intrepid Explorer ${n} to ${worldName}!`
        };
        const func = map[a] || map['princess'];
        return func(n);
      };
      greeting.textContent = getGreeting(avatar, playerName);
    }
    
    const stars = this.container.querySelector('#player-stars') as HTMLElement;
    if (stars) {
      stars.textContent = `⭐ ${localStorage.getItem('alp_stars') || '0'}`;
    }
  }

  private bindEvents() {
    const btnSandbox = this.container.querySelector('#btn-goto-sandbox');
    const btnLogout = this.container.querySelector('#btn-logout');
    const btnSync = this.container.querySelector('#btn-sync') as HTMLButtonElement;
    
    if (btnSync) {
      btnSync.addEventListener('click', async () => {
        btnSync.textContent = 'Syncing...';
        btnSync.disabled = true;
        
        const syncEngine = new SyncEngine();
        const success = await syncEngine.sync();
        
        btnSync.textContent = success ? 'Synced!' : 'Sync Failed';
        setTimeout(() => {
          btnSync.textContent = 'Sync Data';
          btnSync.disabled = false;
        }, 2000);
        
        if (success) {
          // Re-render entirely to update map nodes and star counts if they were overwritten
          this.render();
        }
      });
    }
    
    if (btnSandbox) {
      btnSandbox.addEventListener('click', () => {
        // Need to render sandbox
        this.app.showScreen('screen-sandbox');
      });
    }

    if (btnLogout) {
      btnLogout.addEventListener('click', () => {
        this.app.profileSwitcher.logout();
        this.app.landingScreen.render();
        this.app.showScreen('screen-landing');
      });
    }

    // Parents area button
    const btnParents = this.container.querySelector('#btn-parents-map');
    if (btnParents) {
      btnParents.addEventListener('click', () => {
        this.app.parentsDashboard.render();
        this.app.showScreen('screen-parents');
      });
    }

    // Avatar change logic
    const avatarDisplay = this.container.querySelector('.avatar-display');
    const avatarModal = document.getElementById('modal-avatar');
    if (avatarDisplay && avatarModal) {
      avatarDisplay.addEventListener('click', () => {
        avatarModal.classList.add('active');
        
        const getAvatarSrc = (a: string) => {
          const map: Record<string, string> = {
            princess: '/art/princess_avatar.jpg',
            knight: '/art/knight_avatar.jpg',
            magician: '/art/magician_avatar.jpg',
            explorer: '/art/explorer_avatar.jpg'
          };
          return map[a] || map['princess'];
        };

        avatarModal.innerHTML = `
          <div class="task-modal-content glass-modal" style="padding: 20px; text-align: center;">
            <h2 style="color: #333; margin-bottom: 20px;">Change Hero</h2>
            <div class="avatar-grid">
              ${this.app.profileSwitcher.getAvailableAvatars().map(av => `
                <div class="avatar-option" data-avatar="${av}" style="cursor: pointer; margin: 10px;">
                  <img src="${getAvatarSrc(av)}" class="profile-avatar-img" style="width:80px; height:80px;" />
                </div>
              `).join('')}
            </div>
            <button id="btn-close-avatar" class="btn btn-large" style="margin-top: 20px;">Cancel</button>
          </div>
        `;

        avatarModal.querySelectorAll('.avatar-option').forEach(el => {
          el.addEventListener('click', (e) => {
            const selected = (e.currentTarget as HTMLElement).getAttribute('data-avatar');
            if (selected) {
              this.app.profileSwitcher.changeAvatar(selected);
              this.updateHeader(this.app.profileSwitcher.getCurrentPlayerName() || 'Unknown', selected);
            }
            avatarModal.classList.remove('active');
          });
        });

        avatarModal.querySelector('#btn-close-avatar')?.addEventListener('click', () => {
          avatarModal.classList.remove('active');
        });
      });
    }
  }

  public onShow() {
    this.updateHeader(
      this.app.profileSwitcher.getCurrentPlayerName() || 'Unknown',
      this.app.profileSwitcher.getCurrentAvatar() || 'princess'
    );
    this.loadState();
    this.updateBackground();
    this.generateMapWorld();
    this.centerMapOnActiveNode();
  }

  private updateBackground() {
    const mapContainer = this.container.querySelector('.map-container') as HTMLElement;
    if (!mapContainer) return;

    // Each world is 10 nodes (this.totalNodes). So world index = floor(nodes / 10)
    // If the kid exceeds the number of backgrounds, it loops.
    const worldIndex = Math.floor(this.playerNodesCompleted / this.totalNodes);
    const bgIndex = worldIndex % this.backgrounds.length;
    
    mapContainer.style.backgroundImage = `url('/art/${this.backgrounds[bgIndex]}')`;
    mapContainer.style.backgroundSize = 'cover';
    mapContainer.style.backgroundPosition = 'center';
  }

  private generateMapWorld() {
    const mapWorld = this.container.querySelector('#map-world') as HTMLElement;
    if (!mapWorld) return;
    mapWorld.innerHTML = '';
    
    this.currentPathNodes = [];
    const mapWidth = 1000;
    const mapHeight = 1000;
    
    for (let i = 0; i < this.totalNodes; i++) {
      let x, y;
      if (i === 0) {
        x = mapWidth / 2;
        y = mapHeight - 100;
      } else {
        const prev = this.currentPathNodes[i - 1];
        x = prev.x + (Math.random() * 200 - 100);
        x = Math.max(100, Math.min(mapWidth - 100, x));
        y = prev.y - (Math.random() * 80 + 80);
      }
      this.currentPathNodes.push({x, y});
    }

    // Draw SVG Path
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute('class', 'map-path-svg');
    svg.setAttribute('viewBox', `0 0 ${mapWidth} ${mapHeight}`);
    
    let pathD = `M ${this.currentPathNodes[0].x} ${this.currentPathNodes[0].y}`;
    for (let i = 1; i < this.currentPathNodes.length; i++) {
      const curr = this.currentPathNodes[i];
      const prev = this.currentPathNodes[i - 1];
      const ctrlX = (prev.x + curr.x) / 2 + (Math.random() * 100 - 50);
      const ctrlY = (prev.y + curr.y) / 2;
      pathD += ` Q ${ctrlX} ${ctrlY}, ${curr.x} ${curr.y}`;
    }
    
    const path = document.createElementNS(svgNS, "path");
    path.setAttribute('d', pathD);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', 'rgba(255, 255, 255, 0.9)');
    path.setAttribute('stroke-width', '12');
    path.setAttribute('stroke-dasharray', '20, 15');
    svg.appendChild(path);
    mapWorld.appendChild(svg);

    // Draw Nodes
    const localNodesCompleted = this.playerNodesCompleted % this.totalNodes;
    
    this.currentPathNodes.forEach((node, i) => {
      const nodeEl = document.createElement('div');
      nodeEl.className = 'map-node';
      nodeEl.style.left = `${node.x}px`;
      nodeEl.style.top = `${node.y}px`;
      
      const isCompleted = i < localNodesCompleted;
      const isActive = i === localNodesCompleted;

      if (isCompleted) {
        nodeEl.classList.add('completed');
        nodeEl.innerHTML = '⭐';
      } else if (isActive) {
        nodeEl.classList.add('active-node');
        
        const avatar = this.app.profileSwitcher.getCurrentAvatar() || 'princess';
        const getAvatarSrc = (a: string) => {
          const map: Record<string, string> = {
            princess: '/art/princess_avatar.jpg',
            knight: '/art/knight_avatar.jpg',
            magician: '/art/magician_avatar.jpg',
            explorer: '/art/explorer_avatar.jpg'
          };
          return map[a] || map['princess'];
        };
        
        nodeEl.innerHTML = `<img src="${getAvatarSrc(avatar)}" alt="Avatar" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover; display: block;" />`;
        nodeEl.onclick = () => {
          this.app.taskRunner.startSession([]);
        };
      } else {
        nodeEl.classList.add('locked');
        nodeEl.innerHTML = '🔒';
      }
      mapWorld.appendChild(nodeEl);
    });
  }

  private centerMapOnActiveNode() {
    const viewport = this.container.querySelector('#map-viewport');
    if (!viewport || this.currentPathNodes.length === 0) return;
    
    const targetIdx = Math.min(this.playerNodesCompleted, this.currentPathNodes.length - 1);
    const targetNode = this.currentPathNodes[targetIdx];
    
    const vWidth = viewport.clientWidth;
    const vHeight = viewport.clientHeight;
    
    const scrollX = targetNode.x - (vWidth / 2);
    const scrollY = targetNode.y - (vHeight / 2);
    
    viewport.scrollTo({
      left: scrollX,
      top: scrollY,
      behavior: 'smooth'
    });
  }
}
