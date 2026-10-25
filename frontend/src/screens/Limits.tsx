import { ExternalLink } from 'lucide-react';
import { useEffect, useState } from 'react';
import { ErrorNote } from '../components/small';
import { api } from '../lib/api';
import { useI18n } from '../lib/i18n';
import type { Meta } from '../lib/types';

// Verify before use: numbers change. Shown with the verify_contacts caution.
const HELPLINES: [string, string][] = [
  ['MADAD (MEA)', '1800 11 3090'],
  ['National cyber-crime helpline', '1930'],
  ['Emergency', '112'],
];

export default function Limits() {
  const { t, err } = useI18n();
  const [meta, setMeta] = useState<Meta | null>(null);
  const [error, setError] = useState('');
  useEffect(() => { api<Meta>('/meta').then(setMeta).catch((e) => setError(err(e))); }, [err]);

  return (
    <div className="stack">
      <h1>{t('limits.title')}</h1>
      <section className="card"><h2>{t('limits.what_it_does')}</h2><p>{t('limits.what_it_does_body')}</p></section>
      <section className="card"><h2>{t('limits.what_it_does_not')}</h2><p>{t('limits.what_it_does_not_body')}</p>
        <p><strong>{t('limits.not_legal_advice')}</strong></p>
        <p>{t('limits.no_auto_report')}</p>
      </section>
      <section className="card" aria-labelledby="src-h">
        <h2 id="src-h">{t('limits.sources_title')}</h2>
        <ErrorNote message={error} />
        {meta && (
          <>
            <p className="muted">{t('verdict.ra_list_date', { date: meta.ra_list_date })}</p>
            <ul className="plain">
              {meta.rules.map((r) => (
                <li key={r.id}>
                  <strong>{r.id}</strong> {t(`rule.${r.id}.title`)}{' '}
                  {r.heuristic || !/^https?:\/\//.test(r.source)
                    ? <span className="badge badge-heuristic">{t('verdict.heuristic_badge')}</span>
                    : <a href={r.source} target="_blank" rel="noreferrer noopener">{t('verdict.rule_source')} <ExternalLink size={14} aria-hidden="true" /></a>}
                </li>
              ))}
            </ul>
          </>
        )}
      </section>
      <section className="card">
        <h2>{t('limits.helplines_title')}</h2>
        <ul className="plain">{HELPLINES.map(([n, v]) => <li key={n}>{n}: <strong>{v}</strong></li>)}</ul>
        <p className="muted">{t('limits.verify_contacts')}</p>
      </section>
    </div>
  );
}
