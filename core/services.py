"""
Cost Management Export sync and DB-backed reads for the FinOps dashboard.

Kept out of views.py deliberately (per AI PR Review feedback): a function
like sync_cost_export_csv() has no @login_required/CSRF guard of its own --
that's fine as a plain function, but its presence in views.py next to
URL-mapped view functions is a convention risk for future contributors who
might accidentally wire it to a URL. Nothing here is a Django view.
"""
import csv as _csv
import io as _io
import logging
import os
from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.cache import cache
from django.db.models import Sum as _Sum
from django.db.models.functions import TruncMonth as _TruncMonth

from .models import CostRecord

logger = logging.getLogger(__name__)


def _parse_cost_export_row(row, fieldnames):
    """Parse one Cost Management export CSV row into
    (date, resource_id, resource_name, resource_group, cost, currency),
    or None if the row is unusable (missing columns, malformed cost,
    unparseable date, or a credit/negative-cost row)."""
    def _find_col(*candidates):
        # Azure's actual Cost Management export column casing has varied
        # across API versions/timeframes (observed 10.08.2026: lowercase
        # "date"/"costInBillingCurrency"/"resourceGroupName"/"billingCurrency"
        # rather than the PascalCase names in Microsoft's documented schema).
        # Match case-insensitively so this doesn't silently skip every row
        # again the next time Azure's casing shifts.
        lower_map = {fn.lower(): fn for fn in fieldnames}
        for c in candidates:
            actual = lower_map.get(c.lower())
            if actual is not None:
                return actual
        return None

    col_date = _find_col("Date")
    col_resource_id = _find_col("ResourceId")
    col_rg = _find_col("ResourceGroupName", "ResourceGroup")
    col_cost = _find_col("CostInBillingCurrency", "Cost")
    col_currency = _find_col("BillingCurrency", "BillingCurrencyCode", "Currency")

    if not (col_date and col_resource_id and col_cost):
        return None

    resource_id = (row.get(col_resource_id) or "").strip()
    if not resource_id:
        return None
    try:
        # Decimal built directly from the raw string, never through float --
        # the model's cost field is a DecimalField, and float() as an
        # intermediary risks binary floating-point drift before Django/the
        # DB driver ever sees the value. Per AI PR Review feedback.
        cost = Decimal(str(row.get(col_cost) or "0"))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if cost <= 0:
        return None

    raw_date = (row.get(col_date) or "").strip()
    try:
        if len(raw_date) == 8 and raw_date.isdigit():
            d = date(int(raw_date[0:4]), int(raw_date[4:6]), int(raw_date[6:8]))
        elif "/" in raw_date:
            # Observed 10.08.2026: Azure's actual export uses MM/DD/YYYY
            # with slashes (e.g. "08/07/2026"), not the ISO "YYYY-MM-DD"
            # format Microsoft's documented schema implies. Every row
            # silently failed date parsing (int("08/07/2026") -> ValueError)
            # until this branch was added -- synced=0 skipped=223 despite
            # the case-insensitive column fix already working correctly.
            mm, dd, yyyy = raw_date.split("/")[:3]
            d = date(int(yyyy), int(mm), int(dd))
        else:
            parts = raw_date[:10].split("-")
            d = date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return None

    name = resource_id.rstrip("/").split("/")[-1] if resource_id else resource_id
    rg = (row.get(col_rg) or "").strip() if col_rg else ""
    if not rg:
        parts = resource_id.split("/")
        lower_parts = [p.lower() for p in parts]
        if "resourcegroups" in lower_parts:
            idx = lower_parts.index("resourcegroups")
            if idx + 1 < len(parts):
                rg = parts[idx + 1]
    currency = (row.get(col_currency) or "USD").strip() if col_currency else "USD"

    return d, resource_id, name, rg, cost, currency


def sync_cost_export_csv(csv_text):
    """Parse a Cost Management export CSV and upsert every usable row into
    CostRecord. Idempotent: MonthToDate exports re-deliver the whole month
    on every run, so unchanged days are simply overwritten with the same
    value, not duplicated (unique constraint on date+resource_id).
    Returns (rows_synced, rows_skipped)."""
    reader = _csv.DictReader(_io.StringIO(csv_text))
    fieldnames = reader.fieldnames or []
    synced, skipped = 0, 0
    for row in reader:
        parsed = _parse_cost_export_row(row, fieldnames)
        if parsed is None:
            skipped += 1
            continue
        d, resource_id, name, rg, cost, currency = parsed
        CostRecord.objects.update_or_create(
            date=d, resource_id=resource_id,
            defaults={
                "resource_name": name, "resource_group": rg,
                "cost": cost, "currency": currency,
            },
        )
        synced += 1
    return synced, skipped


