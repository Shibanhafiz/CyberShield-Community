// Generates public/sitemap.xml from the route table in src/App.jsx,
// so the sitemap can never go stale when pages change. Runs on `prebuild`.
// Excludes: admin routes, login, dynamic :params, and the * catch-all.
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const appSource = readFileSync(join(root, 'src', 'App.jsx'), 'utf8');

const BASE_URL = process.env.SITEMAP_BASE_URL || 'https://cybershield.example.org';
const EXCLUDED = [/^\/admin/, /\/:[a-zA-Z]+/, /^\*$/];

const paths = new Set();
for (const match of appSource.matchAll(/<Route\s+path="([^"]+)"/g)) {
  const path = match[1];
  // Top-level routes only: nested admin paths are relative ("reports")
  // and the "*" catch-all has no leading slash — both skipped here.
  if (!path.startsWith('/')) continue;
  if (EXCLUDED.some((re) => re.test(path))) continue;
  paths.add(path);
}

const today = new Date().toISOString().slice(0, 10);
const urls = [...paths]
  .sort()
  .map((p) => `  <url>\n    <loc>${BASE_URL}${p}</loc>\n    <lastmod>${today}</lastmod>\n  </url>`)
  .join('\n');

const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`;

writeFileSync(join(root, 'public', 'sitemap.xml'), xml);
console.log(`sitemap.xml: ${paths.size} public URLs (base ${BASE_URL})`);
