from django.contrib import admin
from muse.rest.models import Item, Exhibition

class ItemAdmin(admin.ModelAdmin):
    fieldsets = (
        ( 'Item info',
            {'fields': ['name', 'desc', 'author', 'year']
        }),
        ( 'Exhibition info',
            {'fields': ['exhibitions']
        }),
    )

    list_display = ('name', 'author', 'year')
    list_filter = ['author', 'year']
    search_fields = ['name']


class ExhibitionAdmin(admin.ModelAdmin):
    fieldsets = (
        ( 'Exhibition info',
            {'fields': ['museum', 'title', 'description', 'image']
        }),
        ( 'Date information',
            {'fields': ['start_date', 'end_date']
        }),
    )

    list_display = ('title', 'museum', 'start_date', 'end_date')
    list_display_links = ('title', 'start_date', 'end_date')
    list_filter = ['museum', 'start_date']
    search_fields = ['title', 'museum']


admin.site.register(Item, ItemAdmin)
admin.site.register(Exhibition, ExhibitionAdmin)
