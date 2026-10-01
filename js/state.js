/* What every module needs to agree on. */

export const state = {
  /* Reduced motion: nothing moves on its own, travel becomes a fade. */
  calm: matchMedia('(prefers-reduced-motion: reduce)').matches,
  /* A mouse or trackpad. Tilt, the custom cursor and hover previews need one. */
  fine: matchMedia('(pointer: fine)').matches,
  lenis: null,
};

/* Freeze the page behind an overlay. Lenis keeps its own scroll state, so it
   has to be told as well as the document. */
export function lockScroll(on) {
  if (state.lenis) on ? state.lenis.stop() : state.lenis.start();
  document.documentElement.classList.toggle('is-locked', on);
}

export function focusables(el) {
  return [...el.querySelectorAll('a[href],button:not([disabled]),[tabindex]:not([tabindex="-1"])')]
    .filter((n) => n.offsetParent !== null || n === document.activeElement);
}

/* Keep Tab inside an open overlay. */
export function trapTab(e, container) {
  if (e.key !== 'Tab') return;
  const f = focusables(container);
  if (!f.length) return;
  const first = f[0], last = f[f.length - 1];
  if (!container.contains(document.activeElement)) { e.preventDefault(); first.focus(); }
  else if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
  else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
}
