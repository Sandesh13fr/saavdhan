import { Check, FileUp, FileText, MessageSquareText, X } from 'lucide-react';
import { useId, useState, type DragEvent, type FormEvent, type KeyboardEvent } from 'react';
import { OfferDoc } from '../components/Illustrations';
import { DemoMenu, Headline, PillButton, Stepper } from '../components/ui';
import { useI18n } from '../lib/i18n';

const MAX_FILES = 10;
const ACCEPT = '.pdf,.txt,.png,.jpg,.jpeg,.webp,image/*,application/pdf,text/plain';

export default function Submit({ busy, onSubmit, onDemo }: { busy: boolean; onSubmit: (fd: FormData) => Promise<boolean>; onDemo: (name: string) => void }) {
  const { t } = useI18n();
  const [tab, setTab] = useState<'paste' | 'upload'>('paste');
  const [text, setText] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [drag, setDrag] = useState(false);
  const uid = useId();
  const tabs = [['paste', MessageSquareText, t('submit.tab_paste')], ['upload', FileText, t('submit.tab_upload')]] as const;

  const add = (list: FileList | null) => {
    if (!list) return;
    setFiles((cur) => [...cur, ...Array.from(list)].filter((f, i, all) => all.findIndex((g) => g.name === f.name && g.size === f.size) === i).slice(0, MAX_FILES));
  };
  const drop = (e: DragEvent) => { e.preventDefault(); setDrag(false); add(e.dataTransfer.files); };
  const submit = (e: FormEvent) => {
    e.preventDefault();
    const fd = new FormData();
    if (text.trim()) fd.append('text', text);
    files.forEach((f) => fd.append('files', f));
    void onSubmit(fd);
  };
  const tabKey = (e: KeyboardEvent<HTMLButtonElement>) => {
    if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
    const next = tab === 'paste' ? 'upload' : 'paste';
    setTab(next);
    document.getElementById(`${uid}-tab-${next}`)?.focus();
  };
  const ready = !!text.trim() || files.length > 0;

  return (
    <div className="page submit">
      <header className="submit__head enter">
        <Headline size="md" text={t('submit.title')} id="submit-h" />
        <p className="lede lede--muted submit__sub">{t('submit.sub')}</p>
      </header>
      <div className="flow">
        <Stepper step={1} />
        <form className="card submit__card enter-2" onSubmit={submit} aria-labelledby="submit-h" aria-busy={busy}>
          <div className="tabs" role="tablist" aria-label={t('submit.tabs_label')}>
            {tabs.map(([key, Icon, label]) => (
              <button key={key} id={`${uid}-tab-${key}`} type="button" role="tab" aria-selected={tab === key} aria-controls={`${uid}-panel-${key}`}
                tabIndex={tab === key ? 0 : -1} className="tab" onClick={() => setTab(key)} onKeyDown={tabKey}>
                <Icon size={26} strokeWidth={1.7} aria-hidden="true" /> {label}
                {key === 'upload' && files.length > 0 && <span className="tab__count">{files.length}</span>}
                {key === 'paste' && text.trim() && tab !== 'paste' && <span className="tab__count"><Check size={14} strokeWidth={3} aria-hidden="true" /><span className="sr-only">{t('submit.has_text')}</span></span>}
              </button>
            ))}
          </div>

          <div id={`${uid}-panel-paste`} role="tabpanel" aria-labelledby={`${uid}-tab-paste`} hidden={tab !== 'paste'} className="tabpanel">
            <label htmlFor={`${uid}-text`} className="sr-only">{t('check.paste_label')}</label>
            <textarea id={`${uid}-text`} className="textarea" value={text} maxLength={50000} placeholder={t('submit.paste_placeholder')} onChange={(e) => setText(e.target.value)} />
            <p className="small muted">{t('submit.paste_hint')}</p>
          </div>

          <div id={`${uid}-panel-upload`} role="tabpanel" aria-labelledby={`${uid}-tab-upload`} hidden={tab !== 'upload'} className="tabpanel">
            <label className={`dropzone ${drag ? 'is-drag' : ''}`} onDragOver={(e) => { e.preventDefault(); setDrag(true); }} onDragLeave={() => setDrag(false)} onDrop={drop}>
              <input type="file" multiple accept={ACCEPT} className="sr-only" disabled={files.length >= MAX_FILES} onChange={(e) => { add(e.target.files); e.target.value = ''; }} />
              <span className="dropzone__icon" aria-hidden="true"><FileUp size={44} strokeWidth={1.5} /><span className="dropzone__dot" /></span>
              <strong>{t('submit.drop_title')}</strong>
              <span className="muted small">{t('submit.drop_types')}</span>
            </label>
            {files.length > 0 && (
              <ul className="file-list" aria-label={t('submit.files_label')}>
                {files.map((f, i) => (
                  <li key={f.name + f.size}>
                    <FileText size={18} aria-hidden="true" /> <span className="mono">{f.name}</span>
                    <button type="button" className="icon-btn" aria-label={t('submit.remove_file', { name: f.name })} onClick={() => setFiles(files.filter((_, j) => j !== i))}><X size={18} aria-hidden="true" /></button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="submit__foot">
            <DemoMenu onDemo={onDemo} busy={busy} trigger="link" align="left" />
            <PillButton type="submit" tone="red" busy={busy} disabled={busy || !ready}>{busy ? t('check.analyzing') : t('submit.cta')}</PillButton>
          </div>
          <p className="sr-only" role="status" aria-live="polite">{busy ? t('check.analyzing') : ''}</p>
          <p className="small muted submit__privacy">{t('check.privacy_note')}</p>
        </form>
        <div className="submit__art enter-3" aria-hidden="true">
          <OfferDoc title="" demo="" rotate={8} bursts />
        </div>
      </div>
    </div>
  );
}
