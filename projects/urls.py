from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('list/', views.ProjectListView.as_view(), name='project_list'),
    path('favorites/', views.FavoriteProjectsView.as_view(), name='favorite_projects'),
    path('create-project/', views.CreateProjectView.as_view(), name='create_project'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/edit/', views.EditProjectView.as_view(), name='edit_project'),
    path('<int:pk>/complete/', views.CompleteProjectView.as_view(), name='complete_project'),
    path('<int:pk>/toggle-participate/', views.ToggleParticipateView.as_view(), name='toggle_participate'),
    path('<int:pk>/toggle-favorite/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
]