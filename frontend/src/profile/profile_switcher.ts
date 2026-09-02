export interface UserProfile {
  name: string;
  avatar: string;
}

export class ProfileSwitcher {
  private currentPlayerName: string | null = null;
  private currentAvatar: string | null = null;
  private savedProfiles: UserProfile[] = [];
  private listeners: ((playerName: string | null, avatar: string | null) => void)[] = [];

  constructor() {
    this.currentPlayerName = localStorage.getItem('alp_current_name');
    this.currentAvatar = localStorage.getItem('alp_current_avatar');
    
    try {
      const saved = localStorage.getItem('alp_registered_profiles');
      if (saved) {
        this.savedProfiles = JSON.parse(saved);
      }
    } catch (e) {
      console.error("Failed to parse saved profiles", e);
    }
  }

  public getAvailableAvatars(): string[] {
    return ['princess', 'knight', 'magician', 'explorer'];
  }
  
  public getSavedProfiles(): UserProfile[] {
    return this.savedProfiles;
  }

  public getCurrentPlayerName(): string | null {
    return this.currentPlayerName;
  }
  
  public getCurrentAvatar(): string | null {
    return this.currentAvatar;
  }

  public login(playerName: string, avatar: string = 'princess') {
    this.currentPlayerName = playerName;
    
    // Check if player exists in registry
    const existing = this.savedProfiles.find(p => p.name.toLowerCase() === playerName.toLowerCase());
    
    if (existing) {
      // If logging in as existing, use their saved avatar if we aren't explicitly assigning a new one
      this.currentAvatar = existing.avatar;
    } else {
      // New player
      this.currentAvatar = avatar;
      this.savedProfiles.push({ name: playerName, avatar: this.currentAvatar });
      this.saveRegistry();
    }
    
    localStorage.setItem('alp_current_name', this.currentPlayerName);
    localStorage.setItem('alp_current_avatar', this.currentAvatar);
    this.notifyListeners();
  }
  
  public changeAvatar(avatar: string) {
    this.currentAvatar = avatar;
    localStorage.setItem('alp_current_avatar', avatar);
    
    // Update registry
    if (this.currentPlayerName) {
      const existing = this.savedProfiles.find(p => p.name.toLowerCase() === this.currentPlayerName!.toLowerCase());
      if (existing) {
        existing.avatar = avatar;
        this.saveRegistry();
      }
    }
    
    this.notifyListeners();
  }
  
  private saveRegistry() {
    localStorage.setItem('alp_registered_profiles', JSON.stringify(this.savedProfiles));
  }
  
  public logout() {
    this.currentPlayerName = null;
    this.currentAvatar = null;
    localStorage.removeItem('alp_current_name');
    localStorage.removeItem('alp_current_avatar');
    this.notifyListeners();
  }

  public onProfileChanged(listener: (playerName: string | null, avatar: string | null) => void) {
    this.listeners.push(listener);
  }

  private notifyListeners() {
    this.listeners.forEach(l => l(this.currentPlayerName, this.currentAvatar));
  }
  
  public deleteProfile(playerName: string) {
    this.savedProfiles = this.savedProfiles.filter(p => p.name.toLowerCase() !== playerName.toLowerCase());
    this.saveRegistry();
    
    if (this.currentPlayerName && this.currentPlayerName.toLowerCase() === playerName.toLowerCase()) {
      this.logout();
    }
  }
  
  public resetProgress(_playerName: string) {
    // Currently progress is global, so we just clear the global keys
    // In a future refactor, these keys should be namespaced by playerName
    localStorage.removeItem('alp_nodes_completed');
    localStorage.removeItem('alp_unlocked_stickers');
    localStorage.removeItem('alp_stars');
  }
}
