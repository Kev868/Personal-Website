/* One day in the heavens, walked rather than waited for.

   Each scene owns a time of day. When a scene reaches the middle of the
   screen the sky eases to its time: dawn at the gate, noon in the east
   wing, golden hour in the west, sunset at the library, night at the bell
   tower. The sky is only custom properties on :root, so anything can read
   the current light. */

import { state } from './state.js';

const TIMES = {
  dawn: {
    '--cloud-b': 1,
    '--sky-top': '#e7c595', '--sky-mid': '#f3dcb6', '--sky-low': '#fbf1dc',
    '--sun': 'rgba(255,232,178,0.95)', '--sun-y': '34%', '--stars': 0,
    '--wave': 'rgba(201,162,74,0.16)',
  },
  noon: {
    '--cloud-b': 1,
    '--sky-top': '#b9d0d8', '--sky-mid': '#e2e6da', '--sky-low': '#f6eedb',
    '--sun': 'rgba(255,250,228,0.85)', '--sun-y': '10%', '--stars': 0,
    '--wave': 'rgba(201,162,74,0.13)',
  },
  golden: {
    '--cloud-b': 0.95,
    '--sky-top': '#d49a58', '--sky-mid': '#eec78c', '--sky-low': '#f8e4bd',
    '--sun': 'rgba(255,212,138,0.95)', '--sun-y': '34%', '--stars': 0,
    '--wave': 'rgba(201,162,74,0.18)',
  },
  sunset: {
    '--cloud-b': 0.72,
    '--sky-top': '#5e2f48', '--sky-mid': '#b9563f', '--sky-low': '#eb9a5e',
    '--sun': 'rgba(255,168,96,0.9)', '--sun-y': '66%', '--stars': 0.25,
    '--wave': 'rgba(255,190,120,0.12)',
  },
  night: {
    '--cloud-b': 0.3,
    '--sky-top': '#070b1f', '--sky-mid': '#161a38', '--sky-low': '#2e2444',
    '--sun': 'rgba(255,240,205,0.16)', '--sun-y': '16%', '--stars': 1,
    '--wave': 'rgba(180,170,255,0.06)',
  },
};

/* A scene's time arrives as its top passes the middle of the screen, or
   earlier where its words are drawn for that time: the library's cream
   lettering only reads once the sun is setting. */
const SCENES = [
  ['#gate', 'dawn'],
  ['#software', 'noon'],
  ['#hardware', 'golden'],
  ['#library', 'sunset', 'top 88%'],
  ['#contact', 'night'],
];

export function initSky() {
  const root = document.documentElement;
  gsap.set(root, TIMES.dawn);

  for (const [selector, time, start = 'top 55%'] of SCENES) {
    const scene = document.querySelector(selector);
    if (!scene) continue;
    ScrollTrigger.create({
      trigger: scene,
      start,
      end: 'bottom 55%',
      onToggle: (self) => {
        if (!self.isActive) return;
        gsap.to(root, { ...TIMES[time], duration: state.calm ? 0.01 : 1.8, ease: 'sine.inOut', overwrite: 'auto' });
      },
    });
  }

  drawStars(document.querySelector('.sky-stars'));
}

/* A fixed field of stars, drawn once per size. Its opacity is --stars, so it
   fades in with the evening rather than being redrawn. */
function drawStars(canvas) {
  if (!canvas) return;
  const paint = () => {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    const w = canvas.clientWidth, h = canvas.clientHeight;
    canvas.width = w * dpr; canvas.height = h * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    let seed = 7;
    const rand = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    const count = Math.round((w * h) / 5200);
    for (let i = 0; i < count; i++) {
      const x = rand() * w, y = rand() * h * 0.78;
      const r = rand() < 0.08 ? 1.5 : 0.55 + rand() * 0.7;
      ctx.globalAlpha = 0.35 + rand() * 0.65 * (1 - y / h);
      ctx.fillStyle = rand() < 0.15 ? '#ffe7b0' : '#f4f1ff';
      ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
    }
  };
  paint();
  let t;
  addEventListener('resize', () => { clearTimeout(t); t = setTimeout(paint, 200); });
}
