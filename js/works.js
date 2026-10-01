/* The Hall of Works: seal filters, the two views, and the small things a
   card does under the pointer. Built to hold far more than four projects:
   the Register view is the one that scales, and filters reflow with Flip so
   the eye can follow each card to its new place. */

import { state } from './state.js';

export function initWorks() {
  document.querySelectorAll('.works').forEach((list) => {
    list.querySelectorAll('.work-link').forEach((link) => {
      const arrow = document.createElement('span');
      arrow.className = 'register-arrow';
      arrow.setAttribute('aria-hidden', 'true');
      arrow.textContent = '→';
      link.append(arrow);
    });
    const shell = list.closest('.hall-shell');
    initFilters(shell, list);
    initViews(shell, list);
  });
  if (state.fine && !state.calm) initCardLight();
  if (state.fine) initRegisterPreview();
}

function reflow(list, change) {
  const items = [...list.children];
  if (state.calm) { change(); return; }
  const before = Flip.getState(items);
  change();
  Flip.from(before, {
    duration: 0.75, ease: 'power3.inOut', absolute: true, scale: false,
    onEnter: (els) => gsap.fromTo(els, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.55, delay: 0.15 }),
    onLeave: (els) => gsap.to(els, { opacity: 0, y: -12, duration: 0.3 }),
  });
}

function initFilters(shell, list) {
  const chips = shell?.querySelectorAll('.seal-chip');
  if (!chips?.length) return;
  const empty = shell.querySelector('.works-empty');
  chips.forEach((chip) => chip.addEventListener('click', () => {
    if (chip.getAttribute('aria-pressed') === 'true') return;
    chips.forEach((c) => c.setAttribute('aria-pressed', String(c === chip)));
    if (!state.calm) {
      gsap.fromTo(chip.querySelector('.seal-zh'),
        { scale: 1.35, rotate: -9 }, { scale: 1, rotate: 0, duration: 0.45, ease: 'back.out(3)' });
    }
    const f = chip.dataset.filter;
    reflow(list, () => {
      let shown = 0;
      [...list.children].forEach((li) => {
        const match = f === 'all' || li.dataset.cats.split(' ').includes(f);
        li.classList.toggle('is-hidden', !match);
        shown += match;
      });
      if (empty) empty.hidden = shown > 0;
    });
  }));
}

function initViews(shell, list) {
  const buttons = shell?.querySelectorAll('.view-toggle button');
  if (!buttons?.length) return;
  buttons.forEach((b) => b.addEventListener('click', () => {
    if (b.getAttribute('aria-pressed') === 'true') return;
    buttons.forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    reflow(list, () => { list.dataset.view = b.dataset.view; });
  }));
}

/* Lantern light follows the pointer across a card; the card leans toward it. */
function initCardLight() {
  document.addEventListener('pointermove', (e) => {
    const card = e.target.closest?.('.works[data-view="gallery"] .work-link');
    if (!card) return;
    const r = card.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
    card.style.setProperty('--mx', `${(x * 100).toFixed(1)}%`);
    card.style.setProperty('--my', `${(y * 100).toFixed(1)}%`);
    card.style.setProperty('--tilt-x', `${((0.5 - y) * 5).toFixed(2)}deg`);
    card.style.setProperty('--tilt-y', `${((x - 0.5) * 5).toFixed(2)}deg`);
  }, { passive: true });
  document.addEventListener('pointerout', (e) => {
    const card = e.target.closest?.('.work-link');
    if (card && !card.contains(e.relatedTarget)) {
      card.style.setProperty('--tilt-x', '0deg');
      card.style.setProperty('--tilt-y', '0deg');
    }
  });
}

/* In the Register, a project's picture floats beside the pointer. */
function initRegisterPreview() {
  const box = document.createElement('div');
  box.className = 'register-preview';
  box.setAttribute('aria-hidden', 'true');
  const img = document.createElement('img');
  img.alt = '';
  box.append(img);
  document.body.append(box);
  const moveX = gsap.quickTo(box, 'x', { duration: 0.45, ease: 'power3' });
  const moveY = gsap.quickTo(box, 'y', { duration: 0.45, ease: 'power3' });

  document.addEventListener('pointerover', (e) => {
    const link = e.target.closest?.('.works[data-view="register"] .work-link');
    const pic = link?.querySelector('.work-media img');
    if (!pic) { box.classList.remove('is-on'); return; }
    if (img.src !== pic.currentSrc) img.src = pic.currentSrc || pic.src;
    box.classList.add('is-on');
  });
  document.addEventListener('pointermove', (e) => {
    moveX(e.clientX + 190);
    moveY(e.clientY);
  }, { passive: true });
  document.addEventListener('scroll', () => box.classList.remove('is-on'), { passive: true });
}
