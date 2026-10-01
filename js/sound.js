/* Sound: off until asked for, and absent until there is something to play.

   assets/audio/manifest.json names the files, for example
     { "ambient": "ambient.mp3", "whoosh": "whoosh.mp3" }
   ambient is the quiet guzheng or guqin loop, whoosh the clouds rolling in.
   With no ambient track listed, the nav's sound toggle stays hidden. Asking
   a manifest, rather than probing for each file, keeps missing files from
   showing up as errors in the console.

   Browsers refuse to play sound before the visitor has clicked something,
   so the loop only ever starts from the toggle. */

const MANIFEST = 'assets/audio/manifest.json';
const AMBIENT_VOLUME = 0.32;
const KEY = 'palace-sound';

const tracks = {};
let on = false;

export async function initSound() {
  const toggle = document.querySelector('.sound-toggle');
  let files = {};
  try { files = await (await fetch(MANIFEST)).json(); } catch {}
  for (const [name, file] of Object.entries(files)) {
    if (!file) continue;
    const audio = new Audio(`assets/audio/${file}`);
    audio.preload = name === 'whoosh' ? 'auto' : 'none';
    tracks[name] = audio;
  }
  if (!tracks.ambient || !toggle) return;
  tracks.ambient.loop = true;
  toggle.hidden = false;
  toggle.addEventListener('click', () => set(!on));
  /* Remembered, but only acted on once the visitor has clicked anything. */
  let wanted = false;
  try { wanted = localStorage.getItem(KEY) === 'on'; } catch {}
  if (wanted) addEventListener('pointerdown', () => set(true), { once: true });
}

function set(next) {
  on = next;
  const toggle = document.querySelector('.sound-toggle');
  toggle?.setAttribute('aria-pressed', String(on));
  try { localStorage.setItem(KEY, on ? 'on' : 'off'); } catch {}
  const amb = tracks.ambient;
  if (!amb) return;
  if (on) {
    amb.volume = 0;
    amb.play().then(() => gsap.to(amb, { volume: AMBIENT_VOLUME, duration: 2.5 })).catch(() => {});
  } else {
    gsap.to(amb, { volume: 0, duration: 0.8, onComplete: () => amb.pause() });
  }
}

export function play(name) {
  const t = tracks[name];
  if (!on || !t) return;
  t.currentTime = 0;
  t.volume = 0.5;
  t.play().catch(() => {});
}
