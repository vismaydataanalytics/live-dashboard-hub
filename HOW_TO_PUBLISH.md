# Publish dashboard updates from this laptop

## Normal use: Run_All.bat

In Dashboard_Hub, update your inputs and double-click Run_All.bat. After the one-time GitHub sign-in, it generates the reports and HTML, removes AI from the public copy, validates, uploads, and verifies the live version automatically. Wait for PUBLISHED SUCCESSFULLY; no browser upload is needed.

Viewers who have loaded the updated dashboard get automatic refreshes when a new release is published. Pages check every 30 seconds and also when a viewer returns to the tab. Older pages opened before automatic refresh was installed need one reload to acquire this feature. Refreshing reloads the page; in-page filter selections can reset.

The steps below describe the optional manual fallback.

## Your working folders

The existing Dashboard_Hub project contains the dashboard generator and raw inputs. The separate `Publishing/live-dashboard-hub` folder is the public publishing repository. Only reviewed HTML output belongs in that repository. Do not upload the entire Dashboard_Hub project.

## Each update

1. Update your usual input files and double-click `Run_All.bat` in the Dashboard_Hub project folder. Check the regenerated `Design_Performance.html` locally.
2. Open `Publishing/live-dashboard-hub` and double-click `Prepare_Public_Update.cmd`. It copies the generated dashboard into the permanent publishing path, removes the AI module and proxy configuration, updates the source timestamp, and validates the site. It does not upload anything. If it reports an error, stop and ask for help; the existing live dashboard stays unchanged.
3. Open the [dashboard folder on GitHub](https://github.com/vismaydataanalytics/live-dashboard-hub/tree/main/site/dashboards/sample). Choose **Add file → Upload files**. Select the prepared file `Publishing/live-dashboard-hub/site/dashboards/sample/index.html`. Keep that exact filename. Commit the replacement directly to `main` with a short message such as “Update Design Performance”. Never upload the original AI-enabled HTML.
4. Open the [repository root](https://github.com/vismaydataanalytics/live-dashboard-hub). Use **Add file → Upload files** to replace `dashboards.json` with the prepared copy from `Publishing/live-dashboard-hub`. This updates the source date shown on the hub. Both commits may start a workflow; the last one publishes the complete current site.
5. Check [Publish dashboards](https://github.com/vismaydataanalytics/live-dashboard-hub/actions/workflows/publish.yml). Wait for the latest run to succeed. Reopen the [same dashboard link](https://vismaydataanalytics.github.io/live-dashboard-hub/dashboards/sample/), or refresh with Ctrl+F5 if it was already open.

The permanent link keeps `sample` in its address for continuity; the visible title is Design Performance. Do not rename this folder to change the title.

## Optional: publish with Git

The browser method uses your existing GitHub browser sign-in and requires no new app or token. If you prefer one commit for both files, first sign into Git using GitHub Desktop or your normal Git setup. No command-line sign-in was configured by this work.

In the `Publishing/live-dashboard-hub` folder, before generating an update, synchronize a clean checkout with `git pull --ff-only`. After preparing the HTML, run:

```powershell
git add -- site/dashboards/sample/index.html dashboards.json
git commit -m "Update Design Performance"
git push origin main
```

If you have used browser uploads, the local Git history will be behind the remote. Pull the new commits before preparing your next update. If Git reports conflicts or local changes, stop and ask for help; do not force-push.

## What stays local

Raw_Input, Raw_Input_SIS, Dashboard_Input, Intermediate_Output, image caches, spreadsheets, Python generation scripts, and AI proxy configuration are not published. The original AI-enabled dashboard remains available locally. Google Fonts are used for typography on the public page.

The source time is the generated HTML file's modification time; it is not a claim about how current every underlying data row is. Publication time identifies the build that reached the website.

The HTML is currently about 23 MB. GitHub browser uploads have a 25 MiB per-file limit. The preparation step stops if that limit is exceeded; use Git or reduce embedded images if the dashboard grows.
