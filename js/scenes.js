/* Everything scroll moves: parallax, and the doors of the software hall.
   Plus the gate's own entrance, played once. */

import { state } from './state.js';

let entry = null;   // the doors' ScrollTrigger

export function initScenes() {
  if (state.calm) return;
  initEntry();        // first: its pin shifts every trigger below it
  initParallax();
  initSheen();
  initBannerSway();
}

/* Where a link to the software hall should land: at the doors, still shut
   ("Enter the palace"), or through them, inside. Null when there are no
   doors (reduced motion), and the hall is simply its own anchor. */
export function entryScroll(where) {
  if (!entry) return null;
  return where === 'doors' ? entry.start : entry.end + 1;
}

function glide(y, duration = 1.6) {
  if (state.lenis) state.lenis.scrollTo(y, { duration });
  else scrollTo({ top: y, behavior: 'smooth' });
}

/* The gate comes down as one piece, roof, pillars and all, then its plaque
   and lanterns settle and the name is brushed on stroke by stroke. Called by
   js/ui.js once the arrival (if any) has cleared. Everything starts from its
   visible resting state, so a failure here leaves a finished page rather
   than a blank one. The plaque's centring is a CSS transform, so its tween
   hands the transform back to CSS when done. */
export function revealGate() {
  if (state.calm) return;
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
  tl.from('.gate-arch', { y: -70, opacity: 0, duration: 1.3 }, 0)
    .from('.gate-arch .arch-plaque', { y: -24, opacity: 0, duration: 0.8, clearProps: 'transform' }, 0.55)
    .from('.gate-lanterns', { y: -36, opacity: 0, duration: 1.1, ease: 'back.out(1.6)' }, 0.8)
    .from('.banner', { y: -60, rotate: -4, opacity: 0, duration: 1.4, ease: 'elastic.out(1, 0.55)' }, 0.3)
    .from('.gate-hi', { y: 14, opacity: 0, duration: 0.7 }, 0.45)
    .fromTo('.ink-word',
      { clipPath: 'inset(0 100% 0 0)', filter: 'blur(6px)' },
      { clipPath: 'inset(0 0% 0 0)', filter: 'blur(0px)', duration: 0.9, stagger: 0.18, ease: 'power2.out',
        clearProps: 'clipPath,filter' }, 0.55)
    .from('.about > *, .gate-cta, .socials', { y: 18, opacity: 0, duration: 0.7, stagger: 0.06 }, 0.95)
    .from('.cred', { x: 30, opacity: 0, duration: 0.7, stagger: 0.1 }, 1.0)
    .from('.cloudline--gate .cloud', { yPercent: 30, opacity: 0, duration: 1.6, stagger: 0.15 }, 0);
  return tl;
}

/* The doors of the software hall. The hall is pinned while you scroll: the
   doors swing in, then you walk through, the frame growing past you while
   the hall, clipped until now to the doorway, opens out to its full shape.
   The clip is measured each frame from where the doorway actually is on
   screen, so the hall seen through it cannot drift out of step with it:
   there is one hall and one ceiling, not a picture of them. */
