from django.db import models


class Item(models.Model):
    """ Item class
    """
    name = models.CharField(
        max_length=256,
    )
