# Seed files go here

Drop the real `ideas.json`, `weekly-performance.json`, and `categories.json`
into `C:\TowerHill\Grok-Bot-data\business-ideas\catalog\seed\` on the laptop
that runs Smarty (not this source folder) — that's where
`smarty.seed.load_seed_from_dir` looks on first launch with no cache.

This folder in the source tree is just a placeholder/reminder; nothing here
is read by the app at runtime.

Smarty will never invent the content of these files. Until they're
provided, the app runs with an empty catalog and says so plainly.
