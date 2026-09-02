import './style.css';
import { App } from './app';

// Telemetry placeholder
export const telemetry = {
  trackEvent: (evt: string, data: any) => console.log('TELEMETRY:', evt, data)
};

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});
