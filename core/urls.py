from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . views import CreateUserView, UserDetailView, AllUSerView

urlpatterns = [
    path('user/create/', CreateUserView.as_view(), name='create_user'),
    path('user/me/', UserDetailView.as_view(), name='user_details'),
    path('users/all/', AllUSerView.as_view(), name='all_users'),
    path('user/login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('rest-auth/', include('rest_framework.urls'))
]