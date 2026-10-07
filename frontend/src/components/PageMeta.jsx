import { useEffect } from 'react';

const SITE = 'CyberShield Community';

/** Sets document title + meta description + canonical per page (no library).
 * Googlebot renders JavaScript, so client-side meta is crawlable.
 * Titles stay short and descriptive: "Page | CyberShield Community".
 * Canonical uses the runtime origin, so no production domain is ever
 * hardcoded and staging/dev deployments stay self-consistent. */
export default function PageMeta({ title, description }) {
  useEffect(() => {
    document.title = `${title} | ${SITE}`;
    let tag = document.querySelector('meta[name="description"]');
    if (!tag) {
      tag = document.createElement('meta');
      tag.setAttribute('name', 'description');
      document.head.appendChild(tag);
    }
    tag.setAttribute('content', description);
    let canonical = document.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.setAttribute('rel', 'canonical');
      document.head.appendChild(canonical);
    }
    canonical.setAttribute(
      'href',
      window.location.origin + window.location.pathname,
    );
  }, [title, description]);

  return null;
}
