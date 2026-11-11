# Live Dashboard Hub

Public HTML dashboards at permanent URLs, published with GitHub Actions.

- Hub: https://vismaydataanalytics.github.io/live-dashboard-hub/
- Design Performance: https://vismaydataanalytics.github.io/live-dashboard-hub/dashboards/sample/

This is an independent repository. It has no dependencies on other projects.

## Publish an update
1. Generate and review your approved public HTML output.
2. Replace files in `site/dashboards/<permanent-id>/`. Keep `index.html` as the entry file.
3. Commit the update to `main`. The Publish dashboards workflow validates and deploys the full site.
4. Wait for Actions to succeed, then refresh the existing URL.

To add a dashboard, add its folder and an entry in `dashboards.json`. Never rename an ID after sharing its URL. Local laptop changes are not published until committed and uploaded.

Only reviewed public content belongs here: source and history are public. Do not upload raw company exports, private data, credentials, or private API endpoints. Design Performance is the user-approved public HTML output. The original AI module and proxy configuration are removed from the published copy.

See [laptop publishing instructions](HOW_TO_PUBLISH.md). In the Dashboard_Hub project, use the separate Publishing/live-dashboard-hub folder and double-click Prepare_Public_Update.cmd after regenerating Design_Performance.html. The existing sample URL is retained for continuity.

## Validation and deployment
Run `python scripts/build.py` locally. It validates the registry and local HTML links, then builds `dist/`. Only that folder is published. Standard-library Python is sufficient.

The workflow runs on pushes to main and manual dispatch. Pull requests validate without publishing. Publishing is serialized, and queued commits that are no longer main's head are skipped. Build or upload failures stop before deployment, leaving the current published site in place.

The live build timestamp identifies the build that successfully reached the website; the source-data timestamp is separate. It is not an exact deployment-completion timestamp.

To roll back, revert the faulty content commit on main and allow the publishing workflow to deploy the reverted content. Do not republish a stale workflow run.

## Current scope
Design Performance, a multi-dashboard registry, a generated hub, and GitHub Pages deployment. Filters, charts, images, and reports stay in the self-contained HTML; AI chat is disabled on the public site. Google Fonts are allowed for typography. Hosting provider failure recovery and concurrent-update failure drills have not yet been certified.
