/* The project halls. A work card is a link to #/hall/<key>; following it
   brings the clouds in, and behind them the page is swapped for that
   project's hall with its edict unrolling. Each hall has its own address,
   so Back leaves it and a link can open one directly.

   The halls are the <template id="tpl-KEY"> blocks at the end of
   index.html. Previous and next follow the order of the cards on the page. */

import { state, lockScroll, trapTab } from './state.js';
import { travel, coverNow, open as openClouds } from './travel.js';

const ROUTE = /^#\/hall\/([\w-]+)$/;
const room = document.getElementById('room');
const content = room.querySelector('.edict-content');
const paper = room.querySelector('.edict-paper');
const lowerRoller = room.querySelector('.edict-roller--bottom');
const prevBtn = room.querySelector('.room-nav--prev');
const nextBtn = room.querySelector('.room-nav--next');

let current = null;      // key of the hall on screen
let opener = null;       // the card that led here, for focus on the way out
let pushed = false;      // whether we added the history entry we are on

const order = () => [...document.querySelectorAll('.work-link[href^="#/hall/"]')]
  .map((a) => a.getAttribute('href').replace('#/hall/', ''));

export function initRooms() {
  room.setAttribute('data-lenis-prevent', '');

  document.addEventListener('click', (e) => {
    const link = e.target.closest?.('a[href^="#/hall/"]');
    if (!link || e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault();
    const key = link.getAttribute('href').replace('#/hall/', '');
    opener = link;
    history.pushState({ hall: key }, '', `#/hall/${key}`);
    pushed = true;
    enter(key);
  });

  addEventListener('popstate', () => {
    const m = location.hash.match(ROUTE);
    if (m) enter(m[1]);
    else if (current) leave({ fromHistory: true });
  });

  room.querySelector('.room-leave').addEventListener('click', () => leave());
  prevBtn.addEventListener('click', () => step(-1));
  nextBtn.addEventListener('click', () => step(1));

  document.addEventListener('keydown', (e) => {
    if (!current || !document.getElementById('lightbox').hidden) return;
    if (e.key === 'Escape') leave();
    else if (e.key === 'ArrowLeft') step(-1);
    else if (e.key === 'ArrowRight') step(1);
    else trapTab(e, room);
  });

  /* Arriving by a link straight to a hall: start behind the clouds. */
  const m = location.hash.match(ROUTE);
  if (m && document.getElementById(`tpl-${m[1]}`)) {
    coverNow();
    fill(m[1]);
    show();
    rollUp();
    openClouds();
    unroll();
  }
}

function fill(key) {
  const tpl = document.getElementById(`tpl-${key}`);
  if (!tpl) return false;
  content.replaceChildren(tpl.content.cloneNode(true));
  room.dataset.wing = tpl.dataset.wing || 'east';
  room.setAttribute('aria-label', tpl.dataset.title || 'Project');

  const keys = order();
  const i = keys.indexOf(key);
  for (const [btn, j] of [[prevBtn, i - 1], [nextBtn, i + 1]]) {
    const k = keys[(j + keys.length) % keys.length];
    const t = document.getElementById(`tpl-${k}`);
    const num = t?.content.querySelector('.detail-num')?.textContent || '';
    btn.querySelector('.room-nav-num').textContent = num;
    btn.querySelector('.room-nav-name').textContent = t?.dataset.title || '';
    btn.dataset.key = k;
    btn.hidden = keys.length < 2;
  }
  current = key;
  return true;
}

function show() {
  room.hidden = false;
  room.scrollTop = 0;
  lockScroll(true);
  room.querySelector('.room-leave').focus({ preventScroll: true });
}

/* The paper comes down from the upper roller like an edict being read out.
   It is rolled up while the clouds still cover it, and unrolls as they
   part, so it is never seen open first and then snapped shut. */
function rollUp() {
  if (state.calm) return;
  gsap.killTweensOf([paper, lowerRoller]);
  gsap.set(paper, { clipPath: 'inset(0 0 100% 0)' });
  gsap.set(lowerRoller, { y: -paper.offsetHeight });
}

function unroll() {
  if (state.calm) return;
  const at = { duration: 1.3, ease: 'power2.inOut', delay: 0.35 };
  gsap.to(paper, { ...at, clipPath: 'inset(0 0 0% 0)', clearProps: 'clipPath' });
  gsap.to(lowerRoller, { ...at, y: 0, clearProps: 'transform' });
}

function enter(key) {
  if (!document.getElementById(`tpl-${key}`)) return;
  if (key === current && !room.hidden) return;
  travel(() => { fill(key); show(); rollUp(); }, unroll);
}

function step(dir) {
  const key = (dir < 0 ? prevBtn : nextBtn).dataset.key;
  if (!key) return;
  history.replaceState({ hall: key }, '', `#/hall/${key}`);
  enter(key);
}

async function leave({ fromHistory = false } = {}) {
  if (!current) return;
  if (!fromHistory && pushed) { history.back(); return; }   // popstate calls us again
  if (!fromHistory) history.replaceState(null, '', location.pathname + location.search);
  pushed = false;
  await travel(() => {
    room.hidden = true;
    current = null;
    lockScroll(false);
  });
  opener?.focus({ preventScroll: true });
}
