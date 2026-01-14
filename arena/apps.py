from __future__ import annotations

from django.apps import AppConfig


class ArenaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "arena"

    def ready(self) -> None:
        """Best-effort SQLite tuning for demo deployments.

        WAL improves concurrency for readers while a writer is active.
        busy_timeout helps avoid 'database is locked' on short write bursts.
        """
        try:
            from django.conf import settings
            if settings.DATABASES.get("default", {}).get("ENGINE") != "django.db.backends.sqlite3":
                return

        except Exception:
            # If the DB isn't ready yet (e.g., first migrate), ignore.
            return
