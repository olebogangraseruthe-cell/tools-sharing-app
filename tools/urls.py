from django.urls import path

from . import views

urlpatterns = [
    path('', views.tool_list, name='tool_list'),
    path('tools/<int:pk>/', views.tool_detail, name='tool_detail'),
    path('register/', views.register, name='register'),
    path('tools/add/', views.add_tool, name='add_tool'),
    path('tools/<int:pk>/request/', views.request_tool, name='request_tool'),
    path('requests/mine/', views.my_requests, name='my_requests'),
        path('tools/mine/', views.my_tools, name='my_tools'),
    path('tools/<int:pk>/returned/', views.mark_returned, name='mark_returned'),
    path('requests/<int:pk>/approve/', views.decide_request,
         {'decision': 'approve'}, name='approve_request'),
    path('requests/<int:pk>/decline/', views.decide_request,
         {'decision': 'decline'}, name='decline_request'),    
]