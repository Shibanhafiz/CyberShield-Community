import { Card, Container, PageHeader } from '../components/ui';

export default function About() {
  return (
    <Container narrow>
      <PageHeader
        eyebrow="VTU 1BCP308 · Community project"
        title="About CyberShield Community"
      />
      <div className="mt-4 space-y-4 text-[15px] leading-relaxed text-ink-2">
        <p>
          CyberShield Community is a community cyber-safety platform that helps ordinary
          users understand potentially suspicious SMS messages, WhatsApp messages
          and URLs through explainable, indicative assessments.
        </p>
        <p>
          As a VTU 1BCP308 community project it supports the full arc:
          stakeholder interaction → problem identification → data collection →
          technical implementation → field testing → awareness activities →
          measurable impact → documented evidence. Field-study templates ship
          with the project — no interviews, surveys or impact numbers are
          fabricated; evidence must come from real field activity.
        </p>
        <Card title="What this system is — and is not">
          <p>
            An explainable teaching and reporting tool with privacy-first
            anonymous data collection. Not a guarantee of safety, a verdict of
            guilt, or a measurement of real-world immunity. Scores are
            indicative; URLs are analyzed statically and never visited;
            community data is observations, not verified intelligence.
          </p>
        </Card>
      </div>
    </Container>
  );
}
