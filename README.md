# JD Dance website

The current site is generated from `src/` and `data/`. The former `New/` site and unused Resend endpoint have been removed. Netlify Forms is the only contact-form backend.

## Edit and build

- Page content: `src/pages/*.html`.
- Shared navigation/footer: `src/partials/` and the navigation list in `scripts/build.py`.
- Titles/descriptions: `data/pages.json`.
- Class times/prices: `data/schedule.json` (generates both the HTML timetable and downloadable PDF).
- Styling/behaviour: `style.css`, `site.js`.

Run `python3 scripts/build.py` followed by `python3 scripts/check_site.py`.
The build refreshes the root HTML files for convenient local previews and creates the isolated `public/` directory for deployment. Do not edit generated root HTML directly. Do not publish the repository root.

Preview with `python3 -m http.server --directory public 8000` and open `http://localhost:8000`. Optional browser checks: install Selenium into a temporary virtual environment, then run `python scripts/browser_check.py` using Firefox. These checks use a temporary local server, apply the production security headers and simulate form outcomes without sending enquiries.

## Media

Optimised assets and the media manifest are committed so Netlify only needs Python. Original photos/video are retained as editing sources, but the build only copies referenced assets into `public/`.

To regenerate responsive WebP images and the muted MP4: `python3 scripts/optimize_media.py` (requires ImageMagick and FFmpeg). Review quality after regeneration, then rebuild. Manrope is self-hosted as a subsetted variable WOFF2; its OFL licence is in `assets/fonts/OFL.txt`.

## Netlify

Use repository root as the base directory. `netlify.toml` defines the build command, `public/` publish directory, old-URL redirects, caching and security headers. Remove any old `New/` base-directory override in the Netlify dashboard.

Enable Netlify Forms detection and configure submission notifications for the `contact` form. Keep email delivery and spam review in the Netlify dashboard. No Resend API key or email API function is used by this site.

Production canonical URLs use `https://jddance.info`. Deploy previews and branch deploys get noindex metadata and restrictive robots.txt. The thank-you and 404 pages are always noindex. Hosting-level form handling, HTTPS and actual email delivery need verification on a deployed preview/production site.

See `docs/launch-checklist.md` for remaining business confirmations and hosting checks.
