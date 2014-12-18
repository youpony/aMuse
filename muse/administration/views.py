from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.forms.util import ErrorList
from django.forms.forms import NON_FIELD_ERRORS
from django.shortcuts import render_to_response
from django.db.models.deletion import ProtectedError
from django.template import RequestContext
from django.db import transaction
from django.utils.translation import ugettext as _

from muse.administration.forms import ItemImageFormSet
import muse.rest.models as rest


class ExhibitionList(ListView):
    model = rest.Exhibition
    template_name = 'administration/exhibition/exhibitions_list.html'
    context_object_name = 'exhibitions'
    paginate_by = 21

    def get_queryset(self):
        return super(ExhibitionList, self).get_queryset().order_by(
            '-end_date', 'pk'
        )

    def get_context_data(self, **kwargs):
        context = super(ExhibitionList, self).get_context_data(**kwargs)
        self.request.breadcrumbs([
            ("Home", reverse('exhibitions_list')),
        ])
        context['item_without_exhibition'] = (
            rest.Item.objects.filter(exhibitions=None).count()
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ExhibitionList, self).dispatch(*args, **kwargs)


class ExhibitionQr(ListView):
    model = rest.Item
    context_object_name = 'items'
    template_name = 'administration/exhibition/exhibition_qr.html'
    success_url = reverse_lazy('exhibitions_list')

    def get_context_data(self, **kwargs):
        epk = self.kwargs['pk']
        get_object_or_404(rest.Exhibition, pk=epk)

        context = super(ExhibitionQr, self).get_context_data(**kwargs)
        context['items'] = filter(lambda i: i.exhibitions.filter(pk=epk).all(),
                                  context['items'])
        context['epk'] = str(epk)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ExhibitionQr, self).dispatch(*args, **kwargs)


class ExhibitionCreate(CreateView):
    model = rest.Exhibition
    success_url = reverse_lazy('exhibitions_list')
    template_name = 'administration/exhibition/exhibition_add_edit.html'

    def get_context_data(self, **kwargs):
        context = super(ExhibitionCreate, self).get_context_data(**kwargs)
        context['title'] = _('Add exhibition')
        self.request.breadcrumbs([
            ("Home", reverse('exhibitions_list')),
            (_("Exhibition"), self.request.get_full_path)
        ])
        return context

    def form_valid(self, form):
        try:
            return super(ExhibitionCreate, self).form_valid(form)
        except ValidationError as e:
            errors = ErrorList()
            for error in e.messages:
                errors.append(error)
            errors = form._errors.setdefault(NON_FIELD_ERRORS, errors)

            return super(ExhibitionCreate, self).form_invalid(form)

    @method_decorator(login_required)
    @method_decorator(permission_required('rest.add_exhibition'))
    def dispatch(self, *args, **kwargs):
        return super(ExhibitionCreate, self).dispatch(*args, **kwargs)


class ExhibitionEdit(UpdateView):
    model = rest.Exhibition
    success_url = reverse_lazy('exhibitions_list')
    template_name = 'administration/exhibition/exhibition_add_edit.html'

    def get_context_data(self, **kwargs):
        context = super(ExhibitionEdit, self).get_context_data(**kwargs)
        context['title'] = _('Update exhibition')
        self.request.breadcrumbs([
            ("Home", reverse('exhibitions_list')),
            (_("Exhibition"), self.request.get_full_path)
        ])
        return context

    def form_valid(self, form):
        try:
            return super(ExhibitionEdit, self).form_valid(form)
        except ValidationError as e:
            errors = ErrorList()
            for error in e.messages:
                errors.append(error)
            errors = form._errors.setdefault(NON_FIELD_ERRORS, errors)

            return super(ExhibitionEdit, self).form_invalid(form)

    @method_decorator(login_required)
    @method_decorator(permission_required('rest.change_exhibition'))
    def dispatch(self, *args, **kwargs):
        return super(ExhibitionEdit, self).dispatch(*args, **kwargs)


