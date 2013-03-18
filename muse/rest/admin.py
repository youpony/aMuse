import datetime
import datetime
from django.contrib import admin
from muse.rest.models import Museum, Item, Exhibition, ItemImage

class MuseumAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Museum info',
            {'fields':['name', 'address', 'referral']
        }),
    )

    list_filter = ['name']
    search_fields = ['name']


class UserImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1


class ItemAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Item info',
            {'fields': ['name', 'desc', 'author', 'year']
        }),
        ('Exhibition info',
            {'fields': ['exhibitions']
        }),
    )

    inlines = [UserImageInline]
    list_display = ('name', 'author', 'year', 'actually_exposed')
    list_filter = ['author', 'year']
    filter_horizontal = [ 'exhibitions', ]
    search_fields = ['name']

    def actually_exposed(self, obj):
        """
        This method chek if the item is exposed in an exhibition that is
        actually public.
        """
        return obj.exhibitions.filter(end_date__gte=datetime.date.today())\
            .count() > 0
    actually_exposed.boolean = True
    actually_exposed.short_description = "Actually exposed?"


class ExhibitionAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Exhibition info',
            {'fields': ['museum', 'title', 'description', 'image']
        }),
        ('Date information',
            {'fields': ['start_date', 'end_date']
        }),
    )

    list_display = ('title', 'museum', 'start_date', 'end_date')
    list_display_links = ('title', 'start_date', 'end_date')
    list_filter = ['museum', 'start_date']
    search_fields = ['title', 'museum']


admin.site.register(Museum, MuseumAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Exhibition, ExhibitionAdmin)
