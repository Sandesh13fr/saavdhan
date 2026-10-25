import { ChevronDown, ChevronRight, Link2 } from 'lucide-react';
import { useState } from 'react';
import { OfferDoc } from '../components/Illustrations';
import { DemoChip, Headline, PillLink, Stepper } from '../components/ui';
import { RULE_FACT, offerFacts, type Fact } from '../lib/caseUtils';
import { useI18n } from '../lib/i18n';
import type { CaseView } from '../lib/types';
import { Loading } from './common';

export default function Review({ view }: { view: CaseView | null }) {
  const { t } = useI18n();
  const [open, setOpen] = useState<string | null>(null);
  const [more, setMore] = useState(false);
  if (!view) return <Loading />;
  const a = view.analysis;
  if (!a) return <Loading text={t('review.not_analyzed')} />;
  const { primary, more: rest } = offerFacts(a.offer, t);
  // A fact is flagged when the rule about it is a critical hit (mock 03 highlights one tile, not all).
  const flaggedKeys = new Set(a.verdict.rule_hits.filter((h) => h.status === 'hit' && h.severity === 'critical').map((h) => RULE_FACT[h.rule_id]));
  const flagged = (f: Fact) => f.value != null && flaggedKeys.has(f.key);
  const lead = primary.find((f) => flagged(f) && f.value) ?? primary.find((f) => f.value);
  const restFound = rest.filter((f) => f.value);

  const tile = (f: Fact) => {
    const Icon = f.icon;
    const isOpen = open === f.key;
    const missing = f.value == null;
    const bodyId = `fact-${f.key}`;
    return (
      <li key={f.key} className={`fact ${flagged(f) ? 'is-flagged' : ''} ${missing ? 'is-missing' : ''}`}>
        <button type="button" className="fact__head" aria-expanded={isOpen} aria-controls={bodyId} onClick={() => setOpen(isOpen ? null : f.key)}>
          <span className="ico-circle" aria-hidden="true"><Icon size={26} strokeWidth={1.7} /></span>
          <span className="fact__text">
            <span className="fact__label">{t(`fact.${f.key}`)}</span>
            {missing
              ? <strong className="fact__value fact__value--missing"><span className="miss-dot" aria-hidden="true" />{t('verdict.not_found')}</strong>
              : <strong className="fact__value">{f.value}</strong>}
            {flagged(f) && <span className="sr-only">{t('review.flagged')}</span>}
          </span>
          <ChevronRight className="fact__chev" size={22} aria-hidden="true" />
        </button>
        <div id={bodyId} className="fact__body" hidden={!isOpen}>
          {f.field?.quote ? (
            <figure className="quote">
              <figcaption className="fact__quote-label"><Link2 size={15} aria-hidden="true" /> {t('review.source_quote')}</figcaption>
              <blockquote lang="und">{f.field.quote}</blockquote>
              <figcaption>{t('verdict.source_label')}: {f.field.source_ref ?? '—'}</figcaption>
            </figure>
          ) : <p className="small muted">{t('review.no_quote')}</p>}
        </div>
      </li>
    );
  };

  return (
    <div className="page review">
      <div className="flow flow--review">
        <Stepper step={2} />
        <section className="enter" aria-labelledby="review-h">
          {view.demo && <div className="chip-row" style={{ marginBottom: 18 }}><DemoChip /></div>}
          <Headline id="review-h" size="md" text={t('review.title')} />
          <p className="lede">{t('review.sub')}</p>
          <ul className="facts">{primary.map(tile)}</ul>
          {restFound.length > 0 && (
            <>
              <button type="button" className="group-toggle" aria-expanded={more} aria-controls="facts-more" onClick={() => setMore(!more)} style={{ marginTop: 14 }}>
                {t('review.more', { count: restFound.length })}
                <ChevronDown className="row__chev" size={22} aria-hidden="true" />
              </button>
              <ul className="facts" id="facts-more" hidden={!more}>{restFound.map(tile)}</ul>
            </>
          )}
          <p className="small muted" style={{ marginTop: 16 }}>{t(`verdict.method.${a.extraction_method}`)}</p>
          {a.errors.length > 0 && <ul className="small muted">{a.errors.map((e, i) => <li key={i}>{e}</li>)}</ul>}
          <div className="actions">
            <PillLink href={`#/result/${view.id}`}>{t('review.cta')}</PillLink>
            <span className="vsep" aria-hidden="true" />
            <a className="link-btn" href="#/check">{t('review.edit')}</a>
          </div>
        </section>
        <div className="review__art enter-2" aria-hidden="true">
          <OfferDoc title={t('illo.job_offer')} demo={view.demo ? t('ui.demo_data') : ''} fieldLabel={lead ? t(`fact.${lead.key}`).toUpperCase() : ''} fieldValue={lead?.value ?? undefined} rotate={4} />
        </div>
      </div>
    </div>
  );
}
