import { Badge } from './ui';

/** Risk level is always text + tinted badge, never color alone.
 * The numeric score is secondary metadata, not the headline. */
export default function RiskBadge({ level, score }) {
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1" role="status" aria-label={`Risk level ${level}`}>
      <Badge tone={level === 'HIGH' ? 'red' : level === 'LOW' ? 'green' : 'amber'}>
        {level === 'HIGH' ? 'High risk' : level === 'LOW' ? 'Low risk' : 'Medium risk'}
      </Badge>
      {typeof score === 'number' && (
        <span className="text-[13px] text-muted">Score {score}/100 · engineering heuristic</span>
      )}
    </div>
  );
}
