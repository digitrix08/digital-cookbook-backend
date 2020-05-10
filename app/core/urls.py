from .views import CreatUserView, CreateTokenView, ManageUserView
from django.urls import path

app_name = "core"

urlpatterns = [
    path('create/', CreatUserView.as_view(), name="create"),
    path('token/', CreateTokenView.as_view(), name="token"),
    path('profile/', ManageUserView.as_view(), name="profile")
]
