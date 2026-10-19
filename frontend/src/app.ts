import { ProfileSwitcher } from './profile/profile_switcher';
import { LandingScreen } from './ui/LandingScreen';
import { AccountScreen } from './ui/AccountScreen';
import { MapScreen } from './ui/MapScreen';
import { ParentsDashboard } from './ui/ParentsDashboard';
import { TaskRunner } from './ui/TaskRunner';
import { ToyboxScreen } from './ui/ToyboxScreen';

export class App {
  public profileSwitcher: ProfileSwitcher;
  
  // UI Components
  public landingScreen: LandingScreen;
  public accountScreen: AccountScreen;
  public mapScreen: MapScreen;
  public parentsDashboard: ParentsDashboard;
  public taskRunner: TaskRunner;
  public toyboxScreen: ToyboxScreen;

  constructor() {
    this.profileSwitcher = new ProfileSwitcher();
    
    // Initialize UI Components
    this.landingScreen = new LandingScreen(this);
    this.accountScreen = new AccountScreen(this);
    this.mapScreen = new MapScreen(this);
    this.parentsDashboard = new ParentsDashboard(this);
    this.taskRunner = new TaskRunner(this);
    this.toyboxScreen = new ToyboxScreen(this);
  }

  public init() {
    this.landingScreen.render();
    this.accountScreen.render();
    this.mapScreen.render();
    this.parentsDashboard.render();
    this.taskRunner.render();
    this.toyboxScreen.render();
    
    // Check auth state
    const currentName = this.profileSwitcher.getCurrentPlayerName();
    if (currentName) {
      this.showScreen('screen-map');
    } else {
      this.showScreen('screen-landing');
    }

    // Request persistent storage if supported by the browser
    if (typeof navigator !== 'undefined' && navigator.storage && typeof navigator.storage.persist === 'function') {
      navigator.storage.persist().catch(function () {});
    }
  }

  public showScreen(screenId: string) {
    // Hide all screens
    const screens = document.querySelectorAll('.screen');
    screens.forEach(s => s.classList.remove('active'));
    
    // Show target screen
    const target = document.getElementById(screenId);
    if (target) {
      target.classList.add('active');
      
      // Trigger lifecycle hooks if needed
      if (screenId === 'screen-map') {
        this.mapScreen.onShow();
      }
    }
  }
}
