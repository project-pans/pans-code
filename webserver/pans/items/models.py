from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=255)
    upc = models.CharField(max_length=255)
    quantity = models.IntegerField()
    percent = models.FloatField()
    date = models.DateTimeField()
    weight_num = models.IntegerField()

    class Meta:
      verbose_name_plural = "items"

    def __str__(self):
        return self.name
