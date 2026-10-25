import { ArrowUpRight, Building2, CreditCard, ExternalLink, FileText, Headset, Info, Landmark, ShieldAlert } from 'lucide-react';
import { useEffect, useState } from 'react';
import type { LucideIcon } from 'lucide-react';
import { HelpDocs } from '../components/Illustrations';
import { AlertChip, ErrorNote, Headline, PillLink } from '../components/ui';
import { api, packetUrl } from '../lib/api';
import { isListDate } from '../lib/caseUtils';
import { useI18n } from '../lib/i18n';
import type { CaseView, Meta } from '../lib/types';

// Official channels named in the brief. Users must verify each on the official site before use.
const PLACES: [string, LucideIcon, string, string][] = [
  ['mea', FileText, 'mailto:helpline@mea.gov.in', 'helpline@mea.gov.in'],
  ['madad', Headset, 'https://madad.gov.in', 'madad.gov.in'],
  ['embassy', Landmark, 'https://www.mea.gov.in', 'mea.gov.in'],
  ['cyber', CreditCard, 'https://cybercrime.gov.in', '1930 · cybercrime.gov.in'],
  ['police', ShieldAlert, 'tel:112', '112'],
  ['emigrate', Building2, 'https://emigrate.gov.in', 'emigrate.gov.in'],
];

export default function Help({ view }: { view: CaseView | null }) {
  const { t, err } = useI18n();
  const [meta, setMeta] = useState<Meta | null>(null);
  const [error, setError] = useState('');
  useEffect(() => { api<Meta>('/meta').then(setMeta).catch((e) => setError(err(e))); }, [err]);
  const canZip = !!view?.analysis;

  return (
    <div className="page help">
      <div className="split split--top">
        <section className="enter" aria-labelledby="help-h">
          <AlertChip icon="info">{t('help.demo_directory')}</AlertChip>
          <Headline id="help-h" size="md" text={t('help.title')} className="help__title" />
          <ul className="help-grid">
            {PLACES.map(([key, Icon, href, shown]) => {
              const ext = href.startsWith('http');
              return (
                <li key={key} className={`help-card tile ${key === 'police' ? 'help-card--wide' : ''}`}>
                  <a href={href} {...(ext ? { target: '_blank', rel: 'noreferrer noopener' } : {})}>
                    <span className="ico-circle ico-circle--red help-card__ico" aria-hidden="true"><Icon size={30} strokeWidth={1.7} color="#C62828" /></span>
                    <span className="help-card__text">
                      <strong>{t(`help.${key}.name`)}</strong>
                      <span className="muted">{t(`help.${key}.what`)}</span>
                      <span className="mono help-card__addr">{shown}</span>
                      <span className="help-card__verify">{t('help.verify')}</span>
                    </span>
                    <span className="help-card__go" aria-hidden="true"><ArrowUpRight size={22} /></span>
                    {ext && <span className="sr-only"> ({t('ui.new_tab')})</span>}
                  </a>
                </li>
              );
            })}
          </ul>
        </section>
        <aside className="help__side enter-2" aria-label={t('help.report_zip')}>
          <div className="help__art" aria-hidden="true"><HelpDocs /></div>
          {canZip
            ? <PillLink href={packetUrl(view!.id)} download wide>{t('help.report_zip')}</PillLink>
            : <PillLink href="#/check" wide>{t('home.cta')}</PillLink>}
          <p className="small muted" style={{ marginTop: 12 }}>{canZip ? t('help.zip_note') : t('help.zip_none')}</p>
        </aside>
      </div>

      <section className="limits" aria-labelledby="limits-h">
        <h2 id="limits-h" className="section-title">{t('limits.title')}</h2>
        <ul className="limits__list">
          <li className="tile"><strong>{t('help.limit_legal')}</strong><span className="muted">{t('limits.not_legal_advice')}</span></li>
          <li className="tile"><strong>{t('help.limit_report')}</strong><span className="muted">{t('limits.no_auto_report')}</span></li>
          <li className="tile"><strong>{t('help.limit_demo')}</strong><span className="muted">{t('limits.what_it_does')}</span></li>
          <li className="tile"><strong>{t('help.limit_wrong')}</strong><span className="muted">{t('limits.what_it_does_not')}</span></li>
        </ul>
        <details className="sources">
          <summary>{t('limits.sources_title')}</summary>
          <ErrorNote message={error} />
          {meta && (
            <>
              <p className="ra-line" style={{ margin: '12px 0' }}>{isListDate(meta.ra_list_date) ? t('verdict.ra_list_date', { date: meta.ra_list_date }) : t('verdict.ra_not_checked')}</p>
              <ul className="sources__list">
                {meta.rules.map((r) => (
                  <li key={r.id}>
                    <code>{r.id}</code> <span>{t(`rule.${r.id}.title`)}</span>{' '}
                    {r.heuristic || !/^https?:\/\//.test(r.source)
                      ? <span className="badge badge--heur">{t('verdict.heuristic_badge')}</span>
                      : <a className="src-link" href={r.source} target="_blank" rel="noreferrer noopener">{t('verdict.rule_source')} <ExternalLink size={14} aria-hidden="true" /></a>}
                  </li>
                ))}
              </ul>
            </>
          )}
        </details>
      </section>
      <p className="help__foot"><Info size={22} aria-hidden="true" /> {t('limits.verify_contacts')}</p>
    </div>
  );
}
