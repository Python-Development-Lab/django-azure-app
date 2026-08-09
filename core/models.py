from django.db import models


class CostRecord(models.Model):
    """One row per (date, resource) synced from the Cost Management Export
    CSV in Blob Storage. Read by the FinOps dashboard via normal Django ORM
    queries instead of live Cost Management API calls, eliminating the 429
    exposure for the Monthly Trend and Cost by Resource views.
    """
    date = models.DateField(db_index=True)
    resource_id = models.CharField(max_length=512)
    resource_name = models.CharField(max_length=255)
    resource_group = models.CharField(max_length=255, blank=True, default="")
    cost = models.DecimalField(max_digits=12, decimal_places=4)
    currency = models.CharField(max_length=8, default="USD")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["date", "resource_id"], name="unique_cost_record_per_day"
            )
        ]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["resource_id"]),
        ]

    def __str__(self):
        return f"{self.date} {self.resource_name} ${self.cost}"
