from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalog(), name='catalog'),

    path(
        'booking/<int:booking_id>/',
        views.create_booking,
        name = "booking"
    ),

    path('profile/', views.profile, name='profile'),

    path('manage/', views.manage, name='manage'),

    path(
        'manager/confirm/<int:booking_id>/',
        views.confirm_booking,
        name = "confirm_booking"
    ),

    path(
        'manager/issue/int:booking_id>/',
        views.issue_equiipment,
        name = "issue_equiipment"
    ),

    path(
        'manager/return/<int:booking_id>/',
        views.return_equiipment,
        name = "return_equiipment"
    ),

    path(
        'statistics/',
        views.statistics,
        name = "statistics"
    )
]