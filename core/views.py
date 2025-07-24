from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from . serializers import CreateUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]


class UserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class AllUSerView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer