import { soundFX } from './SoundFX';
import { promptHash } from './hash';

const SILENT_WAV = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA';

class SpeechHelper {
  public status = 'idle';
  private voices: SpeechSynthesisVoice[] = [];
  private unlocked = false;
  private timer: number | null = null;
  private dbgEl: HTMLElement | null = null;
  private audio: HTMLAudioElement | null = null;
  private missing: { [k: string]: boolean } = {};

  private useMp3(): boolean {
    try { return !document.documentElement.classList.contains('lite'); } catch (e) { return false; }
  }

  private synthSupported(): boolean {
    return typeof window !== 'undefined' && 'speechSynthesis' in window &&
      typeof (window as any).SpeechSynthesisUtterance !== 'undefined';
  }

  isSupported(): boolean {
    return this.synthSupported() || !!this.audio;
  }

  init(): void {
    if (typeof window === 'undefined') return;
    if (/[?&]audiodebug=1/.test(window.location.search)) this.makeDebug();
    if (this.useMp3()) {
      try { this.audio = new Audio(); } catch (e) { this.audio = null; }
    }
    this.loadVoices();
    if (this.synthSupported()) {
      try { (window.speechSynthesis as any).onvoiceschanged = () => this.loadVoices(); } catch (e) {}
    }
    const unlock = () => {
      if (this.unlocked) return;
      this.unlocked = true;
      soundFX.unlock();
      if (this.audio) {
        try { this.audio.src = SILENT_WAV; const p: any = this.audio.play(); if (p && p.catch) p.catch(() => {}); } catch (e) {}
      }
      if (this.synthSupported()) {
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
    let tries = 0;
    const retry = window.setInterval(() => {
      this.loadVoices();
      tries++;
      if (this.voices.length > 0 || tries >= 10) window.clearInterval(retry);
    }, 500);
    this.report('init');
  }

  private loadVoices(): void {
    if (!this.synthSupported()) return;
    try { this.voices = window.speechSynthesis.getVoices() || []; } catch (e) { this.voices = []; }
  }

  cancel(): void {
    if (this.timer !== null) { window.clearTimeout(this.timer); this.timer = null; }
    try { if (this.audio) this.audio.pause(); } catch (e) {}
    if (this.synthSupported()) { try { window.speechSynthesis.cancel(); } catch (e) {} }
  }

  speak(text: string): void {
    if (!text || !this.isSupported()) { this.report('speak skipped'); return; }
    this.cancel();
    if (this.audio) {
      const h = promptHash(text);
      if (!this.missing[h]) {
        const env = (import.meta as any).env;
        const base = env && env.BASE_URL ? env.BASE_URL : './';
        const a = this.audio;
        a.onerror = () => { this.missing[h] = true; this.report('mp3 missing, using TTS'); this.speakWithSynth(text); };
        a.onplaying = () => this.report('mp3 playing ' + h);
        try {
          a.src = base + 'audio/prompts/' + h + '.mp3';
          const p: any = a.play();
          if (p && p.catch) p.catch(() => { this.report('mp3 play blocked'); });
          this.report('mp3 requested ' + h);
          return;
        } catch (e) { this.missing[h] = true; }
      }
    }
    this.speakWithSynth(text);
  }

  private speakWithSynth(text: string): void {
    if (!this.synthSupported()) { this.report('no TTS available'); return; }
    try { window.speechSynthesis.cancel(); } catch (e) {}
    // iOS drops speak() issued in the same tick as cancel(); wait a moment.
    if (this.timer !== null) window.clearTimeout(this.timer);
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
        u.onstart = () => this.report('speaking (tts)');
        u.onend = () => this.report('ended (tts)');
        u.onerror = (ev: any) => this.report('tts error ' + (ev && ev.error ? ev.error : '?'));
        window.speechSynthesis.speak(u);
        this.report('tts speak() called, voice=' + (v ? v.name : 'default'));
      } catch (e) {
        this.report('exception ' + e);
      }
    }, 80);
  }

  private report(s: string): void {
    this.status = s;
    if (this.dbgEl) {
      this.dbgEl.textContent = 'audio: ' + s + ' | mode=' + (this.audio ? 'mp3' : 'tts') +
        ' | voices=' + this.voices.length +
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
