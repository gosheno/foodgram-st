from api.paginations import CustomPagination
from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache

from users.models import Follow, User
from users.serializers import (
    AvatarUploadSerializer, FollowSerializer,
    SetPasswordSerializer, UserCreateSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path="me",
    )
    def me(self, request):
        """Получить данные текущего пользователя."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        """Обновить или удалить аватар."""
        if request.method == "PUT":
            return self.update_avatar(request)
        return self.delete_avatar(request)

    def update_avatar(self, request):
        """Обновить аватар пользователя."""
        serializer = AvatarUploadSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        avatar_url = request.build_absolute_uri(request.user.avatar.url)
        return Response({"avatar": avatar_url})

    def delete_avatar(self, request):
        """Удалить аватар пользователя."""
        request.user.avatar.delete(save=False)
        request.user.avatar = None
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Получить подписки пользователя."""
        queryset = User.objects.filter(following__user=request.user).annotate(
            recipes_count=Count('recipes')
        ).prefetch_related('recipes')
        page = self.paginate_queryset(queryset)
        context = {'request': request, 'recipes_limit': request.query_params.get('recipes_limit')}
        serializer = FollowSerializer(page, many=True, context=context)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        """Подписаться на пользователя."""
        author = self.get_object()
        if author == request.user:
            return Response(
                {"detail": "You cannot subscribe to yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(user=request.user, following=author).exists():
            return Response(
                {"detail": "You are already subscribed to this user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(user=request.user, following=author)
        serializer = FollowSerializer(author, context=self._get_follow_context(request))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        """Отписаться от пользователя."""
        follow = Follow.objects.filter(user=request.user, following=self.get_object())
        if not follow.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='set_password',
    )
    def set_password(self, request):
        """Изменить пароль пользователя."""
        serializer = SetPasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_follow_context(self, request):
        """Получить контекст для сериализатора подписок."""
        return {
            'request': request,
            'recipes_limit': request.query_params.get('recipes_limit')
        }
        
    def retrieve(self, request, *args, **kwargs):
        cache_key = f"user_{kwargs['pk']}_details"
        data = cache.get(cache_key)
        
        if not data:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            cache.set(cache_key, data, timeout=60*15)  # 15 минут
        return Response(data)