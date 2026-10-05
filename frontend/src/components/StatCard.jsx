import { Stat } from './ui';

/** Backwards-compatible wrapper: restrained stat block (no colorful cards). */
export default function StatCard({ label, value }) {
  return <Stat label={label} value={value} />;
}
