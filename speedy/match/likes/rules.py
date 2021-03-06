from rules import predicate, add_perm, is_authenticated

from speedy.core.accounts.base_rules import is_self
from speedy.core.blocks.rules import there_is_block
from speedy.core.accounts.models import User
from .models import UserLike


@predicate
def already_likes(user, other_user):
    return UserLike.objects.filter(from_user=user, to_user=other_user).exists()


@predicate
def both_are_users(user, other_user):
    return ((isinstance(user, User)) and (isinstance(other_user, User)))


add_perm('likes.like', is_authenticated & ~is_self & ~there_is_block & ~already_likes & both_are_users)
add_perm('likes.unlike', is_authenticated & ~is_self & ~there_is_block & already_likes & both_are_users)
add_perm('likes.view_likes', is_authenticated & is_self)


