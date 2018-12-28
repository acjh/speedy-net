from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_sites_with_login, exclude_on_speedy_match
from speedy.core.blocks.models import Block
from .test_factories import ActiveUserFactory


@only_on_sites_with_login
class ViewProfileTestCase(SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()

    @exclude_on_speedy_match
    def test_has_access(self):
        self.assertTrue(expr=self.user.has_perm(perm='accounts.view_profile', obj=self.other_user))
        self.assertTrue(expr=self.other_user.has_perm(perm='accounts.view_profile', obj=self.user))

    @exclude_on_speedy_match
    def test_has_no_access_if_blocked(self):
        Block.objects.block(blocker=self.other_user, blocked=self.user)
        self.assertFalse(expr=self.user.has_perm(perm='accounts.view_profile', obj=self.other_user))
        self.assertFalse(expr=self.other_user.has_perm(perm='accounts.view_profile', obj=self.user))