class ExhibitionDelete(DeleteView):
    model = rest.Exhibition
    template_name = 'administration/confirm_delete.html'
    success_url = reverse_lazy('exhibitions_list')
    unsuccess_template = 'administration/unable_to_delete.html'

    def get_context_data(self, **kwargs):
        context = super(ExhibitionDelete, self).get_context_data(**kwargs)
        context['undo_url'] = reverse('exhibitions_list')
        self.request.breadcrumbs([
            ("Home", reverse('exhibitions_list')),
            (_("Exhibition"), self.request.get_full_path)
        ])
        return context

    def delete(self, request, *args, **kwargs):
        try:
            return super(ExhibitionDelete, self).delete(
                request, *args, **kwargs
            )
        except ProtectedError:
            self.get_context_data()
            return render_to_response(
                self.unsuccess_template,
                {'object': self.get_object()},
                context_instance=RequestContext(request)
            )

    @method_decorator(login_required)
    @method_decorator(permission_required('rest.delete_exhibition'))
    def dispatch(self, *args, **kwargs):
        return super(ExhibitionDelete, self).dispatch(*args, **kwargs)


class ItemList(ListView):
    model = rest.Item
    template_name = 'administration/item/items_list.html'
    context_object_name = 'items'
    paginate_by = 21

    def get_context_data(self, **kwargs):
        context = super(ItemList, self).get_context_data(**kwargs)
        self.request.breadcrumbs([
            ("Home", reverse('exhibitions_list')),
            (_("Exhibition"), self.request.get_full_path)
        ])
        context['exhibition_pk'] = self.kwargs['pk']
        return context

    def get_queryset(self):
        exhibition_pk = self.kwargs['pk']
        return rest.Item.objects.filter(exhibitions=exhibition_pk).order_by(
            'pk'
        )

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ItemList, self).dispatch(*args, **kwargs)


class ItemCreate(CreateView):
    model = rest.Item
    template_name = 'administration/item/item_add_edit.html'

    def get_success_url(self):
        return reverse_lazy('items_list', args=[self.kwargs['exhibition_pk']])

    def get_context_data(self, **kwargs):
        context = super(ItemCreate, self).get_context_data(**kwargs)
        context['title'] = _('Add item')

        if self.request.POST:
            context['itemimage_formset'] = ItemImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context['itemimage_formset'] = ItemImageFormSet(
                instance=self.object
            )

        self.request.breadcrumbs("Home", reverse('exhibitions_list'))

        if 'exhibition_pk' in self.kwargs:
            self.request.breadcrumbs(
                _("Exhibition"),
                reverse('items_list', args=[self.kwargs['exhibition_pk']])
            )
        else:
            self.request.breadcrumbs(
                _("Items"),
                reverse('item_no_exhibition_list')
            )

        self.request.breadcrumbs(_("Item"), self.request.get_full_path)
        return context

    def form_valid(self, form):
        with transaction.commit_manually():
            try:
                super(ItemCreate, self).form_valid(form)
            except ValidationError as e:
                transaction.rollback()
                errors = ErrorList()
                for error in e.messages:
                    errors.append(error)
                errors = form._errors.setdefault(NON_FIELD_ERRORS, errors)

                return super(ItemCreate, self).form_invalid(form)

            context = self.get_context_data()

            itemimage_form = context['itemimage_formset']

            if itemimage_form.is_valid():
                itemimage_form.save()
                transaction.commit()
                return redirect(self.get_success_url())
            else:
                transaction.rollback()
                return self.render_to_response(
                    self.get_context_data(form=form)
                )

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    @method_decorator(login_required)
    @method_decorator(permission_required('rest.add_item'))
    def dispatch(self, *args, **kwargs):
        return super(ItemCreate, self).dispatch(*args, **kwargs)


