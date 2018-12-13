from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.utils.module_loading import import_string
from django.views import generic
from friendship.models import FriendshipRequest
from rules.contrib.views import LoginRequiredMixin

from speedy.net.accounts.models import User, normalize_username
from speedy.net.friends.rules import friend_request_sent, is_friend


class UserMixin(object):
    user_slug_kwarg = 'slug'

    def use_request_user(self):
        return self.user_slug_kwarg not in self.kwargs

    def dispatch(self, request, *args, **kwargs):
        self.user = self.get_user()
        if not self.use_request_user() and self.user.slug != kwargs[self.user_slug_kwarg]:
            kwargs[self.user_slug_kwarg] = self.user.slug
            components = []
            components.extend(request.resolver_match.namespaces)
            components.append(request.resolver_match.url_name)
            return redirect(to=':'.join(components), permanent=True, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_user_queryset(self):
        return User.objects.active()

    def get_user(self):
        try:
            slug = self.kwargs.get(self.user_slug_kwarg)
            if self.use_request_user() or slug == 'me':
                if self.request.user.is_authenticated:
                    return self.request.user
                else:
                    raise PermissionDenied()
            user = self.get_user_queryset().get(Q(slug=slug) | Q(username=normalize_username(slug=slug)))
            if not user.profile.is_active:
                raise Http404('This user is not active on this site.')
            return user
        except User.DoesNotExist:
            raise Http404()

    def get_permission_object(self):
        return self.get_user()

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'user': self.user,
        })
        if self.request.user.is_authenticated():
            try:
                friend_request_received = FriendshipRequest.objects.get(from_user=self.user, to_user=self.request.user)
            except FriendshipRequest.DoesNotExist:
                friend_request_received = False
            cd.update({
                'user_is_friend': is_friend(self.request.user, self.user),
                'friend_request_sent': friend_request_sent(self.request.user, self.user),
                'friend_request_received': friend_request_received,
            })
        return cd


class MeView(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        url = self.request.user.get_absolute_url()
        rest = kwargs.get('rest')
        if rest:
            url += '/' + rest
        return url


class UserDetailView(UserMixin, generic.TemplateView):
    template_name = 'profiles/user_detail.html'

    def get_widget_kwargs(self):
        return {
            'entity': self.user,
            'viewer': self.request.user,
        }

    def get_widgets(self):
        widgets = []
        for widget_path in settings.USER_PROFILE_WIDGETS:
            widget_class = import_string(widget_path)
            widgets.append(widget_class(**self.get_widget_kwargs()))
        return widgets

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'widgets': self.get_widgets(),
        })
        return cd