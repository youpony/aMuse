# pylint: disable=R0904

import datetime
from django.contrib import admin

from muse.rest import models


class MuseumAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            'Museum info',
            {
                'fields': ['name', 'address', 'referral']
            }
        ),
    )

    list_filter = ['name']
    search_fields = ['name']


class ItemImageInline(admin.TabularInline):
    model = models.ItemImage
    extra = 1
    max_num = 3


class ItemAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            'Item info',
            {
                'fields': ['name', 'desc', 'author', 'year', 'city']
            }
        ),
        (
            'Exhibition info',
            {
                'fields': ['exhibitions']
            }
        ),
    )

    inlines = [ItemImageInline]
    list_display = ('name', 'author', 'year', 'actually_exposed')
    list_filter = ['author', 'year']
    filter_horizontal = ['exhibitions', ]
    search_fields = ['name']

    def actually_exposed(self, obj):
        """
        This method chek if the item is exposed in an exhibition that is
        actually public.
        """
        return obj.exhibitions.filter(
            end_date__gte=datetime.date.today()
        ).count() > 0

    actually_exposed.boolean = True
    actually_exposed.short_description = "Actually exposed?"


class ExhibitionAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            'Exhibition info',
            {
                'fields': ['museum', 'title', 'description', 'image', 'video']
            }
        ),
        (
            'Date information',
            {
                'fields': ['start_date', 'end_date']
            }
        ),
    )

    list_display = ('title', 'museum', 'start_date', 'end_date')
    list_display_links = ('title', 'start_date', 'end_date')
    list_filter = ['museum', 'start_date']
    search_fields = ['title', 'museum']


class PostAdmin(admin.ModelAdmin):
    pass


class TourAdmin(admin.ModelAdmin):
    readonly_fields = ('public_id', 'private_id')
    list_display = ('__unicode__', 'public_id', 'private_id')


# Museum management
admin.site.register(models.Museum, MuseumAdmin)
admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.Exhibition, ExhibitionAdmin)

# User story management
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Tour, TourAdmin)
