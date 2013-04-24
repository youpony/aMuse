# pylint: disable=R0904
import hashlib
import os
import time
import re

from django.db import models
from django.dispatch import Signal, receiver
from django.core.exceptions import ValidationError
from django.core.mail import send_mail


def csrng_key():
    # os.random is a blocking call?
    return hashlib.sha256('{key}.{salt}'.format(
        key=time.time(),
        salt=os.urandom(100),
    )).hexdigest()


class Museum(models.Model):
    """
    A museum simply holds informations about spacial, temporal, and social
    coordinates.
    """
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    referral = models.EmailField(max_length=254)

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
    video = models.CharField(max_length=40, blank=True)

    def __unicode__(self):
        return u'{title}-{museum}'.format(title=self.title,
                                          museum=self.museum)

    def save(self, *args, **kwargs):
        """
        Override save method to ensure that end_date is equal or greather
        than start_date
        """
        if self.end_date < self.start_date:
            raise ValidationError('End date must to be after start date')

        super(Exhibition, self).save(*args, **kwargs)


class Item(models.Model):
    """
    An Item is an object present at the exhibition.
    """
    name = models.CharField(max_length=50)
    desc = models.TextField()
    author = models.CharField(max_length=50, blank=True)
    year = models.CharField(max_length=9)
    exhibitions = models.ManyToManyField(
        Exhibition,
        verbose_name='exhibitions where this item is available'
    )

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        """
        Override save  method to ensure that year use the format dddd or
        dddd-dddd where d rapresent an integer.
        This method is necessary to let user set a year for an item that
        haven't a fixed year date.
        """
        if not (re.match(r'^\d{1,4}$', str(self.year)) or
                re.match(r'^\d{1,4}-\d{1,4}$', str(self.year))):
            raise ValidationError('Year must be in format yyyy or yyyy-yyyy')

        super(Item, self).save(*args, **kwargs)


class Tour(models.Model):
    """
    The user visiting the exhibition.
    """
    public_id = models.CharField(default=csrng_key, max_length=64,
                                 unique=True, editable=False)
    private_id = models.CharField(default=csrng_key, max_length=64,
                                  unique=True, editable=False)
    name = models.CharField(max_length=60)
    email = models.EmailField(max_length=254)
    museum = models.ForeignKey(Museum)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'{user}\'s tour'.format(user=unicode(self.name))


class ItemImage(models.Model):
    """
    This class represent image directly connect with the museum material,
    so it rapresent official images.
    """
    title = models.CharField(max_length=80)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images/{.title:.80}'.format)
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
    item = models.ForeignKey(
        Item, on_delete=models.PROTECT, blank=True, null=True
    )
    image = models.ImageField(
        upload_to='people_uploads', blank=True, null=True
    )
    text = models.TextField()
    # XXX. add pointer to the current exhibition.

    def save(self, *args, **kwargs):
        """
        Override save method to ensure that a Post is referred to at least
        one object or an image, and ensure that at least one of this
        two possibility is set.
        """
        if ((self.item is None and self.image is None)):
            raise ValidationError('A Post must refer to an image or '
                                  'to an item')

        super(Post, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{index}-{tour}'.format(index=self.ordering_index,
                                        tour=self.tour)

    class Meta:
        ordering = ['ordering_index']
        unique_together = (('tour', 'ordering_index'),)


#story_created = Signal(providing_args=['tour', 'museum'])

#@receiver(story_created, sender=Tour)
def notify_email(sender, **kwargs):
    tour = kwargs['tour']
    museum = kwargs['museum']
    genurl = kwargs['url']

    referral = museum.referral
    sbj = '[{mname}] Created new story: {id}'.format(
        mname=museum.name, id=tour.public_id[:5])
    body = '''
       Hey {nickname}!
       Somebody, hopefully you, crated a new story.
       Here is your public link: {publink}
       Here is your editable link, do not share this with no one! {privlink}.

       Sincerly yours,
        -- {mname} Notification System
    '''.format(
        mname=museum.name,
        nickname=tour.name,
        publink=genurl(pk=tour.public_id),
        privlink=genurl(pk=tour.private_id),
    )

    # XXX. send as mime message? correct format?
    send_mail(sbj, body, referral, [tour.email])
