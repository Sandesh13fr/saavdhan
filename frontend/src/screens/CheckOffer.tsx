import { Upload } from 'lucide-react';
import { useState, type FormEvent } from 'react';
import { ErrorNote } from '../components/small';
import { api } from '../lib/api';
import { useI18n } from '../lib/i18n';
import type { CaseView } from '../lib/types';

const DEMOS = [['bangkok-data-entry', 'check.demo_scam'], ['dubai-near-miss', 'check.demo_near_miss']] as const;

export default function CheckOffer({ onCase }: { onCase: (c: CaseView) => void }) {
  const { t, err } = useI18n();
  const [text, setText] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const run = async (start: () => Promise<CaseView>) => {
    setBusy(true); setError('');
    try {
      const created = await start();
      onCase(await api<CaseView>(`/offers/${created.id}/analyze`, {}));
    } catch (e) { setError(err(e)); } finally { setBusy(false); }
  };
  const submit = (e: FormEvent) => {
    e.preventDefault();
    const fd = new FormData();
    if (text.trim()) fd.append('text', text);
    files.forEach((f) => fd.append('files', f));
    void run(() => api<CaseView>('/offers', fd));
  };
  // Demo endpoints already return a created case; analyze runs next like any other case.
  const demo = (name: string) => run(() => api<CaseView>(`/demo/offers/${name}`, {}));

  return (
    <section aria-labelledby="check-h" className="stack">
      <h1 id="check-h">{t('check.title')}</h1>
      <p>{t('check.intro')}</p>
      <form className="card stack" onSubmit={submit} aria-busy={busy}>
        <label htmlFor="offer-text">{t('check.paste_label')}</label>
        <textarea id="offer-text" rows={8} value={text} placeholder={t('check.paste_placeholder')} onChange={(e) => setText(e.target.value)} />
        <label htmlFor="offer-files" className="file-label"><Upload size={18} aria-hidden="true" /> {t('check.upload_label')}</label>
        <input id="offer-files" type="file" multiple accept=".pdf,.txt,image/*,application/pdf,text/plain"
          onChange={(e) => setFiles(Array.from(e.target.files ?? []).slice(0, 10))} />
        {files.length > 0 && <ul className="plain">{files.map((f) => <li key={f.name + f.size}>{f.name}</li>)}</ul>}
        <button className="btn btn-primary" type="submit" disabled={busy || (!text.trim() && !files.length)}>
          {busy ? t('check.analyzing') : t('check.submit')}
        </button>
        <p className="muted">{t('check.privacy_note')}</p>
      </form>
      <ErrorNote message={error} />
      <div className="card stack">
        <h2>{t('check.demo_title')}</h2>
        <div className="row">
          {DEMOS.map(([name, key]) => (
            <button key={name} className="btn" type="button" disabled={busy} onClick={() => void demo(name)}>{t(key)}</button>
          ))}
        </div>
      </div>
    </section>
  );
}
