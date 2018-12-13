from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from friendship.models import Friend, FriendshipRequest
from rules.contrib.views import PermissionRequiredMixin

from speedy.net.accounts.utils import get_site_profile_model
from speedy.net.profiles.views import UserMixin
from .rules import friend_request_sent


class UserFriendListView(UserMixin, generic.TemplateView):
    template_name = 'friends/friend_list.html'

    def get_friends(self):
        SiteProfile = get_site_profile_model()
        table_name = SiteProfile._meta.db_table
        qs = self.user.friends.all().extra(
            select={
                'last_visit': 'select last_visit from {} where user_id = friendship_friend.from_user_id'.format(table_name)
            },
        ).order_by('-last_visit')
        return qs

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'friends': self.get_friends(),
        })
        return cd


class ReceivedFriendshipRequestsListView(UserMixin, PermissionRequiredMixin, generic.TemplateView):
    template_name = 'friends/received_requests.html'
    permission_required = 'friends.view_requests'


class SentFriendshipRequestsListView(UserMixin, PermissionRequiredMixin, generic.TemplateView):
    template_name = 'friends/sent_requests.html'
    permission_required = 'friends.view_requests'


class LimitMaxFriendsMixin(object):
    def check_own_friends(self):
        user_number_of_friends = len(Friend.objects.friends(self.request.user))
        if user_number_of_friends >= settings.MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED:
            raise ValidationError(_("You already have {0} friends. You can't have more than {1} friends on "
                                    "Speedy Net. Please remove friends before you proceed.").format(
                user_number_of_friends,
                settings.MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED))

    def check_other_user_friends(self, user):
        other_user_number_of_friends = len(Friend.objects.friends(user))
        if other_user_number_of_friends >= settings.MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED:
            raise ValidationError(_("This user already has {0} friends. They can't have more than {1} friends on "
                                    "Speedy Net. Please ask them to remove friends before you proceed.").format(
                other_user_number_of_friends,
                settings.MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED))


class FriendRequestView(LimitMaxFriendsMixin, UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.request'

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def dispatch(self, request, *args, **kwargs):
        self.user = self.get_user()
        if request.user.is_authenticated:
            if friend_request_sent(request.user, self.user):
                messages.warning(request, _('You already requested friendship from this user.'))
                return redirect(to=self.user)
            if Friend.objects.are_friends(request.user, self.user):
                messages.warning(request, _('You already are friends with this user.'))
                return redirect(to=self.user)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            self.check_own_friends()
            self.check_other_user_friends(self.user)
        except ValidationError as e:
            messages.error(self.request, e.message)
            return redirect(to=self.user)
        Friend.objects.add_friend(request.user, self.user)
        messages.success(request, _('Friend request sent.'))
        return redirect(to=self.user)


class CancelFriendRequestView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.cancel_request'

    def post(self, request, *args, **kwargs):
        try:
            frequest = FriendshipRequest.objects.get(from_user=self.request.user, to_user=self.user)
        except FriendshipRequest.DoesNotExist:
            messages.error(request, _('No friend request.'))
            return redirect(to=self.user)
        frequest.cancel()
        messages.success(request, _("You've cancelled your friend request."))
        return redirect(to=self.user)


class AcceptRejectFriendRequestViewBase(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.view_requests'

    def get_redirect_url(self):
        return reverse('friends:list', kwargs={'slug': self.request.user.slug})

    def get_friend_request(self):
        if not hasattr(self, '_friend_request'):
            self._friend_request = get_object_or_404(
                self.user.friendship_requests_received,
                id=self.kwargs.get('friendship_request_id'),
            )
        return self._friend_request

    def get(self, request, *args, **kwargs):
        return redirect(to=self.get_redirect_url())

    def post(self, request, *args, **kwargs):
        frequest = self.get_friend_request()
        getattr(frequest, self.action)()
        messages.success(request, self.message)
        return redirect(to=self.get_redirect_url())


class AcceptFriendRequestView(LimitMaxFriendsMixin, AcceptRejectFriendRequestViewBase):
    action = 'accept'
    message = _('Friend request accepted.')

    def post(self, request, *args, **kwargs):
        frequest = self.get_friend_request()
        try:
            self.check_own_friends()
            self.check_other_user_friends(frequest.from_user)
        except ValidationError as e:
            messages.error(self.request, e.message)
            return redirect(to=self.get_redirect_url())
        return super().post(request, *args, **kwargs)


class RejectFriendRequestView(AcceptRejectFriendRequestViewBase):
    action = 'cancel'
    message = _('Friend request rejected.')


class RemoveFriendView(UserMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'friends.remove'

    def get(self, request, *args, **kwargs):
        return redirect(to=self.user)

    def post(self, request, *args, **kwargs):
        Friend.objects.remove_friend(self.request.user, self.user)
        messages.success(request, _('You have removed this user from friends.'))
        return redirect(to=self.user)