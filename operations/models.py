from django.db import models

class Operation(models.Model):
    op_type = models.CharField(max_length=50, default='Export')
    category = models.CharField(max_length=200)
    partner_country = models.CharField(max_length=100, default='Ukraine')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()

    def str(self):
        return f"{self.op_type} - {self.category}"
