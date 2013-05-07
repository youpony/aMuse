from django.forms.models import inlineformset_factory

import muse.rest.models as rest

ItemImageFormSet = inlineformset_factory(
    rest.Item, rest.ItemImage, extra=3, max_num=3, can_delete=True
)
