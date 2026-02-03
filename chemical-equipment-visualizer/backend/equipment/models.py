from django.db import models

class Dataset(models.Model):
    name = models.CharField(max_length=150)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name="equipment"
    )

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)   # renamed from category
    material = models.CharField(max_length=100)

    flowrate = models.FloatField()             # REQUIRED BY TASK
    pressure = models.FloatField()
    temperature = models.FloatField()

    def __str__(self):
        return self.name
