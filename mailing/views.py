from datetime import timedelta
from random import sample
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, CreateView, DetailView, DeleteView, UpdateView
from blog.models import BlogPost
from .models import Mailing, Client, Message, Log
from .forms import MailingForm, MessageForm, ClientForm


class HomeView(TemplateView):
    template_name = 'mailing/home.html'
    extra_context = {
        'title': 'Главная страница',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count_mailing'] = Mailing.objects.count()
        active_mailings_count = Mailing.objects.filter(status__in=['created', 'started']).count()
        context['active_mailings_count'] = active_mailings_count
        unique_clients_count = Client.objects.filter(is_active=True).distinct().count()
        context['unique_clients_count'] = unique_clients_count
        all_posts = list(BlogPost.objects.all())
        context['random_blog_posts'] = sample(all_posts, min(3, len(all_posts)))
        context['object_list'] = Mailing.objects.all()
        user = self.request.user
        user_group_names = [group.name for group in user.groups.all()]
        context['user_group_names'] = user_group_names
        return context


class MailingListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'
    permission_required = 'mailing.view_mailing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_group_names = [group.name for group in user.groups.all()]
        context['user_group_names'] = user_group_names
        return context

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Managers').exists():
            return super().get_queryset()
        else:
            return super().get_queryset().filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/create_mailing.html'
    permission_required = 'mailing.add_mailing'

    def form_valid(self, form):
        new_mailing = form.save(commit=False)
        new_mailing.owner = self.request.user

        # Set end_time based on frequency
        if new_mailing.frequency == 'daily':
            new_mailing.end_time = new_mailing.start_time + timedelta(days=1)
        elif new_mailing.frequency == 'weekly':
            new_mailing.end_time = new_mailing.start_time + timedelta(days=7)
        elif new_mailing.frequency == 'monthly':
            new_mailing.end_time = new_mailing.start_time + timedelta(days=30)
        else:
            new_mailing.end_time = None

        new_mailing.save()
        self.mailing_pk = new_mailing.pk
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('mailing:create_message', kwargs={'mailing_pk': self.mailing_pk})


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    fields = ('start_time', 'frequency', 'recipients', 'status')
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing')
    permission_required = 'mailing.change_mailing'

    def form_valid(self, form):
        updated_mailing = form.save(commit=False)
        updated_mailing.owner = self.request.user

        # Set end_time based on frequency
        if updated_mailing.frequency == 'daily':
            updated_mailing.end_time = updated_mailing.start_time + timedelta(days=1)
        elif updated_mailing.frequency == 'weekly':
            updated_mailing.end_time = updated_mailing.start_time + timedelta(days=7)
        elif updated_mailing.frequency == 'monthly':
            updated_mailing.end_time = updated_mailing.start_time + timedelta(days=30)
        else:
            updated_mailing.end_time = None

        is_active = self.request.POST.get('is_active')
        updated_mailing.is_active = is_active == 'on'
        updated_mailing.save()
        return super().form_valid(form)

    def get_object(self, queryset=None):
        mailing = super().get_object(queryset)
        if not self.request.user.is_superuser and self.request.user != mailing.owner:
            raise Http404("You do not have permission to access this mailing")
        return mailing


class MailingDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'
    permission_required = 'mailing.view_mailing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = Message.objects.filter(mailing=self.object)
        return context


class MailingDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Mailing
    success_url = reverse_lazy('mailing:mailing')
    extra_context = {
        'title': 'Удаление записи:'
    }
    permission_required = 'mailing.delete_mailing'

    def get_object(self, queryset=None):
        mailing = super().get_object(queryset)
        mailing = get_object_or_404(Mailing, id=mailing.pk)
        user_groups = [group.name for group in self.request.user.groups.all()]
        if mailing.owner != self.request.user and 'Managers' not in user_groups:
            raise Http404
        return mailing


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'

    def post(self, request, *args, **kwargs):
        if 'action' in request.POST and request.POST['action'] in ['activate', 'deactivate']:
            client_id = request.POST.get('client_id')
            client = get_object_or_404(Client, pk=client_id)

            if not request.user.has_perm('mailing.view_client'):
                return HttpResponseRedirect(reverse('mailing:client_list'))

            if request.POST['action'] == 'deactivate':
                client.is_active = False
            elif request.POST['action'] == 'activate':
                client.is_active = True
            client.save()
            return HttpResponseRedirect(reverse('mailing:client_list'))
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_admin'] = user.is_superuser
        context['is_manager'] = user.groups.filter(name='Manager').exists() or user.groups.filter(name='Managers').exists()
        return context

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Managers').exists():
            return super().get_queryset()
        else:
            return super().get_queryset().filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailing:client_list')
    template_name = 'mailing/create_client.html'
    permission_required = 'mailing.add_client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Создание нового клиента."
        return context

    def form_valid(self, form):
        client = form.save(commit=False)
        client.owner = self.request.user
        client.save()
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailing:client_list')
    template_name = 'mailing/client_form.html'
    permission_required = 'mailing.change_client'

    def get_object(self, queryset=None):
        client = super().get_object(queryset)
        user = self.request.user
        if user != client.owner and not user.is_superuser and not user.groups.filter(name='Managers').exists():
            raise Http404("You do not have permission to access this client")
        return client


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('mailing:client_list')
    template_name = 'mailing/client_confirm_delete.html'
    permission_required = 'mailing.delete_client'

    def get_object(self, queryset=None):
        client = super().get_object(queryset)
        if client.owner != self.request.user:
            raise Http404("You do not have permission to access this client")
        return client


class MessageListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'
    permission_required = 'mailing.view_message'

    def get_queryset(self):
        mailing_pk = self.kwargs['mailing_pk']
        return Message.objects.filter(mailing__pk=mailing_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_group_names = [group.name for group in user.groups.all()]
        context['user_group_names'] = user_group_names
        context['mailing_pk'] = self.kwargs['mailing_pk']
        return context


class MessageCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/create_message.html'
    success_url = reverse_lazy('mailing:mailing')
    permission_required = 'mailing.add_message'

    def form_valid(self, form):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['mailing_pk'])
        message = form.save(commit=False)
        message.mailing = mailing
        message.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:mailing')
    permission_required = 'mailing.change_message'

    def form_valid(self, form):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['mailing_pk'])
        message = form.save(commit=False)
        message.mailing = mailing
        message.save()
        return super().form_valid(form)

    def get_object(self, queryset=None):
        client = super().get_object(queryset)
        if client.owner != self.request.user:
            raise Http404("You do not have permission to access this client")
        return client


