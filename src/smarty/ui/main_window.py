"""Smarty's three-pane main window: category tiles (left), chronological
list for the selected tile (right), and the selected record's detail in the
center (summary/advice on top ~2/3, status + notes on bottom ~1/3).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from smarty.importer import ImportRejected, import_file
from smarty.models import STATUSES
from smarty.paths import save_device_label
from smarty.seed import Catalog
from smarty.store import Store
from smarty.sync import SyncConfig, sync_notes_journal
from smarty.ui.view_model import (
    STATUS_VIEW_LABELS,
    STATUS_VIEW_TO_STATUS,
    filter_rows,
    rows_for_category,
    rows_for_status_view,
    sort_rows,
)
from smarty.version import APP_NAME, CATEGORIES_ORDER, STATUS_VIEWS_ORDER

AUTOSAVE_DEBOUNCE_MS = 600
REJECT_CONFIRM_WINDOW_MS = 4000


class MainWindow(QMainWindow):
    def __init__(self, store: Store, paths, sync_config: SyncConfig | None = None):
        super().__init__()
        self.store = store
        self.paths = paths
        self.sync_config = sync_config or SyncConfig()
        self.setWindowTitle(APP_NAME)

        self._current_content_id: str | None = None
        self._reject_armed = False
        self._last_content_check = "never"
        self._last_notes_sync = "never"

        self._notes_timer = QTimer(self)
        self._notes_timer.setSingleShot(True)
        self._notes_timer.timeout.connect(self._flush_notes)

        self._steps_timer = QTimer(self)
        self._steps_timer.setSingleShot(True)
        self._steps_timer.timeout.connect(self._flush_practical_steps)

        self._build_ui()
        self._populate_tiles()
        self._refresh_sync_label()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        root.addWidget(self._build_top_bar())

        splitter = QSplitter(Qt.Horizontal, central)
        root.addWidget(splitter, 1)

        # Spatial layout is deliberately NOT the conventional left-list /
        # right-detail split: Left = category tiles, Center = the selected
        # record's detail, Right = the chronological list for that tile.
        # Do not swap center and right.
        self.tile_list = QListWidget()
        self.tile_list.setMinimumWidth(180)
        self.tile_list.currentItemChanged.connect(self._on_tile_changed)
        splitter.addWidget(self.tile_list)

        splitter.addWidget(self._build_detail_pane())

        self.record_list = QListWidget()
        self.record_list.setMinimumWidth(220)
        self.record_list.currentItemChanged.connect(self._on_record_changed)
        splitter.addWidget(self.record_list)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 2)
        self._main_splitter = splitter

    def _build_top_bar(self) -> QWidget:
        bar = QWidget()
        layout = QHBoxLayout(bar)
        self.privacy_label = QLabel(
            "Kept is not approval. Filing an idea here does not start outreach, "
            "a development change, or spending."
        )
        self.privacy_label.setWordWrap(True)
        layout.addWidget(self.privacy_label, 2)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search title, id, summary, bot, notes...")
        self.search_box.textChanged.connect(self._refresh_record_list)
        layout.addWidget(self.search_box, 2)

        self.bot_filter = QComboBox()
        self.bot_filter.addItem("All bots", None)
        self.bot_filter.currentIndexChanged.connect(self._refresh_record_list)
        layout.addWidget(self.bot_filter)

        self.status_filter = QComboBox()
        self.status_filter.addItem("All statuses", None)
        for s in STATUSES:
            self.status_filter.addItem(s, s)
        self.status_filter.currentIndexChanged.connect(self._refresh_record_list)
        layout.addWidget(self.status_filter)

        self.sort_toggle = QComboBox()
        self.sort_toggle.addItem("Newest received first", True)
        self.sort_toggle.addItem("Oldest received first", False)
        self.sort_toggle.currentIndexChanged.connect(self._refresh_record_list)
        layout.addWidget(self.sort_toggle)

        self.sync_label = QLabel("")
        layout.addWidget(self.sync_label, 1)

        self.sync_button = QPushButton("Sync now")
        self.sync_button.clicked.connect(self.run_sync)
        layout.addWidget(self.sync_button)

        self.import_button = QPushButton("Import batch...")
        self.import_button.clicked.connect(self._on_import_batch)
        layout.addWidget(self.import_button)

        self.device_label_button = QPushButton()
        self.device_label_button.clicked.connect(self._on_set_device_label)
        layout.addWidget(self.device_label_button)
        self._refresh_device_label_button()

        self.cloud_sync_button = QPushButton("Sync to cloud")
        self.cloud_sync_button.clicked.connect(self.run_cloud_sync)
        self.cloud_sync_button.setVisible(bool(self.paths.cloud_sync_url))
        layout.addWidget(self.cloud_sync_button)

        return bar

    def _build_detail_pane(self) -> QWidget:
        splitter = QSplitter(Qt.Vertical)

        top = QWidget()
        top_layout = QVBoxLayout(top)
        self.title_label = QLabel("")
        self.title_label.setWordWrap(True)
        self.meta_label = QLabel("")
        self.meta_label.setWordWrap(True)
        self.summary_browser = QTextBrowser()
        top_layout.addWidget(self.title_label)
        top_layout.addWidget(self.meta_label)
        top_layout.addWidget(self.summary_browser, 1)

        bottom = QWidget()
        bottom_layout = QVBoxLayout(bottom)

        status_row = QHBoxLayout()
        self.status_buttons: dict[str, QPushButton] = {}
        for status in STATUSES:
            btn = QPushButton(status)
            btn.clicked.connect(lambda checked=False, s=status: self._on_status_clicked(s))
            status_row.addWidget(btn)
            self.status_buttons[status] = btn
        self.reject_button = self.status_buttons["rejected"]
        bottom_layout.addLayout(status_row)

        self.status_label = QLabel("")
        bottom_layout.addWidget(self.status_label)

        bottom_layout.addWidget(QLabel("Notes (yours, autosaved):"))
        self.notes_edit = QTextEdit()
        self.notes_edit.textChanged.connect(self._schedule_notes_save)
        bottom_layout.addWidget(self.notes_edit)

        bottom_layout.addWidget(QLabel("Practical steps (editable bot draft, autosaved):"))
        self.practical_steps_edit = QTextEdit()
        self.practical_steps_edit.textChanged.connect(self._schedule_steps_save)
        bottom_layout.addWidget(self.practical_steps_edit)

        splitter.addWidget(top)
        splitter.addWidget(bottom)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        return splitter

    # ------------------------------------------------------------- tiles

    def _populate_tiles(self) -> None:
        self.tile_list.clear()
        for label in CATEGORIES_ORDER:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, ("category", label))
            self.tile_list.addItem(item)
        for key in STATUS_VIEWS_ORDER:
            item = QListWidgetItem(STATUS_VIEW_LABELS[key])
            item.setData(Qt.UserRole, ("status_view", key))
            self.tile_list.addItem(item)

        while self.bot_filter.count() > 1:
            self.bot_filter.removeItem(1)
        bots = sorted(
            {
                idea.originating_bots[0]
                for idea in self.store.catalog.ideas
                if idea.originating_bots
            }
            | {rec.bot for rec in self.store.catalog.performance_records}
        )
        for bot in bots:
            self.bot_filter.addItem(bot, bot)

        if self.tile_list.count():
            self.tile_list.setCurrentRow(0)

    # --------------------------------------------------------- selection

    def current_rows(self) -> list:
        current = self.tile_list.currentItem()
        if current is None:
            return []
        kind, key = current.data(Qt.UserRole)
        catalog: Catalog = self.store.catalog
        if kind == "category":
            rows = rows_for_category(catalog, self.store, key)
        else:
            rows = rows_for_status_view(catalog, self.store, key)
        rows = filter_rows(
            rows,
            search=self.search_box.text(),
            bot=self.bot_filter.currentData(),
            status=self.status_filter.currentData(),
            store=self.store,
        )
        newest_first = self.sort_toggle.currentData()
        return sort_rows(rows, newest_first=newest_first)

    def _on_tile_changed(self, *_args) -> None:
        self._refresh_record_list()

    def _refresh_record_list(self, *_args) -> None:
        self._flush_pending_edits()
        self.record_list.blockSignals(True)
        self.record_list.clear()
        for row in self.current_rows():
            label = f"{row.title}  [{row.status}]"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, row.content_id)
            self.record_list.addItem(item)
        self.record_list.blockSignals(False)
        if self.record_list.count():
            self.record_list.setCurrentRow(0)
        else:
            self._show_record(None)

    def _on_record_changed(self, *_args) -> None:
        self._flush_pending_edits()
        current = self.record_list.currentItem()
        content_id = current.data(Qt.UserRole) if current else None
        self._show_record(content_id)

    # ------------------------------------------------------------ detail

    def _find_record(self, content_id: str):
        for idea in self.store.catalog.ideas:
            if idea.id == content_id:
                return "idea", idea
        for rec in self.store.catalog.performance_records:
            if rec.id == content_id:
                return "performance", rec
        return None, None

    def _show_record(self, content_id: str | None) -> None:
        self._current_content_id = content_id
        self._reject_armed = False
        self._update_reject_button_label()

        if content_id is None:
            self.title_label.setText("")
            self.meta_label.setText("")
            self.summary_browser.setHtml("")
            self.notes_edit.blockSignals(True)
            self.practical_steps_edit.blockSignals(True)
            self.notes_edit.clear()
            self.practical_steps_edit.clear()
            self.notes_edit.blockSignals(False)
            self.practical_steps_edit.blockSignals(False)
            self.status_label.setText("")
            return

        kind, record = self._find_record(content_id)
        us = self.store.user_state(content_id)

        if kind == "idea":
            self.title_label.setText(f"{record.title}  (id: {record.id})")
            cautions = ", ".join(record.cautions) if record.cautions else "none flagged"
            self.meta_label.setText(
                f"Categories: {', '.join(record.categories)} | "
                f"Bots: {', '.join(record.originating_bots) or 'unknown'} | "
                f"Received period: {record.received_period.start} to {record.received_period.end} "
                f"(discovery time not recorded) | Cautions: {cautions}"
            )
            sources_html = self._render_sources(record)
            advice = record.implementation_advice
            html = (
                f"<p>{record.summary}</p>"
                f"<p><b>Bot suggestion (not source evidence):</b> {advice.get('text', '')}</p>"
                f"{sources_html}"
            )
            self.summary_browser.setHtml(html)
        else:
            self.title_label.setText(f"Weekly performance: {record.bot}  (id: {record.id})")
            self.meta_label.setText(
                f"Verification status: {record.verification_status} | "
                f"Received period: {record.received_period.start} to {record.received_period.end} "
                f"(discovery time not recorded)"
            )
            caveats = "<br>".join(record.caveats)
            html = (
                f"<p>{record.summary}</p>"
                f"<p><i>Weekly performance record, not an idea and not a score Smarty calculated.</i></p>"
                f"<p>{caveats}</p>"
            )
            self.summary_browser.setHtml(html)

        self.notes_edit.blockSignals(True)
        self.practical_steps_edit.blockSignals(True)
        self.notes_edit.setPlainText(us.notes)
        self.practical_steps_edit.setPlainText(us.practical_steps)
        self.notes_edit.blockSignals(False)
        self.practical_steps_edit.blockSignals(False)

        self._update_status_label(us)

    def _render_sources(self, idea) -> str:
        if not idea.sources:
            note = idea.missing_source_note or "no source URL on file"
            return f"<p><i>Sources: {note}</i></p>"
        parts = []
        for s in idea.sources:
            url = s.get("url", "")
            parts.append(f"<li>{url} (unchecked)</li>")
        return "<p>Sources (unverified):</p><ul>" + "".join(parts) + "</ul>"

    def _update_status_label(self, us) -> None:
        if us.is_conflicted("status"):
            choices = ", ".join(f"{v} ({dev})" for v, dev, _ in us.conflicts["status"])
            self.status_label.setText(f"Status conflict, not resolved: {choices}")
        else:
            self.status_label.setText(f"Status: {us.status}")

    # ----------------------------------------------------------- status

    def _on_status_clicked(self, status: str) -> None:
        if self._current_content_id is None:
            return
        if status == "rejected" and not self._reject_armed:
            self._reject_armed = True
            self._update_reject_button_label()
            QTimer.singleShot(REJECT_CONFIRM_WINDOW_MS, self._disarm_reject)
            return
        self._reject_armed = False
        self.store.set_status(self._current_content_id, status)
        self._update_reject_button_label()
        self._update_status_label(self.store.user_state(self._current_content_id))
        self._refresh_record_list()

    def _disarm_reject(self) -> None:
        self._reject_armed = False
        self._update_reject_button_label()

    def _update_reject_button_label(self) -> None:
        self.reject_button.setText("Confirm reject?" if self._reject_armed else "rejected")

    # ------------------------------------------------------------ notes

    def _schedule_notes_save(self) -> None:
        self._notes_timer.start(AUTOSAVE_DEBOUNCE_MS)

    def _schedule_steps_save(self) -> None:
        self._steps_timer.start(AUTOSAVE_DEBOUNCE_MS)

    def _flush_notes(self) -> None:
        if self._current_content_id is None:
            return
        text = self.notes_edit.toPlainText()
        if text != self.store.user_state(self._current_content_id).notes:
            self.store.set_notes(self._current_content_id, text)

    def _flush_practical_steps(self) -> None:
        if self._current_content_id is None:
            return
        text = self.practical_steps_edit.toPlainText()
        if text != self.store.user_state(self._current_content_id).practical_steps:
            self.store.set_practical_steps(self._current_content_id, text)

    def _flush_pending_edits(self) -> None:
        if self._notes_timer.isActive():
            self._notes_timer.stop()
            self._flush_notes()
        if self._steps_timer.isActive():
            self._steps_timer.stop()
            self._flush_practical_steps()

    # ------------------------------------------------------------- sync

    def run_sync(self) -> None:
        from datetime import datetime, timezone

        result = sync_notes_journal(self.store, self.paths, self.sync_config)
        if result.outcome == "ok":
            self._last_notes_sync = datetime.now(timezone.utc).isoformat()
        self._refresh_sync_label(result.outcome)
        self._refresh_record_list()

    def _refresh_sync_label(self, outcome: str | None = None) -> None:
        text = f"Last successful notes sync: {self._last_notes_sync}"
        if outcome and outcome != "ok":
            text += f"  (last attempt: {outcome})"
        self.sync_label.setText(text)

    def run_cloud_sync(self) -> None:
        from smarty.cloud_sync import sync_with_cloud

        result = sync_with_cloud(self.store, self.paths)
        if result.outcome == "ok":
            self.sync_label.setText(
                f"Cloud sync OK: pulled {result.pulled}, pushed {result.pushed}"
            )
        else:
            self.sync_label.setText(f"Cloud sync: {result.outcome} ({result.detail})")
        self._refresh_record_list()

    # --------------------------------------------------------- device id

    def _refresh_device_label_button(self) -> None:
        label = self.paths.device_label or "(unlabeled - click to set)"
        self.device_label_button.setText(f"This computer: {label}")

    def _on_set_device_label(self) -> None:
        import dataclasses

        text, ok = QInputDialog.getText(
            self,
            "Label this computer",
            "A short label so edits from this computer are identifiable during sync "
            "(e.g. Rudy-Laptop). Never invented automatically.",
            text=self.paths.device_label,
        )
        if not ok or not text.strip():
            return
        save_device_label(text.strip())
        self.paths = dataclasses.replace(self.paths, device_label=text.strip())
        self.store.paths = self.paths
        self._refresh_device_label_button()

    # -------------------------------------------------------- import

    def _on_import_batch(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Import batch", "", "JSON files (*.json)")
        if not file_name:
            return
        cache_path = self.paths.local_catalog_dir / "current.json"
        try:
            report, catalog = import_file(cache_path, Path(file_name))
        except (ImportRejected, OSError, ValueError) as exc:
            QMessageBox.critical(self, "Import rejected", str(exc))
            return

        self.store.catalog = catalog
        self._populate_tiles()
        self._refresh_record_list()

        summary = (
            f"Added: {len(report.added_ids)}\n"
            f"Updated: {len(report.updated_ids)}\n"
            f"Skipped (stale revision, kept current text): {len(report.skipped_stale_ids)}\n"
            f"Kept as alternate (same revision, different text): {len(report.kept_alternate_ids)}\n"
            f"No changes (already applied): {'yes' if report.no_op else 'no'}"
        )
        QMessageBox.information(self, "Import complete", summary)

    # ------------------------------------------------------------ close

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self._flush_pending_edits()
        super().closeEvent(event)
