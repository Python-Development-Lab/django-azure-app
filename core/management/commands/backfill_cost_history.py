"""One-time backfill of CostRecord from historical Cost Management export
CSVs, as opposed to core/services.py's daily sync path which only ever
reads the single most-recently-modified blob in the whole `cost-exports`
container.

Context (10.08.2026): the recurring `resource-costs-daily` export only
covers data from its creation date forward -- Cost Management exports
have no retroactive memory. To backfill the Monthly Trend chart's
"Last 12 Months" view, four separate one-time exports (historical-q1..q4,
each <=3 months, Daily's API-enforced maximum) were manually created via
`az rest` under a *separate* blob prefix (resource-costs-historical/),
deliberately kept apart from the daily export's resource-costs/ prefix so
this backfill never risks _fetch_latest_export_csv() picking up a stale
historical file as "the latest" on some future daily sync.

This command is meant to be run manually, once, from an App Service SSH
shell (`python manage.py backfill_cost_history`) -- not on a schedule,
not called from any view. If Azure's export retention window changes or
a wider historical range is ever needed again, re-run the `az rest`
export creation steps documented in the 10.08.2026 session notes before
re-running this command.
"""
import logging
import os

from django.core.management.base import BaseCommand

from core.services import sync_cost_export_csv

logger = logging.getLogger(__name__)

HISTORICAL_PREFIX = "resource-costs-historical/"


class Command(BaseCommand):
    help = (
        "One-time backfill: read every CSV blob under the "
        "resource-costs-historical/ prefix and upsert into CostRecord. "
        "Safe to re-run -- sync_cost_export_csv() upserts on "
        "(date, resource_id), so re-running just re-applies the same rows."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List the blobs that would be processed, without writing to CostRecord.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        account_name = os.environ.get("COST_EXPORT_STORAGE_ACCOUNT")
        if not account_name:
            self.stderr.write(self.style.ERROR(
                "COST_EXPORT_STORAGE_ACCOUNT is not set -- nothing to do."
            ))
            return
        container_name = os.environ.get("COST_EXPORT_CONTAINER", "cost-exports")

        try:
            from azure.identity import ManagedIdentityCredential
            from azure.storage.blob import ContainerClient
        except ImportError:
            self.stderr.write(self.style.ERROR(
                "azure-storage-blob is not installed in this environment."
            ))
            return

        credential = ManagedIdentityCredential()
        container_client = ContainerClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            container_name=container_name,
            credential=credential,
        )

        blobs = [
            b for b in container_client.list_blobs(name_starts_with=HISTORICAL_PREFIX)
            if b.name.endswith(".csv")
        ]

        if not blobs:
            self.stdout.write(self.style.WARNING(
                f"No CSV blobs found under '{HISTORICAL_PREFIX}' in container "
                f"'{container_name}'. Nothing to backfill."
            ))
            return

        self.stdout.write(f"Found {len(blobs)} historical CSV blob(s):")
        for b in blobs:
            self.stdout.write(f"  - {b.name} ({b.size} bytes)")

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run -- no data written."))
            return

        total_synced, total_skipped = 0, 0
        for b in blobs:
            self.stdout.write(f"Processing {b.name} ...")
            blob_client = container_client.get_blob_client(b.name)
            try:
                # utf-8-sig: same BOM-stripping fix as the daily sync path
                # (core/services.py _fetch_latest_export_csv) -- Azure's
                # export CSVs are BOM-prefixed regardless of whether the
                # export is recurring or one-time.
                csv_text = blob_client.download_blob().readall().decode("utf-8-sig")
            except Exception:
                logger.exception("backfill_cost_history: failed to read blob %s", b.name)
                self.stderr.write(self.style.ERROR(f"  Failed to read {b.name}, skipping."))
                continue

            synced, skipped = sync_cost_export_csv(csv_text)
            total_synced += synced
            total_skipped += skipped
            self.stdout.write(f"  synced={synced} skipped={skipped}")

        self.stdout.write(self.style.SUCCESS(
            f"Backfill complete. Total synced={total_synced} skipped={total_skipped}."
        ))
