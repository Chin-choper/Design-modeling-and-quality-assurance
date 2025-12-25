from django.db import models

class Operation(models.Model):
    TYPE_CHOICES = [
        ('Export', 'Експорт'),
        ('Import', 'Імпорт'),
    ]

    op_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100)
    partner_country = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.op_type} - {self.category}"
