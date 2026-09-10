/**
 * Utility for robust asset URL resolution across environments
 * (local dev, GitHub Pages with repository subpath, PWA offline, etc.)
 */
export function resolveAssetUrl(path: string): string {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('data:')) {
    return path;
  }
  // Strip leading slashes so URL resolves relative to document base URI
  const clean = path.replace(/^\/+/, '');
  try {
    const base = document.baseURI || window.location.href;
    return new URL(clean, base).href;
  } catch {
    return clean;
  }
}
