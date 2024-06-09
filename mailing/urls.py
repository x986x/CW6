from django.urls import path
from .views import (
    MailingCreateView, MailingDetailView, MessageCreateView, ClientListView, MailingListView, HomeView,
    DeliveryReportView, MailingDeleteView, ClientCreateView, MailingUpdateView, MessageUpdateView,
    MessageDeleteView, ClientUpdateView, ClientDeleteView, MessageListView, MailingToggleStatusView
)
from django.views.decorators.cache import cache_page

app_name = 'mailing'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('mailing/', MailingListView.as_view(), name='mailing'),
    path('create_mailing/', MailingCreateView.as_view(), name='create_mailing'),
    path('mailing/delete/<int:pk>/', MailingDeleteView.as_view(), name='delete_mailing'),
    path('mailing/update/<int:pk>/', MailingUpdateView.as_view(), name='update_mailing'),
    path('mailing/<int:pk>/', cache_page(60)(MailingDetailView.as_view()), name='mailing_detail'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create/', ClientCreateView.as_view(), name='create_client'),
    path('clients/update/<int:pk>/', ClientUpdateView.as_view(), name='update_client'),
    path('clients/delete/<int:pk>/', ClientDeleteView.as_view(), name='delete_client'),
    path('mailing/<int:mailing_pk>/message', MessageListView.as_view(), name='message_list'),
    path('mailing/toggle_status/<int:pk>/', MailingToggleStatusView.as_view(), name='mailing_toggle_status'),
    path('mailing/<int:mailing_pk>/create_message/', MessageCreateView.as_view(), name='create_message'),
    path('mailing/<int:mailing_pk>/update_message/<int:pk>/', MessageUpdateView.as_view(), name='update_message'),
    path('mailing/<int:mailing_pk>/delete_message/<int:pk>/', MessageDeleteView.as_view(), name='delete_message'),
    path('delivery_report/', cache_page(60)(DeliveryReportView.as_view()), name='delivery_report'),
]


