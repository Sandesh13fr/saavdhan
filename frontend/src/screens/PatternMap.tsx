import { ChevronDown, ChevronRight, FileText, Hash, LogOut, MapPin, Map as MapIcon } from 'lucide-react';
import { useEffect, useState } from 'react';
import { ErrorNote, Headline, PillLink } from '../components/ui';
import { PatternMap as MapView, type MapData } from '../features/map';
import { api, setCsrf } from '../lib/api';
import { useI18n } from '../lib/i18n';
import { go } from '../lib/route';
import { Loading } from './common';

export const shortHash = (h: string) => `${h.slice(0, 4)}…${h.slice(-4)}`;

export function useMapData(authed: boolean) {
  const { err } = useI18n();
  const [data, setData] = useState<MapData | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    if (!authed) return;
    api<MapData>('/reports/map').then((d) => { setData(d); setError(''); }).catch((e) => setError(err(e)));
  }, [authed, err]);
  return { data, error };
}

export default function PatternMapScreen({ authed, onSignedOut }: { authed: boolean | null; onSignedOut: () => void }) {
  const { t } = useI18n();
  const { data, error } = useMapData(!!authed);
  const [district, setDistrict] = useState('');
  useEffect(() => { if (authed === false) go('login'); }, [authed]);
  if (!authed) return <Loading text={t('map.login_required')} />;
  if (!data) return error ? <div className="page"><ErrorNote message={error} /></div> : <Loading />;

  const byCount = [...data.districts].sort((a, b) => b.count - a.count);
  const reports = data.districts.reduce((n, d) => n + d.count, 0);
  const active = data.districts.filter((d) => d.count > 0).length;
  const hashes = data.repeated_agents.length + data.repeated_templates.length;
  const top = byCount.slice(0, 3).map((d) => d.district);
  const highlight = district ? [district] : top;
  const firstHash = data.repeated_agents[0]?.agent_phone_hash ?? data.repeated_templates[0]?.offer_template_hash;
  const logout = async () => {
    try { await api('/auth/logout', {}); } catch { /* ignore */ }
    setCsrf(''); onSignedOut(); go('login');
  };
  const stats = [
    [FileText, reports, t('map.reports')],
    [MapPin, active, t('map.districts')],
    [Hash, hashes, t('pmap.repeated_hashes')],
  ] as const;

  return (
    <div className="page pmap">
      <div className="pmap__head">
        <Headline size="md" text={t('pmap.title')} id="pmap-h" />
        <span className="chip chip--plain">{t('pmap.synthetic')}</span>
        <label className="pmap__filter tile">
          <MapIcon size={24} strokeWidth={1.7} aria-hidden="true" />
          <span className="sr-only">{t('pmap.filter_label')}</span>
          <select value={district} onChange={(e) => setDistrict(e.target.value)}>
            <option value="">{t('pmap.all_districts')}</option>
            {byCount.map((d) => <option key={d.district} value={d.district}>{d.district} ({d.count})</option>)}
          </select>
          <ChevronDown size={22} aria-hidden="true" />
        </label>
      </div>
      <div className="pmap__grid">
        <div className="pmap__map tile">
          <MapView data={data} basemap={false} variant="canvas" highlight={highlight}
            labels={{ title: t('pmap.title'), syntheticData: t('map.synthetic_badge'), reports: t('map.reports'), repeatedAgents: t('map.repeated_agents'), repeatedTemplates: t('map.repeated_templates') }} />
          <span className="pmap__illustrative">{t('pmap.illustrative')}</span>
        </div>
        <ul className="pmap__stats">
          {stats.map(([Icon, n, label]) => (
            <li key={label} className="stat tile">
              <span className="ico-circle ico-circle--red" aria-hidden="true"><Icon size={30} strokeWidth={1.6} /></span>
              <span className="stat__num"><strong className="tnum">{n}</strong><span className="chip chip--sm">{t('pmap.demo')}</span></span>
              <span className="stat__label">{label}</span>
            </li>
          ))}
        </ul>
      </div>
      <div className="pmap__bar tile">
        <ul className="pmap__chips" aria-label={t('pmap.chips_label')}>
          {highlight.map((d) => (
            <li key={d}><button type="button" className="dchip" aria-pressed={district === d} onClick={() => setDistrict(district === d ? '' : d)}><span className="red-dot" aria-hidden="true" />{d}</button></li>
          ))}
        </ul>
        {firstHash && <PillLink tone="red" href={`#/pattern/${firstHash}`}>{t('pmap.explore')}</PillLink>}
      </div>

      <section className="pmap__patterns" aria-labelledby="pat-h">
        <h2 id="pat-h" className="section-title">{t('map.repeated_agents')}</h2>
        <p className="small muted">{t('pmap.hash_note')}</p>
        <ul className="rows">
          {data.repeated_agents.map((a) => (
            <li key={a.agent_phone_hash}><a className="row row__head" href={`#/pattern/${a.agent_phone_hash}`}>
              <span className="row__icon" aria-hidden="true"><Hash size={22} /></span>
              <span className="row__title"><strong className="mono">{shortHash(a.agent_phone_hash)}</strong><span>{t('pmap.row', { count: a.count, n: a.districts.length })} · {a.districts.join(', ')}</span></span>
              <ChevronRight className="row__chev" size={22} aria-hidden="true" />
            </a></li>
          ))}
        </ul>
        <h2 className="section-title" style={{ marginTop: 28 }}>{t('map.repeated_templates')}</h2>
        <ul className="rows">
          {data.repeated_templates.map((a) => (
            <li key={a.offer_template_hash}><a className="row row__head" href={`#/pattern/${a.offer_template_hash}`}>
              <span className="row__icon" aria-hidden="true"><FileText size={22} /></span>
              <span className="row__title"><strong className="mono">{shortHash(a.offer_template_hash)}</strong><span>{t('pmap.row', { count: a.count, n: a.districts.length })} · {a.districts.join(', ')}</span></span>
              <ChevronRight className="row__chev" size={22} aria-hidden="true" />
            </a></li>
          ))}
        </ul>
        <button type="button" className="ghost-btn ghost-btn--sm" style={{ marginTop: 24 }} onClick={() => void logout()}><LogOut size={18} aria-hidden="true" /> {t('map.sign_out')}</button>
      </section>
    </div>
  );
}
