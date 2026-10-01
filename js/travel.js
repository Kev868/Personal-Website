/* Travel: two banks of cloud roll in from either side, meet in the middle,
   and part on the new place. Whatever changes the scene runs while the
   clouds are closed, so nothing is ever seen swapping.

   Under reduced motion the clouds stay put and the screen just fades
   through paper instead. */

import { state } from './state.js';
import { play } from './sound.js';

const layer = document.querySelector('.travel');
const left = layer.querySelector('.travel-cloud--l');
const right = layer.querySelector('.travel-cloud--r');
let busy = false;

/* The stylesheet parks the clouds off-screen with translateX so they never
   flash before this runs. GSAP would read that as x and add xPercent on top,
   parking them twice as far away, where closing only reaches the screen's
   edge. So x is zeroed and the offset handed over to xPercent entirely. */
gsap.set(left, { x: 0, xPercent: -102 });
gsap.set(right, { x: 0, xPercent: 102 });

function tweenTo(xl, xr, duration, ease, delay = 0) {
  return new Promise((resolve) => {
    gsap.timeline({ onComplete: resolve, delay })
      .to(left, { xPercent: xl, duration, ease }, 0)
      .to(right, { xPercent: xr, duration, ease }, 0);
  });
}

function fade(to) {
  return new Promise((resolve) => {
    gsap.to(layer, { backgroundColor: to ? 'rgba(240,230,204,1)' : 'rgba(240,230,204,0)', duration: 0.35, onComplete: resolve });
  });
}

/* Closed, the banks rest at 0: css/palace.css sizes them so that each one's
   solid part already reaches past the middle of the screen. */

export async function close() {
  layer.classList.add('is-closed');
  if (state.calm) return fade(true);
  play('whoosh');
  return tweenTo(0, 0, 0.8, 'power3.inOut');
}

export async function open() {
  if (state.calm) await fade(false);
  else await tweenTo(-102, 102, 0.95, 'power3.inOut', 0.08);
  layer.classList.remove('is-closed');
}

/* Start covered, for arrivals: the clouds are already there and only part. */
export function coverNow() {
  layer.classList.add('is-closed');
  if (state.calm) gsap.set(layer, { backgroundColor: 'rgba(240,230,204,1)' });
  else gsap.set([left, right], { xPercent: 0 });
}

/* Close, run `midway` behind the clouds, open. `parting` runs the moment
   the clouds begin to part, for anything that should play as the new place
   is revealed rather than before it (the edicts unrolling). Calls made while
   a journey is under way are dropped rather than queued: a double click
   should not make the visitor travel twice. */
export async function travel(midway, parting) {
  if (busy) return false;
  busy = true;
  try {
    await close();
    await midway?.();
    parting?.();
    await open();
  } finally {
    busy = false;
  }
  return true;
}