class MailingToggleStatusView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Mailing
    fields = []
    template_name = 'mailing/mailing_toggle_status.html'
    permission_required = 'mailing.can_disable_mailings'

    def post(self, request, *args, **kwargs):
        mailing = self.get_object()
        user = request.user
        if user.is_superuser or user.groups.filter(name='Managers').exists() or mailing.owner == user:
            action = request.POST.get('action')
            if action == 'deactivate':
                mailing.status = 'stopped'
            elif action == 'activate':
                mailing.status = 'started'
            mailing.save()
            return HttpResponseRedirect(reverse('mailing:mailing'))
        else:
            raise Http404("You do not have permission to change the mailing status")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_superuser
        context['is_manager'] = self.request.user.groups.filter(name='Manager').exists()
        return context

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Managers').exists():
            return super().get_queryset()
        else:
            return super().get_queryset().filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy('mailing:mailing')
    template_name = 'mailing/message_confirm_delete.html'
    permission_required = 'mailing.delete_message'

    def get_object(self, queryset=None):
        client = super().get_object(queryset)
        if client.owner != self.request.user:
            raise Http404("You do not have permission to access this message")
        return client


class DeliveryReportView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Log
    template_name = 'mailing/delivery_report.html'
    context_object_name = 'delivery_logs'
    permission_required = 'mailing.view_log'

    def get_queryset(self):
        return Log.objects.filter(status='success')
