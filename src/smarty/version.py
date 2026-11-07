APP_NAME = "Smarty"
APP_VERSION = "0.1.0"
CONTENT_VERSION = "2026-11-07.1"

# Content tiles, keyed by their exact category label text (matches how
# records reference a category in the real seed: Idea/PerformanceRecord
# .categories holds label strings, not a slug).
CATEGORIES_ORDER = [
    "Weekly bots performance",
    "Growth and enrolment",
    "New audiences and channels",
    "Parent engagement and retention",
    "Teaching–Professor ideas",
    "Learning Dragon ideas",
    "Miscellaneous",
]

# Status views are a separate concept (filtered by UserState.status, not by
# a record's categories), so these stay internal slugs.
STATUS_VIEWS_ORDER = [
    "rudys_collection",
    "park_it_for_later",
    "rejected_recoverable",
]
