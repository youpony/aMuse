from django.db import models
from django.contrib.auth.models import User


class Museum(models.Model):
    """
    A museum simply holds informations about spacial, temporal, and social
    coordinates.
    """
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    referral = models.EmailField()


class Exhibition(models.Model):
    """
    An exhibition is the setting up of a presentation of different items,
    collected differently by each user in tours.
    """
    museum = models.ForeignKey(Museum)
    title = models.CharField(max_length=50)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='uploads')


class Item(models.Model):
    """
    An Item is an object present at the exhibition.
    """
    name = models.CharField(max_length=30)
    desc = models.TextField()
    author = models.CharField(max_length=30)
    year = models.IntegerField()
    exhibitions = models.ManyToManyField(Exhibition,
                  verbose_name='exhibitions where this item is available')


class Post(models.Model):
    """
    A post is some kind of content present/taken at the exhibition,
    that the user wants to share.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(Item)
    text = models.TextField()


class Tour(models.Model):
    """
    The user visiting the exhibition.
    """
    date = models.DateTimeField(auto_now_add=True)
    posts = models.ManyToManyField(Post, verbose_name='posts collected during the tour')
    user = models.ForeignKey(User, verbose_name='user having the tour')
    exhibition = models.ForeignKey(Exhibition)

