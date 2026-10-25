import { FileText, Search, UsersRound } from 'lucide-react';
import { FamilyLine, OfferDoc } from '../components/Illustrations';
import { Headline, PillLink } from '../components/ui';
import { useI18n } from '../lib/i18n';

export default function Home() {
  const { t } = useI18n();
  const steps = [[FileText, t('home.step_add')], [Search, t('home.step_evidence')], [UsersRound, t('home.step_checkins')]] as const;
  return (
    <div className="page home">
      <section className="split" aria-labelledby="home-h">
        <div className="enter">
          <Headline id="home-h" size="xl" text={t('home.title')} />
          <p className="lede">{t('home.sub')}</p>
          <p className="deva-line" lang="hi">{t('home.hindi_line')}</p>
          <div className="actions"><PillLink href="#/check">{t('home.cta')}</PillLink></div>
        </div>
        <div className="home__art enter-2">
          <OfferDoc title={t('illo.job_offer')} demo={t('ui.demo_data')} fieldLabel={t('illo.visa_type')} fieldValue={t('illo.tourist_visa')} callout={t('illo.tourist_visa')} />
          <svg className="home__dash" viewBox="0 0 120 160" aria-hidden="true"><path d="M4 8 C60 10 100 50 110 150" fill="none" stroke="#111" strokeWidth="2.5" strokeDasharray="7 8" /></svg>
          <FamilyLine className="home__family" />
        </div>
      </section>
      <ol className="steps-strip tile enter-3" aria-label={t('home.steps_label')}>
        {steps.map(([Icon, label], i) => (
          <li key={i}>
            <span className="ico-circle" aria-hidden="true"><Icon size={30} strokeWidth={1.8} /></span>
            <span><span className="sr-only">{i + 1}. </span>{label}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}
