import { Link } from 'react-router-dom';
import { Button, Container, EmptyState } from '../components/ui';

export default function Placeholder({ title = 'Page not found', text = 'This page does not exist.' }) {
  return (
    <Container narrow>
      <EmptyState
        title={title}
        text={text}
        action={(
          <Link to="/">
            <Button variant="secondary">Back to home</Button>
          </Link>
        )}
      />
    </Container>
  );
}
