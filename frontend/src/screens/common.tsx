import { Headline, PillLink } from '../components/ui';
import { useI18n } from '../lib/i18n';

export function Loading({ text }: { text?: string }) {
  const { t } = useI18n();
  return (
    <div className="page"><p className="status-note" role="status"><span className="spinner spinner--dark" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: 10 }} />{text ?? t('common.loading')}</p></div>
  );
}

/** Empty state for screens that need a checked offer first. */
export function NeedCase({ title, body }: { title: string; body: string }) {
  const { t } = useI18n();
  return (
    <div className="page">
      <section className="empty" aria-labelledby="empty-h">
        <Headline id="empty-h" size="sm" text={title} />
        <p className="lede lede--muted">{body}</p>
        <div className="actions"><PillLink href="#/check">{t('home.cta')}</PillLink></div>
      </section>
    </div>
  );
}
