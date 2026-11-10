# Final launch checks

## Business details awaiting confirmation

- Replace the provisional public identity “JD Dance” with the correct legal entity details where required; confirm company number/registered address if applicable. The user has confirmed jddance.info and retention only as long as needed.
- Confirm whether Contemporary and Stretch & Conditioning are part of other sessions. Do not imply that every card is separately bookable until confirmed.
- Owner confirmed both Saturday Dance Academy sessions run at the listed times; retain both. Competition teams are invitation only.
- Check publication permission for all children’s photographs/video and the two parent testimonials, including the wording and any desired attribution.
- Owner confirmed all teachers are DBS checked and have safeguarding training. Supply a safeguarding contact/policy for publication; first-aid status and training frequency have not been reconfirmed.
- Owner confirmed comfortable clothing, water, street parking and a parent waiting room. Payments may be weekly or monthly and reserve the child’s place regardless of attendance.
- Studio hire includes space, speakers and lighting. Owner gave a capacity of 20–25 people; confirm whether this applies to one studio or both before publishing a capacity against hire rates.
- Still needed: step-free access information, minimum hire duration and cancellation terms. These facts have not been invented.
- Review the privacy notice against actual handling of enquiries, provider account terms and any international-transfer safeguards. Confirm requests/deletion procedures and who monitors the inbox. Website changes cannot enforce retention in Netlify or Gmail.

## Netlify / domain checks (account access needed)

- Set the project base to the repository root, build with `python3 scripts/build.py && python3 scripts/check_site.py`, publish `public/`. Remove old New/ build settings.
- Confirm Forms detection is enabled, the contact form is detected and notification recipients are correct.
- Submit an authorised test enquiry after deploying, verify it arrives in both Netlify submissions and the intended inbox, verify reply handling, then delete the test data. Local checks deliberately do not send messages.
- Confirm native form validation, spam handling and the thanks redirect on real mobile devices; verify a submission failure does not show a false success.
- Verify HTTPS and the preferred domain, including www redirects, old wedding/hen page redirects and a nested unknown URL returning the custom 404 with HTTP 404 status.
- Confirm CSS/JS/media responses have the configured headers, compression and cache behaviour. CSP allows same-origin form POSTs and self-hosted assets.
- Verify deploy previews are noindex. Submit the production sitemap in Search Console once ready.
- Set up uptime and form-delivery monitoring with a named owner; no monitoring service has been silently subscribed to.
- Keep access to the repository and Netlify account, enable account MFA, and confirm the previous deploy can be restored.

## Verification already automated

`check_site.py`: internal links, fragments, responsive-image files/dimensions, page headings/IDs, form structure, current timetable changes and publish-directory boundaries.

`browser_check.py`: Firefox at 320, 390, 768, 901 and 1440 pixels; navigation, overflow, images, hero colours, focus/scroll restoration, query-string interest selection, client validation, simulated form failure/success, video controls, production security headers, reduced motion and JavaScript-disabled fallbacks. Screenshots/results go to `/tmp/jddance-browser-checks`.

Before public launch, also check Safari/iPhone and Chrome/Android, a keyboard/screen reader, and mobile performance against the deployed host. These checks cannot be inferred from Firefox or static source checks.
