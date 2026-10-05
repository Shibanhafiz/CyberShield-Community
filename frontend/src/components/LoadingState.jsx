export default function LoadingState({ label = 'Loading…' }) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-line bg-surface px-4 py-3" role="status" aria-live="polite">
      <span className="h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-brand border-t-transparent" aria-hidden />
      <span className="text-sm text-ink-2">{label}</span>
    </div>
  );
}
