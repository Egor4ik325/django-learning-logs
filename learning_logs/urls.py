""" Define URL schemas for learning_logs Django application. """

from django.urls import path
from . import views

app_name = 'learning_logs'

urlpatterns = [
    # Home page (view's index() function)
    path('', views.index, name='index'),
    # All topics
    path('topics/', views.topics, name='topics'),
    # Specific topic page
    path('topics/<int:topic_id>/', views.topic, name='topic'),
    # Add new topic
    path('new_topic/', views.new_topic, name='new_topic'),
    # Add new entry
    path('new_entry/<int:topic_id>/', views.new_entry, name='new_entry'),
    # Edit entry
    path('edit_entry/<int:entry_id>/', views.edit_entry, name='edit_entry'),
]

# Forms:
# - [ ] url schema
# - [ ] form model
# - [ ] view/controller rendering
# - [ ] template/interface
# - [ ] references to the template/interface/page