function initEntry() {
  const hall = document.querySelector('#software');
  const frame = hall?.querySelector('.entry-frame');
  if (!frame) return;
  const doorway = frame.querySelector('.doorway');
  const shell = hall.querySelector('.hall-shell');
  const narrow = matchMedia('(max-width: 860px)').matches;
  const OPEN = 0.4;                                   // doors open by here
  const FADE = 0.84;                                  // the frame fades from here
  const blend = gsap.parseEase('sine.inOut');
  const cut = parseFloat(getComputedStyle(shell).getPropertyValue('--oct-cut-lg')) || 22;

  /* Scale about the doorway's centre, so walking in heads through it. */
  const aim = () => {
    let y = doorway.offsetHeight / 2;
    for (let el = doorway; el && el !== frame; el = el.offsetParent) y += el.offsetTop;
    gsap.set(frame, { transformOrigin: `50% ${y}px` });
  };

  /* Before you walk in, the hall stands back: lower, so the doorway frames
     its ceiling rather than cutting through its title, and smaller, as far
     things are. It comes forward to its place as you walk through. */
  const setBack = () => {
    let y = 0;
    for (let el = doorway; el && el !== hall; el = el.offsetParent) y += el.offsetTop;
    return Math.max(0, y - shell.offsetTop - 12);
  };
  gsap.set(shell, { transformOrigin: '50% 0%' });

  /* The hall's clip, in its own (untransformed) coordinates: the doorway's
     rectangle, as the octagon's eight points so the one can become the
     other, blended into the octagon while the frame fades. At the end the
     stylesheet's own octagon takes over again. */
  const clip = (p) => {
    if (p >= 1) { shell.style.clipPath = ''; return; }
    const s = shell.getBoundingClientRect();
    const d = doorway.getBoundingClientRect();
    const W = shell.offsetWidth, H = shell.offsetHeight, c = cut;
    const k = s.width / W || 1;
    const x = (v) => Math.min(W, Math.max(0, (v - s.left) / k));
    const y = (v) => Math.min(H, Math.max(0, (v - s.top) / k));
    const L = x(d.left), R = x(d.right), T = y(d.top), B = y(d.bottom);
    const from = [[L, T], [R, T], [R, T], [R, B], [R, B], [L, B], [L, B], [L, T]];
    const to = [[c, 0], [W - c, 0], [W, c], [W, H - c], [W - c, H], [c, H], [0, H - c], [0, c]];
    const q = blend(Math.max(0, (p - FADE) / (1 - FADE)));
    shell.style.clipPath = `polygon(${from.map(([x, y], i) =>
      `${(x + (to[i][0] - x) * q).toFixed(1)}px ${(y + (to[i][1] - y) * q).toFixed(1)}px`).join(', ')})`;
  };

  const tl = gsap.timeline({
    defaults: { ease: 'none' },
    onUpdate() { clip(this.progress()); },
    scrollTrigger: {
      trigger: hall, start: 'top top', end: () => `+=${innerHeight * (narrow ? 1 : 1.2)}`,
      pin: true, anticipatePin: 1, scrub: 0.6, invalidateOnRefresh: true,
      onRefresh: (self) => { aim(); clip(self.animation?.progress() ?? 0); },
    },
  });
  /* Palace doors swing inward, away from you: the free edge recedes. */
  tl.to('.entry-hint', { opacity: 0, duration: 0.08 }, 0)
    .to('.door--l', { rotateY: 96, ease: 'power2.inOut', duration: OPEN }, 0)
    .to('.door--r', { rotateY: -96, ease: 'power2.inOut', duration: OPEN }, 0)
    .to(frame, { scale: narrow ? 2.1 : 2.5, ease: 'power2.in', duration: 1 - OPEN }, OPEN)
    .fromTo(shell, { y: setBack, scale: 0.86 }, { y: 0, scale: 1, ease: 'power2.in', duration: 1 - OPEN }, OPEN)
    .to(frame, { autoAlpha: 0, duration: 1 - FADE }, FADE);
  entry = tl.scrollTrigger;
  aim();
  clip(0);

  /* A knock opens them: walk through to the hall. */
  frame.querySelector('.door--l').addEventListener('click', () => glide(entryScroll('inside'), 2.4));
}

function initParallax() {
  document.querySelectorAll('[data-speed]').forEach((el) => {
    const speed = parseFloat(el.dataset.speed) || 0;
    gsap.fromTo(el, { y: () => -speed * innerHeight * 0.5 }, {
      y: () => speed * innerHeight * 0.5, ease: 'none',
      scrollTrigger: { trigger: el.parentElement, start: 'top bottom', end: 'bottom top', scrub: true, invalidateOnRefresh: true },
    });
  });
  gsap.to('.sky-isles', {
    y: -90, ease: 'none',
    scrollTrigger: { trigger: '#palace', start: 'top top', end: 'bottom bottom', scrub: true },
  });
  document.querySelectorAll('.giant').forEach((g) => {
    gsap.fromTo(g, { yPercent: 18 }, {
      yPercent: -18, ease: 'none',
      scrollTrigger: { trigger: g.closest('section'), start: 'top bottom', end: 'bottom top', scrub: true },
    });
  });
}

/* Gold catches the light as a hall title crosses the screen. */
function initSheen() {
  document.querySelectorAll('.hall-title').forEach((t) => {
    gsap.fromTo(t, { '--sheen': '100%' }, {
      '--sheen': '0%', ease: 'none',
      scrollTrigger: { trigger: t, start: 'top bottom', end: 'bottom top', scrub: true },
    });
  });
}

/* The banner hangs on a cord: pointer movement pushes it, a spring brings it
   back. Rotation is about the top point, where the cord ties on. */
function initBannerSway() {
  const banner = document.querySelector('[data-sway]');
  if (!banner || !state.fine) return;
  let angle = 0, velocity = 0, push = 0, lastX = null;
  addEventListener('pointermove', (e) => {
    if (lastX !== null) push += (e.clientX - lastX) * 0.012;
    lastX = e.clientX;
  }, { passive: true });
  gsap.ticker.add((time) => {
    const idle = Math.sin(time * 0.9) * 0.6;
    velocity += (idle - angle) * 0.02 + push * 0.05;
    velocity *= 0.9;
    push *= 0.6;
    angle = Math.max(-5, Math.min(5, angle + velocity));
    banner.style.rotate = `${angle.toFixed(3)}deg`;
  });
}
