# Smarty — what's needed to go from "working shell" to "fully functional"

## Context (for whoever/whatever reads this)

Smarty is a local Windows desktop app for reviewing Tower Hill business
ideas and weekly bot-performance records. The application itself was
built and tested at `C:\TowerHill\Smarty` (Python 3.14 + PySide6 6.12):
catalog/journal/sync/import/updater core, a three-pane UI, 54 passing
tests, and a real `Smarty.exe` built with PyInstaller and installed with a
desktop shortcut.

**It runs, but it's empty.** The original brief for this app referenced a
production seed catalog — 59 business ideas, 10 weekly performance
records, 10 categories — meant to arrive as `ideas.json`,
`weekly-performance.json`, `categories.json`, bundled in a
`Smarty_Claude_Handoff.zip` (plus optionally `Smarty_source_optional.zip`
containing an earlier Linux/PySide6 build of the same app). Neither zip,
nor any of those JSON files, nor that earlier source, exist anywhere on
the machine Smarty was built on. Nothing was invented to fill the gap —
the brief was explicit that inventing ideas, scores, dates, or URLs is not
allowed — so the catalog is just honestly empty right now.

Full behavioral spec, data rules, sync rules, and what was and wasn't
tested: see `C:\TowerHill\Smarty\README.md` in the same project.

## Questions that need real answers (not invented ones) before this is "fully functional"

1. **Where is the actual seed content?** The 59 ideas / 10 performance
   records / 10 categories, or the `Smarty_Claude_Handoff.zip` /
   `Smarty_source_optional.zip` files. If this workspace has them, export
   them as plain JSON/zip so they can be copied to
   `C:\TowerHill\Grok-Bot-data\business-ideas\catalog\seed\` on the laptop
   running Smarty.

2. **Does an earlier Linux/PySide6 build of this app actually exist** (the
   one described as `python -m sparky`, package name `sparky`, with
   57 passing pytest tests, journal-based sync, an updater, etc.), or was
   that description aspirational/historical only? If it exists, where, and
   should Smarty's fresh Windows build be replaced by it, or left as-is?

3. **What is the real, verified path to the shared data folder** on Rudy's
   and Lumi's actual laptops? The brief named `T:\TowerHill\Sparky\` as a
   legacy/documented name and `\\192.168.2.100\Arhiva\TowerHill\Sparky` as
   an unverified possible UNC. Neither has been confirmed from the machine
   Smarty was built on. Can someone confirm the exact mapping on each real
   laptop?

4. **What device labels should identify each laptop** in the sync journal
   (e.g. `"Rudy-Laptop"`, `"Lumi-Laptop"`) — currently it falls back to
   the Windows hostname if `SPARKY_DEVICE_LABEL` isn't set.

5. **For the 5 ideas with no exact source URL** (drifting students,
   attendance counts, parent clips, student reflection videos, internal
   family-name preflight) — is there real `missing_source_note` wording
   to use per idea, or is a generic "no source URL on file" acceptable?

6. **Is CLI/manual import acceptable for now**, or is an in-app "Import a
   batch file" button/dialog needed before this counts as done? (The
   import logic itself is built and tested; only the UI control to trigger
   it from inside the app is not wired in yet.)

7. **Should the catalog-manifest auto-refresh** (separate from the
   notes/status sync, for pulling in new seed batches automatically from
   the share) be wired into app startup now, or is that a deliberate v2
   step?

8. **Is a zip + PowerShell install script enough**, or is a real MSI/
   installer wizard expected before this is "fully functional" for
   non-technical daily use?

9. **Who actually copies a release zip + `latest.json` to
   `T:\TowerHill\Sparky\Installers\`** once the share mapping is confirmed
   — should that stay a manual, deliberate step by Rudy/Lumi, or is there
   a reason to automate it later?

10. **Any category, caution flag, or status rule not already covered** by
    the 7 content tiles (Weekly bots performance, Growth and enrolment,
    New audiences and channels, Parent engagement and retention,
    Teaching–Professor ideas, Learning Dragon ideas, Miscellaneous) and the
    3 status views (Rudy's collection, Park it for later, Rejected)?
