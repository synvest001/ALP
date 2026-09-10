import { App } from '../app';
import { SyncEngine } from '../engine/SyncEngine';
import { GRAND_TREASURES } from '../data/Treasures';
import { FAIRY_CASTLE_PARTS, getUnlockedCastlePartsCount, renderFairyCastleSvg } from '../data/FairyCastle';
import { soundFX } from '../utils/SoundFX';
import { resolveAssetUrl } from '../utils/assets';
import { DailyQuestManager } from '../engine/DailyQuestManager';

export class MapScreen {
  private container: HTMLElement;
  private app: App;
  
  // State: 5 nodes per realm path makes each journey focused and rewarding
  public static readonly NODES_PER_MAP = 5;
  private totalNodes = MapScreen.NODES_PER_MAP;
  private playerNodesCompleted = 0;
  private currentPathNodes: {x: number, y: number}[] = [];
  
  private backgrounds = [
    'magical_forest.jpg',
    'emerald_waterfalls.jpg',
    'crystal_cave.jpg',
    'dragon_castle.jpg',
    'mushroom_village.jpg',
    'pixie_hollow.jpg',
    'whispering_woods.jpg',
    'candy_canyon.jpg',
    'clockwork_city.jpg',
    'cloud_kingdom.jpg',
    'mystic_aurora_fjord.jpg',
    'dinosaur_valley.jpg',
    'enchanted_library.jpg',
    'fairy_treehouse.jpg',
    'floating_islands.jpg',
    'frozen_tundra.jpg',
    'golden_savannah_palace.jpg',
    'mermaid_lagoon.jpg',
    'rainbow_peaks.jpg',
    'starlight_observatory.jpg',
    'volcano_forge.jpg',
    'crystal_glacier_peaks.jpg',
    'sunken_atlantis.jpg',
    'pumpkin_hollow.jpg',
    'bamboo_sanctuary.jpg',
    'sapphire_coral_reef.jpg',
    'cosmic_nebula.jpg',
    'desert_oasis.jpg',
    'gingerbread_village.jpg',
    'whimsical_toyland.jpg',
    'bioluminescent_jungle.jpg',
    'celestial_pirate_haven.jpg',
    'cherry_gardens.jpg',
    'moonlit_lantern_valley.jpg',
    'sunfire_desert_pyramids.jpg',
    'crystal_geode_mines.jpg',
    'celestial_starlit_citadel.jpg',
    'autumn_whisper_grove.jpg'
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
          <button id="btn-goto-castle" class="header-btn castle-btn" title="View Fairy Castle">🏰 Fairy Castle</button>
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

      <!-- Castle Viewer Modal -->
      <div id="modal-fairy-castle" class="castle-modal hidden">
        <div class="castle-modal-card">
          <button id="btn-close-castle" class="btn-close-modal">✕</button>
          <div class="castle-modal-header">
            <h2>🏰 The Royal Fairy Castle</h2>
            <p class="castle-subtitle">Complete realms to construct new magical wings!</p>
          </div>
          <div class="castle-view-container" id="castle-display-area">
            <!-- Castle SVG injected here -->
          </div>
          <div class="castle-parts-list" id="castle-parts-checklist">
            <!-- Parts checklist injected here -->
          </div>
        </div>
      </div>

      <!-- Grand Realm Completion Modal -->
      <div id="modal-realm-complete" class="realm-complete-modal hidden">
        <div class="realm-complete-card">
          <div class="confetti-container" id="completion-confetti"></div>
          <div class="completion-crown">👑</div>
          <h1 class="completion-title" id="complete-realm-title">Realm Complete!</h1>
          <p class="completion-subtitle" id="complete-realm-desc">You have conquered the path and built a new part of the Fairy Castle!</p>

          <!-- Castle upgrade display -->
          <div class="completion-castle-box" id="completion-castle-box">
            <h3 class="upgrade-headline">🏰 Castle Wing Constructed:</h3>
            <div class="new-part-name" id="new-part-title">Moonstone Foundation & Crystal Moat</div>
            <div class="completion-svg-preview" id="completion-castle-svg"></div>
          </div>

          <!-- Treasure Award Display -->
          <div class="completion-treasure-box" id="completion-treasure-box">
            <div class="treasure-ribbon">⭐ GRAND TREASURE UNLOCKED ⭐</div>
            <div class="treasure-award-card" id="treasure-award-card">
              <!-- Treasure SVG & details injected here -->
            </div>
          </div>

          <button id="btn-next-realm" class="btn-continue-journey">
            Journey to Next Realm ✨
          </button>
        </div>
      </div>

      <!-- Adventure Select Modal -->
      <div id="modal-adventure-select" class="castle-modal hidden">
        <div class="castle-modal-card" style="max-width: 500px; text-align: center;">
          <button id="btn-close-adventure" class="btn-close-modal">✕</button>
          <h2>🗺️ Choose Your Path</h2>
          <p style="margin-bottom: 20px;">What would you like to explore today?</p>
          
          <div style="display: flex; flex-direction: column; gap: 15px;">
            <button class="btn btn-large btn-adventure" data-domain="" style="background: linear-gradient(135deg, #a855f7, #7e22ce);">
              🌟 Mixed Adventure (Recommended)
            </button>
            <button class="btn btn-large btn-adventure" data-domain="MATHEMATICS" style="background: linear-gradient(135deg, #ef4444, #b91c1c);">
              🔢 Math Focus
            </button>
            <button class="btn btn-large btn-adventure" data-domain="ENGLISH_LANGUAGE" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8);">
              📖 English Focus
            </button>
            <button class="btn btn-large btn-adventure" data-domain="LOGICAL_REASONING" style="background: linear-gradient(135deg, #f59e0b, #b45309);">
              🧩 Logic Focus
            </button>
            <button class="btn btn-large btn-adventure" data-domain="SCIENCE_EVS" style="background: linear-gradient(135deg, #10b981, #047857);">
              🌍 Science & World Focus
            </button>
          </div>
        </div>
      </div>
    `;

    this.bindEvents();
    this.loadState();
  }

  private getPlayerKey(prefix: string): string {
    const kidName = (this.app?.profileSwitcher?.getCurrentPlayerName() || 'default_player').toLowerCase().trim();
    return `alp_${kidName}_${prefix}`;
  }

  private loadState() {
    const playerKey = this.getPlayerKey('nodes_completed');
    const savedNodes = localStorage.getItem(playerKey) || localStorage.getItem('alp_nodes_completed');
    if (savedNodes) {
      this.playerNodesCompleted = parseInt(savedNodes, 10) || 0;
    } else {
      this.playerNodesCompleted = 0;
    }
  }

  public saveState() {
    const playerKey = this.getPlayerKey('nodes_completed');
    localStorage.setItem(playerKey, this.playerNodesCompleted.toString());
    localStorage.setItem('alp_nodes_completed', this.playerNodesCompleted.toString());
  }

  public getCurrentWorldIndex(): number {
    return Math.floor(this.playerNodesCompleted / this.totalNodes);
  }

  public getCurrentWorldName(): string {
    const worldIndex = this.getCurrentWorldIndex();
    const bgIndex = worldIndex % this.backgrounds.length;
    let name = this.backgrounds[bgIndex].replace('.jpg', '').replace(/_/g, ' ');
    return name.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  }

  public getNextWorldName(): string {
    const nextIndex = (this.getCurrentWorldIndex() + 1) % this.backgrounds.length;
    let name = this.backgrounds[nextIndex].replace('.jpg', '').replace(/_/g, ' ');
    return name.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  }

  public updateHeader(playerName: string, avatar: string) {
    const avatarDisplay = this.container.querySelector('#map-avatar-display') as HTMLElement;
    const greeting = this.container.querySelector('#map-greeting') as HTMLElement;
    
    if (avatarDisplay) {
      const getAvatarSrc = (a: string) => {
        const map: Record<string, string> = {
          princess: 'art/princess_avatar.jpg',
          knight: 'art/knight_avatar.jpg',
          magician: 'art/magician_avatar.jpg',
          explorer: 'art/explorer_avatar.jpg'
        };
        return resolveAssetUrl(map[a] || map['princess']);
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
      const starKey = this.getPlayerKey('stars');
      const starVal = localStorage.getItem(starKey) || localStorage.getItem('alp_stars') || '0';
      stars.textContent = `⭐ ${starVal}`;
    }

    // Dynamic Level Display based on completed nodes/realms
    const levelEl = this.container.querySelector('#player-level') as HTMLElement;
    if (levelEl) {
      const realmNum = Math.floor(this.playerNodesCompleted / this.totalNodes) + 1;
      const titles = ['Novice', 'Explorer', 'Star Seeker', 'Pathfinder', 'Sorcerer', 'Realm Hero', 'Champion'];
      const title = titles[Math.min(realmNum - 1, titles.length - 1)] || 'Grand Master';
      levelEl.textContent = `Level ${realmNum}: ${title}`;
    }

    // Dynamic Daily Quest Display
    const questEl = this.container.querySelector('#map-quest-status') as HTMLElement;
    if (questEl) {
      const quest = DailyQuestManager.getStatus(playerName);
      if (quest.completed) {
        questEl.innerHTML = `Daily Quest: ${quest.count} / ${quest.target} 🌟 <span class="quest-done-badge">Completed!</span>`;
        questEl.classList.add('quest-completed');
      } else {
        questEl.innerHTML = `Daily Quest: ${quest.count} / ${quest.target} 🎯`;
        questEl.classList.remove('quest-completed');
      }
    }
  }

  private bindEvents() {
    const btnSandbox = this.container.querySelector('#btn-goto-sandbox');
    const btnCastle = this.container.querySelector('#btn-goto-castle');
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
          this.render();
        }
      });
    }
    
    if (btnSandbox) {
      btnSandbox.addEventListener('click', () => {
        this.app.showScreen('screen-sandbox');
      });
    }

    if (btnCastle) {
      btnCastle.addEventListener('click', () => {
        this.openCastleModal();
      });
    }

    const btnCloseCastle = this.container.querySelector('#btn-close-castle');
    const castleModal = this.container.querySelector('#modal-fairy-castle');
    if (btnCloseCastle && castleModal) {
      btnCloseCastle.addEventListener('click', () => {
        castleModal.classList.add('hidden');
      });
    }

    // Adventure Modal bindings
    const adventureModal = this.container.querySelector('#modal-adventure-select');
    const btnCloseAdventure = this.container.querySelector('#btn-close-adventure');
    if (adventureModal && btnCloseAdventure) {
      btnCloseAdventure.addEventListener('click', () => {
        adventureModal.classList.add('hidden');
      });
      
      const adventureBtns = adventureModal.querySelectorAll('.btn-adventure');
      adventureBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
          const domain = (e.currentTarget as HTMLElement).getAttribute('data-domain');
          adventureModal.classList.add('hidden');
          
          if (domain) {
            this.app.taskRunner.startSession(undefined, domain);
          } else {
            this.app.taskRunner.startSession();
          }
        });
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

    // Avatar change modal
    const avatarDisplay = this.container.querySelector('.avatar-display');
    const avatarModal = document.getElementById('modal-avatar');
    if (avatarDisplay && avatarModal) {
      avatarDisplay.addEventListener('click', () => {
        avatarModal.classList.add('active');
        
        const getAvatarSrc = (a: string) => {
          const map: Record<string, string> = {
            princess: 'art/princess_avatar.jpg',
            knight: 'art/knight_avatar.jpg',
            magician: 'art/magician_avatar.jpg',
            explorer: 'art/explorer_avatar.jpg'
          };
          return resolveAssetUrl(map[a] || map['princess']);
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

  public openCastleModal() {
    const modal = this.container.querySelector('#modal-fairy-castle');
    const displayArea = this.container.querySelector('#castle-display-area');
    const checklist = this.container.querySelector('#castle-parts-checklist');
    if (!modal || !displayArea || !checklist) return;

    soundFX.playCastleBuild();
    const unlockedCount = getUnlockedCastlePartsCount(this.playerNodesCompleted, this.totalNodes);
    
    displayArea.innerHTML = renderFairyCastleSvg(unlockedCount);

    checklist.innerHTML = FAIRY_CASTLE_PARTS.map(part => {
      const isBuilt = part.partIndex <= unlockedCount;
      return `
        <div class="castle-part-row ${isBuilt ? 'built' : 'locked'}">
          <span class="part-status-icon">${isBuilt ? '✅' : '🔒'}</span>
          <div class="part-text">
            <div class="part-title">Part ${part.partIndex}: ${part.name}</div>
            <div class="part-realm">${isBuilt ? 'Built after completing ' + part.realmRequirement : 'Requires completing ' + part.realmRequirement}</div>
            <p class="part-desc">${part.description}</p>
          </div>
        </div>
      `;
    }).join('');

    modal.classList.remove('hidden');
  }

  public onShow() {
    this.loadState();
    this.updateHeader(
      this.app.profileSwitcher.getCurrentPlayerName() || 'Unknown',
      this.app.profileSwitcher.getCurrentAvatar() || 'princess'
    );
    this.updateBackground();
    this.generateMapWorld();
    this.centerMapOnActiveNode();
  }

  private updateBackground() {
    const mapContainer = this.container.querySelector('.map-container') as HTMLElement;
    if (!mapContainer) return;

    const worldIndex = Math.floor(this.playerNodesCompleted / this.totalNodes);
    const bgIndex = worldIndex % this.backgrounds.length;
    
    const bgUrl = resolveAssetUrl(`art/${this.backgrounds[bgIndex]}`);
    mapContainer.style.backgroundImage = `url('${bgUrl}')`;
    mapContainer.style.backgroundSize = 'cover';
    mapContainer.style.backgroundPosition = 'center';
    mapContainer.style.backgroundRepeat = 'no-repeat';
  }

  private generateMapWorld() {
    const mapWorld = this.container.querySelector('#map-world') as HTMLElement;
    const viewport = this.container.querySelector('#map-viewport') as HTMLElement;
    if (!mapWorld || !viewport) return;
    mapWorld.innerHTML = '';
    
    this.currentPathNodes = [];
    const mapWidth = Math.max(viewport.clientWidth, 1000);
    const mapHeight = Math.max(viewport.clientHeight, 700);
    mapWorld.style.width = `${mapWidth}px`;
    mapWorld.style.height = `${mapHeight}px`;
    
    // Deterministic winding path matching the golden road in the background art!
    // Traces naturally from bottom-center up towards the waterfall archway
    const pathRatios = [
      { x: 0.50, y: 0.84 }, // Node 0: Starting gateway at bottom-center
      { x: 0.54, y: 0.68 }, // Node 1: Winding curve up-right
      { x: 0.58, y: 0.52 }, // Node 2: Sunny glade on stone road
      { x: 0.59, y: 0.36 }, // Node 3: Beside crystal stream/bridge
      { x: 0.57, y: 0.20 }  // Node 4: Final destination archway at top!
    ];

    for (let i = 0; i < this.totalNodes; i++) {
      const ratio = pathRatios[i] || { x: 0.5, y: 0.8 - i * 0.15 };
      const x = mapWidth * ratio.x;
      const y = mapHeight * ratio.y;
      this.currentPathNodes.push({ x, y });
    }

    // Draw Smooth SVG Path connecting the 5 nodes
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute('class', 'map-path-svg');
    svg.setAttribute('viewBox', `0 0 ${mapWidth} ${mapHeight}`);
    
    let pathD = `M ${this.currentPathNodes[0].x} ${this.currentPathNodes[0].y}`;
    for (let i = 1; i < this.currentPathNodes.length; i++) {
      const curr = this.currentPathNodes[i];
      const prev = this.currentPathNodes[i - 1];
      const ctrlX = (prev.x + curr.x) / 2 + 15;
      const ctrlY = (prev.y + curr.y) / 2;
      pathD += ` Q ${ctrlX} ${ctrlY}, ${curr.x} ${curr.y}`;
    }
    
    // Drop shadow path for depth
    const shadowPath = document.createElementNS(svgNS, "path");
    shadowPath.setAttribute('d', pathD);
    shadowPath.setAttribute('fill', 'none');
    shadowPath.setAttribute('stroke', 'rgba(0, 0, 0, 0.4)');
    shadowPath.setAttribute('stroke-width', '16');
    shadowPath.setAttribute('stroke-linecap', 'round');
    svg.appendChild(shadowPath);

    // Glowing main dashed path
    const path = document.createElementNS(svgNS, "path");
    path.setAttribute('d', pathD);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', 'rgba(255, 255, 255, 0.95)');
    path.setAttribute('stroke-width', '12');
    path.setAttribute('stroke-dasharray', '22, 14');
    path.setAttribute('stroke-linecap', 'round');
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
            princess: 'art/princess_avatar.jpg',
            knight: 'art/knight_avatar.jpg',
            magician: 'art/magician_avatar.jpg',
            explorer: 'art/explorer_avatar.jpg'
          };
          return resolveAssetUrl(map[a] || map['princess']);
        };
        
        nodeEl.innerHTML = `<img src="${getAvatarSrc(avatar)}" alt="Avatar" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover; display: block;" />`;
        nodeEl.onclick = () => {
          const adventureModal = this.container.querySelector('#modal-adventure-select');
          if (adventureModal) {
            adventureModal.classList.remove('hidden');
          } else {
            this.app.taskRunner.startSession();
          }
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
    
    const localIdx = this.playerNodesCompleted % this.totalNodes;
    const targetIdx = Math.min(localIdx, this.currentPathNodes.length - 1);
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

  /**
   * Called when a player completes the 5th node of a realm!
   * Celebrates the completion, constructs a new wing of the Fairy Castle,
   * awards the grand treasure, and transitions to the next realm!
   */
  public showRealmCompletion(realmIndex: number, _newTotalNodes: number, onDone: () => void) {
    const modal = this.container.querySelector('#modal-realm-complete') as HTMLElement;
    const title = this.container.querySelector('#complete-realm-title') as HTMLElement;
    const desc = this.container.querySelector('#complete-realm-desc') as HTMLElement;
    const newPartTitle = this.container.querySelector('#new-part-title') as HTMLElement;
    const castleSvgArea = this.container.querySelector('#completion-castle-svg') as HTMLElement;
    const treasureCardArea = this.container.querySelector('#treasure-award-card') as HTMLElement;
    const btnNext = this.container.querySelector('#btn-next-realm') as HTMLButtonElement;

    if (!modal) return;

    soundFX.playTreasureUnlock();
    soundFX.playCastleBuild();

    const worldName = this.getCurrentWorldName();
    const nextWorldName = this.getNextWorldName();
    const unlockedPartsCount = Math.min(FAIRY_CASTLE_PARTS.length, realmIndex + 1);
    const newPart = FAIRY_CASTLE_PARTS[realmIndex] || FAIRY_CASTLE_PARTS[FAIRY_CASTLE_PARTS.length - 1];
    const unlockedTreasure = GRAND_TREASURES[realmIndex] || GRAND_TREASURES[GRAND_TREASURES.length - 1];

    if (title) title.textContent = `🌟 ${worldName} Complete! 🌟`;
    if (desc) desc.textContent = `You cleared all 5 challenges on the path! A new wing has been added to your Fairy Castle.`;
    if (newPartTitle && newPart) newPartTitle.textContent = `Part ${newPart.partIndex}: ${newPart.name}`;
    if (castleSvgArea) castleSvgArea.innerHTML = renderFairyCastleSvg(unlockedPartsCount, newPart.partIndex);

    if (treasureCardArea && unlockedTreasure) {
      treasureCardArea.innerHTML = `
        <div class="award-art-container">${unlockedTreasure.svg}</div>
        <div class="award-text">
          <div class="treasure-badge ${unlockedTreasure.rarity.toLowerCase()}">${unlockedTreasure.rarity}</div>
          <h3 class="award-name">${unlockedTreasure.name}</h3>
          <p class="award-desc">${unlockedTreasure.description}</p>
        </div>
      `;
    }

    if (btnNext) {
      btnNext.textContent = `Enter ${nextWorldName} ➔`;
      btnNext.onclick = () => {
        modal.classList.add('hidden');
        onDone();
      };
    }

    modal.classList.remove('hidden');
  }
}
