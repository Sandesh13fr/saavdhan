// Saavdhan logo: angular S mark (geometric approximation of the board's mark) + wordmark.
export function Mark({ className = 'brand__mark', title }: { className?: string; title?: string }) {
  return (
    <svg className={className} viewBox="0 0 100 120" role={title ? 'img' : undefined} aria-hidden={title ? undefined : true} aria-label={title}>
      <path fill="#C62828" d="M18 8H92L80 30H42V44L82 68V112H8L20 90H58V76L18 52Z" />
      <path fill="#9F1D1D" d="M42 44L82 68L58 76L18 52Z" />
      <path fill="#E04545" d="M18 8H92L86 19H18Z" opacity=".55" />
    </svg>
  );
}

export function Logo({ href = '#/', label }: { href?: string; label: string }) {
  return (
    <a className="brand" href={href} aria-label={label}>
      <Mark />
      <span className="brand__word" aria-hidden="true">SAAVDHAN</span>
    </a>
  );
}
