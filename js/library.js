/* The library: the résumé as a handscroll. It unrolls from the left roller
   to the right, and reads sideways: the wheel scrolls it horizontally, and
   it can be dragged like paper. On narrow screens it hangs vertically
   instead and scrolls the ordinary way. */

import { state, lockScroll, trapTab } from './state.js';
import { travel } from './travel.js';

const scroll = document.getElementById('handscroll');
const paper = scroll.querySelector('.handscroll-paper');
const endRoller = scroll.querySelector('.handscroll-roller--end');
const sideways = () => matchMedia('(min-width: 861px)').matches;
let opener = null;

export function initLibrary() {
  paper.setAttribute('data-lenis-prevent', '');

  document.querySelectorAll('[data-open="library"]').forEach((b) => b.addEventListener('click', (e) => {
    e.preventDefault();
    opener = b;
    travel(() => {
      scroll.hidden = false;
      paper.scrollLeft = 0;
      paper.scrollTop = 0;
      lockScroll(true);
      scroll.querySelector('.handscroll-close').focus({ preventScroll: true });
      rollUp();
    }, unroll);
  }));

  scroll.querySelector('.handscroll-close').addEventListener('click', close);
  document.addEventListener('keydown', (e) => {
    if (scroll.hidden) return;
    if (e.key === 'Escape') close();
    else trapTab(e, scroll);
  });

  /* Vertical wheel reads along the scroll. */
  paper.addEventListener('wheel', (e) => {
    if (!sideways() || Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
    e.preventDefault();
    paper.scrollLeft += e.deltaY;
  }, { passive: false });

  initDrag();
}

/* Rolled up behind the clouds, unrolled as they part: see js/room.js. */
function rollUp() {
  if (state.calm) return;
  gsap.killTweensOf([paper, endRoller]);
  if (sideways()) {
    gsap.set(paper, { clipPath: 'inset(0 100% 0 0)' });
    gsap.set(endRoller, { x: -paper.offsetWidth });
  } else {
    gsap.set(paper, { clipPath: 'inset(0 0 100% 0)' });
  }
}

function unroll() {
  if (state.calm) return;
  const at = { duration: sideways() ? 1.5 : 1.2, ease: 'power2.inOut', delay: 0.35 };
  gsap.to(paper, { ...at, clipPath: 'inset(0 0% 0 0)', clearProps: 'clipPath' });
  if (sideways()) gsap.to(endRoller, { ...at, x: 0, clearProps: 'transform' });
}

function close() {
  travel(() => {
    scroll.hidden = true;
    lockScroll(false);
  }).then(() => opener?.focus({ preventScroll: true }));
}

/* Drag to read. A press only becomes a drag after a few pixels, so the links
   on the scroll still click. */
function initDrag() {
  let startX = 0, startLeft = 0, dragging = false, pressed = false;
  paper.addEventListener('pointerdown', (e) => {
    if (!sideways() || e.pointerType !== 'mouse' || e.button !== 0) return;
    pressed = true; dragging = false;
    startX = e.clientX; startLeft = paper.scrollLeft;
  });
  addEventListener('pointermove', (e) => {
    if (!pressed) return;
    const dx = e.clientX - startX;
    if (!dragging && Math.abs(dx) > 5) {
      dragging = true;
      paper.classList.add('is-dragging');
      paper.setPointerCapture?.(e.pointerId);
    }
    if (dragging) paper.scrollLeft = startLeft - dx;
  });
  addEventListener('pointerup', () => {
    if (dragging) {
      /* Swallow the click that ends a drag, so it does not follow a link.
         Only that click: if none comes, the listener expires on the next
         tick instead of eating some later, unrelated one. */
      const swallow = (ev) => { ev.preventDefault(); ev.stopPropagation(); };
      addEventListener('click', swallow, { capture: true, once: true });
      setTimeout(() => removeEventListener('click', swallow, { capture: true }), 0);
    }
    pressed = false; dragging = false;
    paper.classList.remove('is-dragging');
  });
}
