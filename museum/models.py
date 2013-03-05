from django.db import models

from filer.fields.image import FilerImageField
from django.utils.translation import ugettext_lazy as _

class Material(models.Model):
    '''
    This class represt an object that is/ was available at the museum. Materials
    need to remain in db even if they are no longer available
    '''
    id = models.AutoField(primary_key=True)

    name = models.CharField( _('nqme'), max_length=255 )

    description = description = models.CharField( _('description'), 
                                                  max_length=255 )
                                   
    insights = models.TextField(_(u'insights'), editable=False,
                                         blank='True', null='True')

    gallery = models.ForeignKey( 
                            Material, 
                            verbose_name=_('gallery in which the object is')
                            )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name=_("material")
        verbose_name_plural=_("materials")

     

class Gallery(models.Model):
    '''
    This class rapresent object gallary available in the museum. Galleries need
    to remain in db even if they are no longer available
    '''
    id = models.AutoField(primary_key=True)

    name = models.CharField(_('name'), max_length=255)

    description = description = models.CharField(_('description'), 
                                                 max_length=255)

    insights = models.TextField( _(u'insights'),blank='True', 
                                 null='True')

    dateandtime = models.DateField(
                         _(u'date in which the gallary start to be pubblic'))

    dateandtime_end = models.DateField(_(u'data in which the gallery close'),
                                       blank='True', null='True')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name=_("gallery")
        verbose_name_plural=_("galleries")



class Comments(models.Model):
    '''
    This class represent comments send by users, and append in personal
    stories
    '''
    id = models.AutoField(primary_key=True)
    
    author = models.CharField( _('author'), max_length=255)

    text = models.TextField(_(u'comment'))

    material = models.ForeignKey(Material, 
                                 verbose_name=_('object of the comment'))

    visible = models.BooelanField(_(u'visible'), null=False, blank=False) 

    def __unicode__(self):
        return self.text

    class Meta:
        verbose_name=_("material_image")
        verbose_name_plural=_("material_images")


#TODO: we need also user image, need tho check inheritance, i remember some problem
class Material_image(models.Model):
    '''
    This class represent image directly connect with the museom material,
    so it rapresent official images
    '''
    id = models.AutoField(primary_key=True)

    object = models.ForeignKey(Material)
    
    image = FilerImageField( verbose_name=_("image") )
        
    title = models.CharField( _("title"), max_length=255 )
    
    alt = models.CharField( _("alt text"), max_length=80, blank=True )

    def __unicode__(self):
        return self.title 

    class Meta:
        verbose_name=_("material_image")
        verbose_name_plural=_("material_images")



class Report(models.Model):
    '''
    This class represent reports send by anonimuos user to admin to signal
    offensive or inappropriate material
    '''
    id = models.AutoField(primary_key=True)

    text = models.TextField(_(u'problem'))

    image = models.ForeignKey(Material_image)

    comment = models.ForeignKey(Comments)

    def clean(self):
        if not self.image and not self.comment:
            raise ValidationError(_("Innapropriate content not specified, \
                                     please specify an image or a comment"))
    
    def __unicode__(self):
        return self.text + 'about ' + (self.)

    class Meta:
        verbose_name=_("report")
        verbose_name_plural=_("reports")


                            


