from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_log, name='create_log'),
    path('log/<str:record_id>/', views.view_log, name='view_log'),
    path('log/<str:record_id>/edit/', views.edit_log, name='edit_log'),
    path('download/<str:record_id>/', views.download_file, name='download_file'),
    path('user/<str:username>/entries/', views.user_entries, name='user_entries'),
    path('log/public/<str:record_id>/', views.view_log_public, name='view_log_public'),
    path('download/public/<str:record_id>/', views.download_file_public, name='download_file_public'),
    path('my-magics/', views.my_magics, name='my_magics'),
    path('my-efforts/', views.my_efforts, name='my_efforts'),
    path('my-efforts/create/', views.create_effort, name='create_effort'),
    path('my-efforts/<int:pk>/complete/', views.complete_effort, name='complete_effort'),
    path('search/', views.search_logs, name='search_logs'),
    path('api/quote/', views.get_random_quote, name='get_random_quote'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/quotes/', views.manage_quotes, name='manage_quotes'),
    path('admin-panel/quotes/delete/<int:quote_id>/', views.delete_quote, name='delete_quote'),
    path('admin-panel/export-json/', views.export_data_json, name='export_data_json'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('my-jobs/create/', views.create_job, name='create_job'),
    path('my-jobs/edit/<int:job_id>/', views.edit_job, name='edit_job'),
    path('my-jobs/delete/<int:job_id>/', views.delete_job, name='delete_job'),
]
