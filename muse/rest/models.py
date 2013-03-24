# pylint: disable=R0904

from django.db import models
from django.core.exceptions import ValidationError

import hashlib


class Museum(models.Model):
    """
    A museum simply holds informations about spacial, temporal, and social
    coordinates.
    """
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    referral = models.EmailField()

    def __unicode__(self):
        return unicode(self.name)


class Exhibition(models.Model):
    """
    An exhibition is the setting up of a presentation of different items,
    collected differently by each user in tours.
    """
    museum = models.ForeignKey(Museum)
    title = models.CharField(max_length=60)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='uploads')

    def __unicode__(self):
        return "{title}-{museum}".format(title=unicode(self.title),
                                         museum=unicode(self.museum))


class Item(models.Model):
    """
    An Item is an object present at the exhibition.
    """
    name = models.CharField(max_length=50)
    desc = models.TextField()
    author = models.CharField(max_length=50, blank=True)
    year = models.IntegerField()
    exhibitions = models.ManyToManyField(
        Exhibition,
        verbose_name='exhibitions where this item is available'
    )

    def __unicode__(self):
        return unicode(self.name)


class Tour(models.Model):
    """
    The user visiting the exhibition.
    """
    #public_id =
    private_id = models.CharField(max_length=64, unique=True, editable=False)
    date = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(max_length=50)
    museum = models.ForeignKey(Museum)
    email = models.EmailField(max_length=254)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "User {user} tour".format(user=unicode(self.nickname))

    def save(self, *args, **kwargs):
        """
        This method ensure to set the private_id
        """
        if not self.private_id:
            self.private_id = hashlib.sha256(
                "{email}_{timestamp}_{nickname}".format(
                    email=self.email,
                    timestamp=self.timestamp,
                    nickname=self.nickname,
                )
            ).hexdigest()
        super(Tour, self).save(*args, **kwargs)


class Image(models.Model):
    """
    This class represents an image
    """
    title = models.CharField(max_length=80)
    image = models.ImageField(upload_to='people_uploads')

    def __unicode__(self):
        return self.title


class ItemImage(Image):
    """
    This class represent image directly connect with the museum material,
    so it rapresent official images
    """
    item = models.ForeignKey(Item)
    description = models.CharField(max_length=250)


class Post(models.Model):
    """
    A post is some kind of content present/taken at the exhibition,
    that the user wants to share.
    """
    ordering_index = models.IntegerField()
    tour = models.ForeignKey(Tour)
    timestamp = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(Item, blank=True, null=True)
    image = models.ForeignKey(Image, blank=True, null=True)
    text = models.TextField()

    def clean(self):
        """
        This method ensure tha a Post is referred to at least one object or an
        image, and ensure that only one of this two possibility is set
        """
        if ((self.item is None and self.image is None) or
                (self.item and self.image)):
            raise ValidationError('A Post must refer to an image or '
                                  'to an item, but not to both')

    class Meta:
        ordering = ['ordering_index']
        unique_together = (("tour", "ordering_index"),)