def _fetch_latest_export_csv():
    """Read the most recently modified CSV blob from the Cost Management
    Export container via the App Service's Managed Identity. Returns the
    CSV text, or None if the storage account isn't configured, the
    container is empty, or any error occurs -- callers must treat None as
    "sync unavailable, fall back to live API", never as an empty dataset.
    """
    account_name = os.environ.get("COST_EXPORT_STORAGE_ACCOUNT")
    if not account_name:
        return None
    container_name = os.environ.get("COST_EXPORT_CONTAINER", "cost-exports")
    try:
        from azure.identity import ManagedIdentityCredential
        from azure.storage.blob import ContainerClient
    except ImportError:
        logger.warning("finops: azure-storage-blob not installed, skipping export sync")
        return None
    try:
        credential = ManagedIdentityCredential()
        container_client = ContainerClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            container_name=container_name,
            credential=credential,
        )
        blobs = sorted(
            container_client.list_blobs(),
            key=lambda b: b.last_modified,
            reverse=True,
        )
        csv_blob = next((b for b in blobs if b.name.endswith(".csv")), None)
        if csv_blob is None:
            logger.warning("finops: no CSV blob found in cost export container")
            return None
        blob_client = container_client.get_blob_client(csv_blob.name)
        # utf-8-sig (not utf-8): Azure's export CSV is written with a
        # UTF-8 BOM. Plain utf-8 decoding leaves that BOM attached to the
        # first column name (observed 10.08.2026: fieldnames[0] came back
        # as '\ufeffdate', not 'date'), so _find_col("Date") never matched
        # and every row was silently skipped even with the other two
        # parsing fixes already in place. utf-8-sig strips the BOM if
        # present and is a no-op if absent -- safe either way.
        return blob_client.download_blob().readall().decode("utf-8-sig")
    except Exception:
        logger.exception("finops: failed to read cost export from blob storage")
        return None


def _sync_cost_export_if_stale(year, month, max_age_hours=20):
    """Sync the latest export CSV into CostRecord if we don't already have
    data for `today` (or the sync has never run for real). Cheap check:
    just look at whether any row exists for the current UTC date. Runs at
    most once per cold cache-population event, not on every request.

    Guarded by a short-lived cache lock (cache.add is atomic within a
    single process). This project uses Django's LocMemCache (see project
    gotcha: LocMemCache is not shared between gunicorn workers), so the
    lock only prevents duplicate downloads WITHIN one worker, not across
    the 2 configured workers -- two requests landing on different workers
    at the same cold-cache moment can still both sync in parallel. This
    is an accepted, non-corrupting trade-off: sync_cost_export_csv() is
    idempotent (update_or_create on the date+resource_id unique
    constraint), so the worst case is redundant network/CPU work, never
    duplicate or inconsistent rows. A true cross-worker lock would need
    a database-backed mechanism (e.g. select_for_update on a lock row)
    since Postgres, not the cache, is the only resource actually shared
    across workers in this deployment.
    """
    today = date.today()
    if not (year == today.year and month == today.month):
        return  # only the current month is kept fresh; past months are static
    if CostRecord.objects.filter(date=today).exists():
        return
    lock_key = f"finops_export_sync_lock:{today.isoformat()}"
    if not cache.add(lock_key, "1", 60):
        logger.info("finops: cost export sync already in progress on another worker/request, skipping")
        return
    csv_text = _fetch_latest_export_csv()
    if csv_text is None:
        return
    try:
        synced, skipped = sync_cost_export_csv(csv_text)
        logger.info("finops: cost export sync -- synced=%d skipped=%d" % (synced, skipped))
    except Exception:
        logger.exception("finops: cost export sync failed")


def _resource_costs_from_db(year, month, top_n=15):
    """Same shape as the live _resource_costs(): {"resources", "top", "total"}.
    Returns None (signal: fall back to live API) if there is no data for
    this month at all -- distinguishes "genuinely zero spend" (empty list,
    still a valid dict) from "we have never synced this month" (None)."""
    month_start = date(year, month, 1)
    month_end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    if not CostRecord.objects.filter(date__gte=month_start, date__lt=month_end).exists():
        return None
    qs = (
        CostRecord.objects
        .filter(date__gte=month_start, date__lt=month_end)
        .values("resource_id", "resource_name", "resource_group")
        .annotate(total_cost=_Sum("cost"))
        .order_by("-total_cost")
    )
    resources = [
        {
            "resource": r["resource_name"],
            "resource_group": r["resource_group"],
            "cost": round(float(r["total_cost"]), 3),
        }
        for r in qs
    ]
    total = round(sum(r["cost"] for r in resources), 2)
    return {"resources": resources, "top": resources[:top_n], "total": total}


def _monthly_trend_from_db(months=12):
    """Same shape as the live _monthly_trend(). Returns None (signal: fall
    back to live API) if there is no data at all yet."""
    if not CostRecord.objects.exists():
        return None
    qs = (
        CostRecord.objects
        .annotate(month=_TruncMonth("date"))
        .values("month")
        .annotate(total_cost=_Sum("cost"))
        .order_by("-month")[:months]
    )
    trend = [
        {
            "month": f"{r['month'].year:04d}-{r['month'].month:02d}",
            "label": r["month"].strftime("%b %Y"),
            "cost": round(float(r["total_cost"]), 2),
        }
        for r in qs
    ]
    trend.sort(key=lambda x: x["month"])
    return trend
