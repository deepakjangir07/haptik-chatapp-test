from django.db import connections
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication

from chat import settings
from core.serializers import MessageModelSerializer, UserModelSerializer
from core.models import MessageModel,Connection,Group


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication scheme used by DRF. DRF's SessionAuthentication uses
    Django's session framework for authentication which requires CSRF to be
    checked. In this case we are going to disable CSRF tokens for the API.
    """

    def enforce_csrf(self, request):
        return


class MessagePagination(PageNumberPagination):
    """
    Limit message prefetch to one page.
    """
    page_size = settings.MESSAGES_TO_LOAD


class MessageModelViewSet(ModelViewSet):
    queryset = MessageModel.objects.all()
    serializer_class = MessageModelSerializer
    allowed_methods = ('GET', 'POST', 'HEAD', 'OPTIONS')
    authentication_classes = (CsrfExemptSessionAuthentication,)
    pagination_class = MessagePagination

    def list(self, request, *args, **kwargs):
        print(request.user)
        print(kwargs)

      
        target = self.request.query_params.get('target', None)
        user_id = self.request.query_params.get('user_id',None)

        
        if target is not None:
            print(target)
            print(user_id)
            if user_id:
                user = User.objects.get(id=user_id)
                if not user.is_active:
                    from .models import Group
                    group = Group.objects.get(title=user.username)
                    print(group)
                    connection = Connection.objects.get(group=group)
                    print(connection)
                    if connection:
                        all_group_users = connection.users.all().values_list('username',flat=True).distinct()
                        print(all_group_users)
                        print(request.user)
                        self.queryset = self.queryset.filter(Q(recipient_id=user.id))
                else:
                    self.queryset = self.queryset.filter(
                        Q(recipient=request.user, user__username=target) |
                        Q(recipient__username=target, user=request.user))
        return super(MessageModelViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        print(request.user)
        print(kwargs['pk'])

        msg = get_object_or_404(
            self.queryset.filter(Q(recipient=request.user) |
                                 Q(user=request.user),
                                 Q(pk=kwargs['pk'])))
        serializer = self.get_serializer(msg)
        return Response(serializer.data)


class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer
    allowed_methods = ('GET', 'HEAD', 'OPTIONS')
    pagination_class = None  # Get all user

    def list(self, request, *args, **kwargs):
        # Get all users except yourself
        self.queryset = self.queryset.exclude(id=request.user.id)
        return super(UserModelViewSet, self).list(request, *args, **kwargs)
