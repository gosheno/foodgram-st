from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    AvatarUploadSerializer,
    SetPasswordSerializer,
    FollowSerializer,
)
from users.models import Follow, User
from api.paginations import CustomPagination


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
        serializer = self.get_serializer(
            request.user,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        return self.update_avatar(request) if request.method == "PUT" \
            else self.delete_avatar(request)

    def update_avatar(self, request):
        user = request.user
        serializer = AvatarUploadSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            avatar_url = request.build_absolute_uri(user.avatar.url)
            return Response({"avatar": avatar_url}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        user = request.user
        recipes_limit = request.query_params.get('recipes_limit')

        queryset = User.objects.filter(following__user=user) \
            .annotate(recipes_count=Count('recipes'))
        page = self.paginate_queryset(queryset)

        context = self.get_serializer_context()
        context['recipes_limit'] = recipes_limit

        serializer = FollowSerializer(page, many=True, context=context)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = self.get_object()

        if author == user or \
                Follow.objects.filter(user=user, following=author).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        Follow.objects.create(user=user, following=author)

        serializer = FollowSerializer(
            author,
            context=self._get_follow_context(request),
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        user = request.user
        author = self.get_object()

        follow = Follow.objects.filter(user=user, following=author)
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
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(
                    serializer.validated_data['current_password']):
                return Response(
                    {'current_password': ['Неверный пароль.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_follow_context(self, request):
        return {
            'request': request,
            'recipes_limit': request.query_params.get('recipes_limit')
        }
