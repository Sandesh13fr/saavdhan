import { AlertTriangle, ClipboardCheck, OctagonX, Quote } from 'lucide-react';
import type { ReactNode } from 'react';
import { useI18n } from '../lib/i18n';
import type { FieldValue, Lang, Level } from '../lib/types';

export function SyntheticBadge({ label }: { label?: string }) {
  const { t } = useI18n();
  return <span className="badge badge-synthetic">{label ?? t('app.synthetic_badge')}</span>;
}

export function ErrorNote({ message }: { message: string }) {
  return message ? <p className="error-note" role="alert">{message}</p> : null;
}

const LANGS: [Lang, string][] = [['en', 'EN'], ['hi', 'हिं'], ['mr', 'मरा']];
export function LanguageToggle() {
  const { lang, setLang, t } = useI18n();
  return (
    <div className="lang-toggle" role="group" aria-label="Language">
      {LANGS.map(([code, label]) => (
        <button key={code} type="button" lang={code} aria-pressed={lang === code} title={t(`lang.${code}`)} onClick={() => setLang(code)}>{label}</button>
      ))}
    </div>
  );
}

export const LEVEL_ICON = { STOP: OctagonX, VERIFY_FIRST: AlertTriangle, NO_RED_FLAGS_FOUND: ClipboardCheck };

export function VerdictBanner({ level, raDate, children }: { level: Level; raDate: string; children?: ReactNode }) {
  const { t } = useI18n();
  const Icon = LEVEL_ICON[level];
  return (
    <section className={`banner banner-${level}`} aria-labelledby="verdict-h">
      <Icon size={36} aria-hidden="true" />
      <div>
        <h1 id="verdict-h">{t(`verdict.${level}.title`)}</h1>
        <p>{t(`verdict.${level}.body`)}</p>
        <p className="banner-date"><strong>{t('verdict.ra_list_date', { date: raDate })}</strong></p>
        {children}
      </div>
    </section>
  );
}

export function QuoteBlock({ field }: { field: FieldValue }) {
  const { t } = useI18n();
  if (!field.quote) return null;
  return (
    <figure className="quote">
      <Quote size={16} aria-hidden="true" />
      <blockquote lang="und">{field.quote}</blockquote>
      <figcaption>
        {t('verdict.source_label')}: {field.source_ref ?? '—'}
      </figcaption>
    </figure>
  );
}
