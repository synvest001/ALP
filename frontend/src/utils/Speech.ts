import { soundFX } from './SoundFX';

class SpeechHelper {
  public status = 'idle';
  private voices: SpeechSynthesisVoice[] = [];
  private unlocked = false;
  private timer: number | null = null;
  private dbgEl: HTMLElement | null = null;

  isSupported(): boolean {
    return typeof window !== 'undefined' && 'speechSynthesis' in window &&
      typeof (window as any).SpeechSynthesisUtterance !== 'undefined';
  }

  init(): void {
    if (typeof window === 'undefined') return;
    if (/[?&]audiodebug=1/.test(window.location.search)) this.makeDebug();
    this.loadVoices();
    if (this.isSupported()) {
      try {
        (window.speechSynthesis as any).onvoiceschanged = () => this.loadVoices();
      } catch (e) {}
    }
    const unlock = () => {
      if (this.unlocked) return;
      this.unlocked = true;
      soundFX.unlock();
      if (this.isSupported()) {
        try {
          const u = new SpeechSynthesisUtterance(' ');
          u.volume = 0;
          window.speechSynthesis.speak(u);
        } catch (e) {}
      }
      this.report('unlocked by touch');
      document.removeEventListener('touchend', unlock, true);
      document.removeEventListener('click', unlock, true);
    };
    document.addEventListener('touchend', unlock, true);
    document.addEventListener('click', unlock, true);
    // retry voice list a few times because iOS fills it late
    let tries = 0;
    const retry = window.setInterval(() => {
      this.loadVoices();
      tries++;
      if (this.voices.length > 0 || tries >= 10) window.clearInterval(retry);
    }, 500);
  }

  private loadVoices(): void {
    if (!this.isSupported()) return;
    try { this.voices = window.speechSynthesis.getVoices() || []; } catch (e) { this.voices = []; }
    this.report('voices=' + this.voices.length);
  }

  cancel(): void {
    if (this.timer !== null) { window.clearTimeout(this.timer); this.timer = null; }
    if (this.isSupported()) { try { window.speechSynthesis.cancel(); } catch (e) {} }
  }

  speak(text: string): void {
    if (!text || !this.isSupported()) { this.report('speak skipped (unsupported/empty)'); return; }
    this.cancel();
    // iOS drops speak() issued in the same tick as cancel(); wait a moment.
    this.timer = window.setTimeout(() => {
      this.timer = null;
      try {
        const u = new SpeechSynthesisUtterance(text);
        u.lang = 'en-US';
        u.rate = 0.85;
        u.volume = 1;
        if (this.voices.length === 0) this.loadVoices();
        let v: SpeechSynthesisVoice | null = null;
        for (let i = 0; i < this.voices.length; i++) {
          if (this.voices[i].lang && this.voices[i].lang.indexOf('en') === 0) { v = this.voices[i]; break; }
        }
        if (v) u.voice = v;
        u.onstart = () => this.report('speaking');
        u.onend = () => this.report('ended');
        u.onerror = (ev: any) => this.report('error ' + (ev && ev.error ? ev.error : '?'));
        window.speechSynthesis.speak(u);
        this.report('speak() called, voice=' + (v ? v.name : 'default'));
      } catch (e) {
        this.report('exception ' + e);
      }
    }, 80);
  }

  private report(s: string): void {
    this.status = s;
    if (this.dbgEl) {
      this.dbgEl.textContent = 'audio: ' + s + ' | voices=' + this.voices.length +
        ' | AC=' + (typeof (window as any).AudioContext) + '/' + (typeof (window as any).webkitAudioContext);
    }
  }

  private makeDebug(): void {
    const d = document.createElement('div');
    d.style.cssText = 'position:fixed;left:0;top:0;right:0;z-index:99999;background:#222;color:#0f0;font:12px monospace;padding:2px 4px;pointer-events:none';
    d.textContent = 'audio: init';
    const add = () => { document.body.appendChild(d); };
    if (document.body) add(); else document.addEventListener('DOMContentLoaded', add);
    this.dbgEl = d;
  }
}

export const speech = new SpeechHelper();
