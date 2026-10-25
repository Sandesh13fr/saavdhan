import { Copy, FileText, Flag, FolderOpen, Info } from 'lucide-react';
import { useEffect, useState } from 'react';
import { HashGraph } from '../components/Illustrations';
import { Disclosure, ErrorNote, Headline, PillLink } from '../components/ui';
import { useI18n } from '../lib/i18n';
import { go } from '../lib/route';
import { Loading } from './common';
import { shortHash, useMapData } from './PatternMap';

export default function PatternDetail({ authed, hash }: { authed: boolean | null; hash: string }) {
  const { t } = useI18n();
  const { data, error } = useMapData(!!authed);
  const [copied, setCopied] = useState(false);
  useEffect(() => { if (authed === false) go('login'); }, [authed]);
  if (!authed) return <Loading text={t('map.login_required')} />;
  if (!data) return error ? <div className="page"><ErrorNote message={error} /></div> : <Loading />;

  const agent = data.repeated_agents.find((a) => a.agent_phone_hash === hash);
  const tpl = data.repeated_templates.find((a) => a.offer_template_hash === hash);
  const item = agent ?? tpl;
  if (!item) return <div className="page"><ErrorNote message={t('pdetail.not_found')} /><p style={{ marginTop: 16 }}><a href="#/map">{t('pdetail.back')}</a></p></div>;
  const counts = new Map(data.districts.map((d) => [d.district, d.count]));
  const copy = async () => { try { await navigator.clipboard.writeText(hash); setCopied(true); setTimeout(() => setCopied(false), 1800); } catch { /* clipboard blocked */ } };
  const n = item.districts.length;

  return (
    <div className="page pdetail">
      <div className="split split--top">
        <section className="enter" aria-labelledby="pd-h">
          <Headline id="pd-h" size="md" text={agent ? t('pdetail.title_agent', { n }) : t('pdetail.title_template', { n })} />
          <p className="pdetail__meta muted">
            <span>{t('pmap.synthetic')}</span><span aria-hidden="true">•</span>
            <span className="mono">{t('pdetail.hash')} {shortHash(hash)}</span>
            <button type="button" className="icon-btn" onClick={() => void copy()} aria-label={t('pdetail.copy')}><Copy size={20} aria-hidden="true" /></button>
            <span role="status" className="small">{copied ? t('pdetail.copied') : ''}</span>
          </p>
          <div className="pdetail__graph">
            <HashGraph center={shortHash(hash)} nodes={item.districts} label={t('pdetail.graph_label', { hash: shortHash(hash), districts: item.districts.join(', ') })} />
          </div>
        </section>
        <aside className="pdetail__side enter-2" aria-label={t('pdetail.side_label')}>
          <div className="rows">
            <Disclosure defaultOpen icon={<span className="ico-circle ico-circle--red ico-circle--sm" aria-hidden="true"><FileText size={22} color="#C62828" /></span>} title={t('pdetail.reports', { count: item.count })}>
              <p>{t('pdetail.reports_body', { count: item.count, n })}</p>
            </Disclosure>
            <Disclosure icon={<span className="ico-circle ico-circle--red ico-circle--sm" aria-hidden="true"><Flag size={22} color="#C62828" /></span>} title={t('pdetail.districts', { n })}>
              <ul className="dlist">{item.districts.map((d) => <li key={d}><span>{d}</span><span className="mono muted">{counts.get(d) != null ? t('pdetail.district_total', { count: counts.get(d)! }) : '—'}</span></li>)}</ul>
            </Disclosure>
            <Disclosure icon={<span className="ico-circle ico-circle--red ico-circle--sm" aria-hidden="true"><FolderOpen size={22} color="#C62828" /></span>} title={t('pdetail.full_hash')}>
              <code className="pdetail__hash">{hash}</code>
              <p className="small muted">{t('pdetail.hash_explain')}</p>
            </Disclosure>
          </div>
          <div className="actions"><PillLink href="#/map" wide>{t('pdetail.back')}</PillLink></div>
        </aside>
      </div>
      <p className="help__foot"><Info size={22} aria-hidden="true" /> {t('pmap.hash_note')}</p>
    </div>
  );
}
