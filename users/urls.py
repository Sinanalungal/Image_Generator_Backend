from django.urls import path
from .views import RegisterView,RetrieveUserView,ImageView,ProfilePicView,RetrieveUserData,UserDataUpdateView,AdminDataFetch,EditUserData,DeleteUser,SearchQuery


urlpatterns = [
    path('register/',RegisterView.as_view()),
    path('me/',RetrieveUserView.as_view()),
    path('generate_image/',ImageView.as_view()),
    path('update_profile/',ProfilePicView.as_view()),
    path('fetchdata/',RetrieveUserData.as_view()),
    path('edit_details/',UserDataUpdateView.as_view()),
    path('users_data/',AdminDataFetch.as_view()),
    path('edit_user/<int:id>/',EditUserData.as_view()),
    path('delete_user/<int:id>/',DeleteUser.as_view()),
    path('search/',SearchQuery.as_view()),
]
