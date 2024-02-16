from django.urls import path
from .views import RegisterView,RetrieveUserView,ImageView,ProfilePicView


urlpatterns = [
    path('register/',RegisterView.as_view()),
    path('me/',RetrieveUserView.as_view()),
    path('generate_image/',ImageView.as_view()),
    path('update_profile/',ProfilePicView.as_view()),
    
]
