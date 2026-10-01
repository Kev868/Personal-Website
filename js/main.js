/* The palace, assembled. GSAP, ScrollTrigger, Flip and Lenis are loaded as
   deferred scripts before this module, so their globals exist by now. */

import { state } from './state.js';
import { applyType } from './type.js';
import { initSky } from './sky.js';
import { initScenes, entryScroll } from './scenes.js';
import { initWorks } from './works.js';
import { initRooms } from './room.js';
import { initLibrary } from './library.js';
import { initUI, arrive } from './ui.js';
import { initSound } from './sound.js';

applyType();
gsap.registerPlugin(ScrollTrigger, Flip);

/* Smooth scrolling, driven by GSAP's clock so scroll-linked scenes and the
   scroll itself move on the same frame. */
if (!state.calm) {
  state.lenis = new Lenis({ lerp: 0.085 });
  state.lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((t) => state.lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0);
}

/* In-page anchors glide rather than jump. Hall links (#/hall/...) are routes,
   not anchors, and belong to js/room.js. The software hall stands behind its
   doors: "Enter the palace" stops at them, the nav's link walks you in. */
document.addEventListener('click', (e) => {
  const a = e.target.closest?.('a[href^="#"]');
  const href = a?.getAttribute('href');
  if (!href || href === '#' || href.startsWith('#/')) return;
  const target = document.querySelector(href);
  if (!target) return;
  e.preventDefault();
  const doors = href === '#software' ? entryScroll(a.dataset.to === 'doors' ? 'doors' : 'inside') : null;
  if (doors !== null) state.lenis.scrollTo(doors, { duration: 1.6 });
  else if (state.lenis) state.lenis.scrollTo(target, { offset: href === '#gate' ? 0 : -62, duration: 1.6 });
  else target.scrollIntoView({ behavior: state.calm ? 'auto' : 'smooth' });
});

/* Scenes before the sky: the doors pin the software hall, and triggers made
   after that pin are measured with the room it takes already counted. */
initUI();
initScenes();
initSky();
initWorks();
initRooms();
initLibrary();
initSound();

/* Fonts change line lengths, and line lengths move every trigger point. */
document.fonts?.ready.then(() => ScrollTrigger.refresh());

arrive();
