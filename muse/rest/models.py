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
    name = models.CharField(max_length=30)
    desc = models.TextField()
    author = models.CharField(max_length=30)
    year = models.IntegerField()
    exhibitions = models.ManyToManyField(
        Exhibition,
        verbose_name='exhibitions where this item is available'
    )

    def __unicode__(self):
        return unicode(self.name)


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
    #public_id =
    #private_id =

    date = models.DateTimeField(auto_now_add=True)
    posts = models.ManyToManyField(
        Post,
        verbose_name='posts collected during the tour'
    )
    user = models.ForeignKey(User, verbose_name='user having the tour')
    exhibition = models.ForeignKey(Exhibition)
    #email


class Image(models.Model):
    """
    This class represents an image
    """
    id = models.AutoField(primary_key=True)  # FIXME[ml]: id? O.o
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=250)
    image = models.ImageField(upload_to='people_uploads')

    def __unicode__(self):
        return self.title


class ItemImage(Image):
    """
    This class represent image directly connect with the museom material,
    so it represent official images
    """
    item = models.ForeignKey(Item)


class StoryImage(Image):
    """
    A StoryImage is an image loaded from a user in order to place it in the
    storyteller
    """
    #user
    pass
    #Not yet implemented, miss a foreign key to a story
