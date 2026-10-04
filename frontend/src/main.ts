import './style.css';
import { App } from './app';
import { speech } from './utils/Speech';

// Telemetry placeholder
export const telemetry = {
  trackEvent: (evt: string, data: any) => console.log('TELEMETRY:', evt, data)
};

function start() {
  speech.init();
  const app = new App();
  app.init();
}

// Start the app immediately if DOM is already parsed/interactive, otherwise wait for DOMContentLoaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', start);
} else {
  start();
}

