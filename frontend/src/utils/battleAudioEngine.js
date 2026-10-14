/**
 * UNYQ Arena Battle Audio Engine
 * Handles procedural audio synthesis, sound FX, and media playback for battle showdowns.
 */

class BattleAudioEngine {
  constructor() {
    this.ctx = null;
    this.activeLoopInterval = null;
    this.isPlaying = false;
    this.currentTrackKey = null;
    this.step = 0;
  }

  initContext() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.ctx = new AudioContext();
      }
    }
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume();
    }
    return this.ctx;
  }

  playVoteChime() {
    const ctx = this.initContext();
    if (!ctx) return;
    const now = ctx.currentTime;
    
    // Radiant harmonic chord: A4 (440), C#5 (554.37), E5 (659.25), A5 (880)
    [440, 554.37, 659.25, 880].forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, now + idx * 0.05);
      
      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(0.12, now + idx * 0.05 + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.05 + 0.45);
      
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + idx * 0.05);
      osc.stop(now + idx * 0.05 + 0.5);
    });
  }

  playGong() {
    const ctx = this.initContext();
    if (!ctx) return;
    const now = ctx.currentTime;
    
    // Deep metallic gong tone
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(146.83, now); // D3
    osc.frequency.exponentialRampToValueAtTime(73.42, now + 1.2); // pitch bend down
    
    gain.gain.setValueAtTime(0.3, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 1.4);
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 1.5);
  }

  /**
   * Procedural Beat Generator for Demo Battle Rounds
   * Style: 140 BPM Trap Beat (Kick, 808 glide, Crisp Hat, Snare, Dark Synth)
   */
  startBeatLoop(trackKey, style = "dark_trap") {
    this.stopPlayback();
    const ctx = this.initContext();
    if (!ctx) return;

    this.isPlaying = true;
    this.currentTrackKey = trackKey;
    this.step = 0;

    const bpm = 140;
    const stepTime = (60 / bpm) / 4; // 16th notes = ~107ms

    // Define pitch sequences based on contender side
    const isContenderA = trackKey.includes("left");
    const bassFreqs = isContenderA 
      ? [55, 55, 0, 55, 0, 65.4, 0, 49, 55, 0, 55, 55, 0, 73.4, 65.4, 0] // A minor
      : [43.65, 43.65, 0, 43.65, 0, 51.91, 0, 38.89, 43.65, 0, 43.65, 43.65, 0, 58.27, 51.91, 0]; // F minor

    const synthPitches = isContenderA
      ? [220, 261.63, 329.63, 261.63] // Am arpeggio
      : [174.61, 207.65, 261.63, 207.65]; // Fm arpeggio

    this.activeLoopInterval = setInterval(() => {
      if (!this.isPlaying) return;
      const now = ctx.currentTime;
      const currentStep = this.step % 16;

      // 1. Kick on steps 0, 6, 10
      if (currentStep === 0 || currentStep === 6 || currentStep === 10) {
        this._triggerKick(ctx, now);
      }

      // 2. Snare / Clap on step 4 and 12
      if (currentStep === 4 || currentStep === 12) {
        this._triggerSnare(ctx, now);
      }

      // 3. Hi-hats on every 2nd step + roll on 14, 15
      if (currentStep % 2 === 0 || currentStep >= 14) {
        this._triggerHiHat(ctx, now, currentStep >= 14);
      }

      // 4. 808 Sub-Bass
      const bassFreq = bassFreqs[currentStep];
      if (bassFreq > 0) {
        this._trigger808(ctx, now, bassFreq);
      }

      // 5. Ambient Melodic Pluck
      if (currentStep % 4 === 0) {
        const pitch = synthPitches[(currentStep / 4) % synthPitches.length];
        this._triggerPluck(ctx, now, pitch);
      }

      this.step++;
    }, stepTime * 1000);
  }

  stopPlayback() {
    this.isPlaying = false;
    this.currentTrackKey = null;
    if (this.activeLoopInterval) {
      clearInterval(this.activeLoopInterval);
      this.activeLoopInterval = null;
    }
  }

  _triggerKick(ctx, now) {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.frequency.setValueAtTime(140, now);
    osc.frequency.exponentialRampToValueAtTime(40, now + 0.1);
    gain.gain.setValueAtTime(0.4, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.16);
  }

  _triggerSnare(ctx, now) {
    // Noise buffer for snap
    const bufferSize = ctx.sampleRate * 0.1;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const output = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      output[i] = Math.random() * 2 - 1;
    }
    const whiteNoise = ctx.createBufferSource();
    whiteNoise.buffer = buffer;

    const filter = ctx.createBiquadFilter();
    filter.type = "highpass";
    filter.frequency.value = 1000;

    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.2, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);

    whiteNoise.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);
    whiteNoise.start(now);
    whiteNoise.stop(now + 0.13);
  }

  _triggerHiHat(ctx, now, isRoll = false) {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "square";
    osc.frequency.setValueAtTime(8000, now);
    gain.gain.setValueAtTime(isRoll ? 0.04 : 0.07, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + (isRoll ? 0.03 : 0.05));
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.06);
  }

  _trigger808(ctx, now, freq) {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(freq * 1.5, now);
    osc.frequency.exponentialRampToValueAtTime(freq, now + 0.04);
    gain.gain.setValueAtTime(0.35, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.3);
  }

  _triggerPluck(ctx, now, freq) {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(freq, now);
    gain.gain.setValueAtTime(0.12, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.38);
  }
}

export const battleAudio = new BattleAudioEngine();
