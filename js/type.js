/* ?type=b|c|today tries another typeface pairing without touching the CSS.
   Pairing A is the default and needs nothing. The tokens for each live in
   css/palace.css under :root[data-type]. */

const PAIRINGS = ['a', 'b', 'c', 'today'];
/* Faces the default <link> does not already load. */
const EXTRA_FONTS = { b: 'Yuji+Syuku' };

export function applyType() {
  const type = new URLSearchParams(location.search).get('type');
  if (!PAIRINGS.includes(type) || type === 'a') return;
  document.documentElement.dataset.type = type;
  const family = EXTRA_FONTS[type];
  if (family) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = `https://fonts.googleapis.com/css2?family=${family}&display=swap`;
    document.head.append(link);
  }
}
