from django.urls import path
from . import views
from . import admin

from . import websocket

urlpatterns = [
    path('data_view/', views.kafka_data_view, name='kafka-data'),
    path('trigger/', views.trigger_producer, name='trigger_producer'),
    path('data_view/', views.kafka_data_view, name='kafka_data_view'),
    path('data/web/', websocket.web),
    path('', views.home),
    



]
# urls.py

# from django.urls import path
# from . import views

# urlpatterns = [
#     # Other URLs...
#     path('data_view/', views.kafka_data_view, name='kafka_data_view'),
# ]
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('trigger/', views.trigger_producer, name='trigger_producer'),
# ]
# from django.urls import path, include

# from django.urls import path
# from . import views

# urlpatterns = [
#     path('trigger/', views.trigger_producer, name='trigger_producer'),
#     path('data_view/', views.data_view, name='data_view'),  # Add this line
# ]


# json---------------------------------
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('add_data/', views.DataView.as_view(), name='add_data'),
# ]



# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# urlpatterns = [
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     # Other URLs
# ]
# urlpatterns = [
#     path('data_list/', views.DataListView.as_view(), name='data_list'),
# ]
