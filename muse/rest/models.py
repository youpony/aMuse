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
        return self.name


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
        return u'{title}-{museum}'.format(title=self.title,
                                          museum=self.museum)


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


class User(models.Model):
    nickname = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)

    def __unicode__(self):
        return self.nickname


class Tour(models.Model):
    """
    The user visiting the exhibition.
    """
    #public_id =
    private_id = models.CharField(max_length=64, unique=True, editable=False)
    user = models.ForeignKey(User, blank=True, null=True)
    museum = models.ForeignKey(Museum)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'User {user} tour'.format(user=unicode(self.user))


class UserImage(models.Model):
    """
    This class represents an image.
    """
    title = models.CharField(max_length=80, blank=True, null=True)
    image = models.ImageField(upload_to='people_uploads')

    def __unicode__(self):
        return self.title


class ItemImage(models.Model):
    """
    This class represent image directly connect with the museum material,
    so it rapresent official images.
    """
    title = models.CharField(max_length=80)
    item = models.ForeignKey(Item)
    image = models.ImageField(upload_to='item_images')
    description = models.CharField(max_length=250, blank=True, null=True)

    def __unicode__(self):
        return self.title


class Post(models.Model):
    """
    A post is some kind of content present/taken at the exhibition,
    that the user wants to share.
    """
    ordering_index = models.IntegerField()
    tour = models.ForeignKey(Tour)
    timestamp = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(Item, blank=True, null=True)
    image = models.ForeignKey(UserImage, blank=True, null=True)
    text = models.TextField()

    def clean(self):
        """
        This method ensure that a Post is referred to at least one object or an
        image, and ensure that only one of this two possibility is set.
        """
        if ((self.item is None and self.image is None)):
            raise ValidationError('A Post must refer to an image or '
                                  'to an item')

    def __unicode__(self):
        return u'{index}-{tour}'.format(index=self.ordering_index,
                                        tour=self.tour)

    class Meta:
        ordering = ['ordering_index']
        unique_together = (('tour', 'ordering_index'),)
