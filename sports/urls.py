from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 


#app_name = "sports"

urlpatterns = [
    path("", views.index, name="index"),
    path("create_event", views.create_event, name="create_event"),
    path("login", views.login_user, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_user, name="logout"),
    path("password_reset_sent", views.password_reset_sent, name="password_reset_sent"),

    # apis
    path("events", views.events, name="events"),
    path("past_events", views.past, name="past"),
    path("event/<int:event_id>", views.event, name="event"),
    path("update/<int:id>", views.update, name="update"),
    path("delete/<int:id>", views.delete, name="delete"),


]