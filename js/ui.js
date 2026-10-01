/* The small things: the arrival, the cursor, the lightbox, "more about me". */

import { state, lockScroll } from './state.js';
import { coverNow, open as openClouds } from './travel.js';
import { revealGate } from './scenes.js';

export function initUI() {
  initAbout();
  initLightbox();
  if (state.fine && !state.calm) initCursor();
}

/* First visit: the seal presses onto the paper, the ink settles, and the
   clouds part on the gate. Later visits in the same session go straight to
   the gate's own entrance. The class that shows the arrival is set in
   <head> before first paint, so the gate never flashes underneath. */
export function arrive() {
  const html = document.documentElement;
  if (!html.classList.contains('arrive')) { revealGate(); return; }
  try { sessionStorage.setItem('arrived', '1'); } catch {}
  const veil = document.querySelector('.arrival');
  lockScroll(true);
  gsap.timeline()
    .fromTo('.arrival-seal', { scale: 1.6, opacity: 0, rotate: -8 }, { scale: 1, opacity: 1, rotate: 0, duration: 0.55, ease: 'power4.in' })
    .to('.arrival-seal', { scale: 0.96, duration: 0.08, yoyo: true, repeat: 1 })
    .fromTo('.arrival-ink', { scale: 0.6, opacity: 0.9 }, { scale: 2.4, opacity: 0, duration: 1.1, ease: 'power2.out' }, '<')
    .to({}, { duration: 0.35 })
    .add(() => {
      coverNow();
      html.classList.remove('arrive');
      veil.style.display = 'none';
      lockScroll(false);
      openClouds();
      revealGate();
    });
}

function initAbout() {
  const btn = document.querySelector('.about-more');
  const extra = document.getElementById('about-extra');
  btn?.addEventListener('click', () => {
    const opening = extra.hidden;
    extra.hidden = !opening;
    btn.textContent = opening ? 'less about me ↑' : 'more about me →';
    btn.setAttribute('aria-expanded', String(opening));
  });
}

/* Any .zoom image, including ones cloned into a hall, opens full size. */
function initLightbox() {
  const lb = document.getElementById('lightbox');
  const img = lb.querySelector('img');
  const cap = lb.querySelector('.lightbox-cap');
  const closeBtn = lb.querySelector('.lightbox-close');
  let back = null;
  const close = () => {
    lb.hidden = true;
    img.removeAttribute('src');
    back?.focus({ preventScroll: true });
  };
  document.addEventListener('click', (e) => {
    const z = e.target.closest?.('.zoom');
    if (!z) return;
    back = document.activeElement;
    img.src = z.currentSrc || z.src;
    img.alt = z.alt || '';
    cap.textContent = z.dataset.caption || z.alt || '';
    lb.hidden = false;
    closeBtn.focus({ preventScroll: true });
  });
  lb.addEventListener('click', (e) => { if (e.target === lb) close(); });
  closeBtn.addEventListener('click', close);
  document.addEventListener('keydown', (e) => {
    if (!lb.hidden && e.key === 'Escape') { e.stopImmediatePropagation(); close(); }
  }, { capture: true });
}

/* A gilt diamond that trails the pointer and names what a click will do. */
function initCursor() {
  const cursor = document.querySelector('.cursor');
  const label = cursor.querySelector('.cursor-label');
  document.documentElement.classList.add('has-cursor');
  const x = gsap.quickTo(cursor, 'x', { duration: 0.22, ease: 'power3' });
  const y = gsap.quickTo(cursor, 'y', { duration: 0.22, ease: 'power3' });
  addEventListener('pointermove', (e) => { x(e.clientX); y(e.clientY); }, { passive: true });
  document.addEventListener('pointerover', (e) => {
    const t = e.target.closest?.('a, button, [data-cursor], .zoom');
    cursor.classList.toggle('is-active', !!t);
    const text = t?.dataset.cursor || (t?.classList.contains('zoom') ? 'View' : '');
    label.textContent = text;
    cursor.classList.toggle('has-label', !!text);
  });
  document.addEventListener('pointerleave', () => cursor.classList.remove('is-active', 'has-label'));
}
