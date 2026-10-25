// Hash routes: #/<screen>/<caseId or hash>. Old names stay valid for existing links.
export const SCREENS = ['home', 'check', 'review', 'result', 'evidence', 'plan', 'checkin', 'family', 'help', 'login', 'map', 'pattern'] as const;
export type Screen = (typeof SCREENS)[number];
const ALIASES: Record<string, Screen> = { verdict: 'result', safety: 'checkin', limits: 'help' };

export function parseHash(): { screen: Screen; arg: string } {
  const [raw, arg] = location.hash.replace(/^#\/?/, '').split('/');
  const name = ALIASES[raw] ?? raw;
  let decoded = arg ?? '';
  try { decoded = decodeURIComponent(decoded); } catch { /* keep raw */ }
  return { screen: (SCREENS as readonly string[]).includes(name) ? (name as Screen) : 'home', arg: decoded };
}

export const go = (screen: Screen, arg = '') => { location.hash = `#/${screen}${arg ? `/${encodeURIComponent(arg)}` : ''}`; };