class ItemEdit(UpdateView):
    model = rest.Item
    template_name = 'administration/item/item_add_edit.html'

    def get_success_url(self):
        if 'exhibition_pk' in self.kwargs:
            return reverse_lazy(
                'items_list', args=[self.kwargs['exhibition_pk']]
            )
        else:
            return reverse('item_no_exhibition_list')

    def get_context_data(self, **kwargs):
        context = super(ItemEdit, self).get_context_data(**kwargs)
        context['title'] = _('Update item')

        if self.request.POST:
            context['itemimage_formset'] = ItemImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context['itemimage_formset'] = ItemImageFormSet(
                instance=self.object
            )

        self.request.breadcrumbs("Home", reverse('exhibitions_list'))

        if 'exhibition_pk' in self.kwargs:
            self.request.breadcrumbs(
                _("Exhibition"),
                reverse('items_list', args=[self.kwargs['exhibition_pk']])
            )
        else:
            self.request.breadcrumbs(
                _("Items"),
                reverse('item_no_exhibition_list')
            )
        self.request.breadcrumbs(_("Item"), self.request.get_full_path)

        return context

    def form_valid(self, form):
        try:
            super(ItemEdit, self).form_valid(form)
        except ValidationError as e:
            errors = ErrorList()
            for error in e.messages:
                errors.append(error)
            errors = form._errors.setdefault(NON_FIELD_ERRORS, errors)

            return super(ItemEdit, self).form_invalid(form)

        context = self.get_context_data()

        itemimage_form = context['itemimage_formset']

        if itemimage_form.is_valid():
            itemimage_form.save()

            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    @method_decorator(login_required)
    @method_decorator(permission_required('rest.change_item'))
    def dispatch(self, *args, **kwargs):
        return super(ItemEdit, self).dispatch(*args, **kwargs)


class ItemDelete(DeleteView):
    model = rest.Item
    template_name = 'administration/confirm_delete.html'
    unsuccess_template = 'administration/unable_to_delete.html'

    def get_success_url(self):
        if 'exhibition_pk' in self.kwargs:
            return reverse_lazy(
                'items_list', args=[self.kwargs['exhibition_pk']]
            )
        else:
            return reverse_lazy('item_no_exhibition_list')

    def get_context_data(self, **kwargs):
        context = super(ItemDelete, self).get_context_data(**kwargs)
        self.request.breadcrumbs("Home", reverse('exhibitions_list'))

        if 'exhibition_pk' in self.kwargs:
            self.request.breadcrumbs(
                _("Exhibition"),
                reverse('items_list', args=[self.kwargs['exhibition_pk']])
            )
            context['undo_url'] = reverse(
                'items_list', args=[self.kwargs['exhibition_pk']]
            )
        else:
            self.request.breadcrumbs(
                _("Items"),
                reverse('item_no_exhibition_list')
            )
            context['undo_url'] = reverse('item_no_exhibition_list')

        self.request.breadcrumbs(_("Item"), self.request.get_full_path)
        return context

    def delete(self, request, *args, **kwargs):
        self.item_exhibitions = self.get_object().exhibitions.all()
        try:
            return super(ItemDelete, self).delete(request, *args, **kwargs)
        except ProtectedError:
            self.get_context_data()
            return render_to_response(
                self.unsuccess_template,
                {'object': self.get_object()},
                context_instance=RequestContext(request)
            )

    @method_decorator(login_required)
    @method_decorator(permission_required('rest.delete_item'))
    def dispatch(self, *args, **kwargs):
        return super(ItemDelete, self).dispatch(*args, **kwargs)


class ItemWithoutExhibition(ListView):
    model = rest.Item
    template_name = 'administration/item/items_list.html'
    context_object_name = 'items'
    paginate_by = 21

    def get_context_data(self, **kwargs):
        context = super(ItemWithoutExhibition, self).get_context_data(**kwargs)
        self.request.breadcrumbs([
            ("Home", reverse('exhibitions_list')),
            (_("Items"), self.request.get_full_path)
        ])
        return context

    def get_queryset(self):
        return rest.Item.objects.filter(exhibitions=None).order_by('pk')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ItemWithoutExhibition, self).dispatch(*args, **kwargs)
