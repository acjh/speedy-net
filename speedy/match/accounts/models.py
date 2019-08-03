import logging

from django.db import models
from django.conf import settings as django_settings
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import gettext_lazy as _, pgettext_lazy, get_language
from django.core.exceptions import ValidationError

from translated_fields import TranslatedField

from speedy.core.base.utils import to_attribute
from speedy.core.accounts.models import SiteProfileBase, User
from speedy.core.blocks.models import Block
from speedy.match.likes.models import UserLike
from .managers import SiteProfileManager

logger = logging.getLogger(__name__)


class SiteProfile(SiteProfileBase):
    settings = django_settings.SPEEDY_MATCH_SITE_PROFILE_SETTINGS

    LOCALIZABLE_FIELDS = ('profile_description', 'children', 'more_children', 'match_description')

    RELATED_NAME = 'speedy_match_site_profile'

    HEIGHT_VALID_VALUES = range(settings.MIN_HEIGHT_ALLOWED, settings.MAX_HEIGHT_ALLOWED + 1)
    AGE_MATCH_VALID_VALUES = range(settings.MIN_AGE_MATCH_ALLOWED, settings.MAX_AGE_MATCH_ALLOWED + 1)

    RANK_0 = 0
    RANK_1 = 1
    RANK_2 = 2
    RANK_3 = 3
    RANK_4 = 4
    RANK_5 = 5

    RANK_CHOICES = (
        (RANK_0, _("No match")),
        (RANK_1, _("One heart")),
        (RANK_2, _("Two hearts")),
        (RANK_3, _("Three hearts")),
        (RANK_4, _("Four hearts")),
        (RANK_5, _("Five hearts")),
    )
    RANK_VALID_VALUES = [choice[0] for choice in RANK_CHOICES]

    @staticmethod
    def gender_to_match_default():
        return list()

    @staticmethod
    def diet_match_default():
        return dict({str(diet): __class__.RANK_5 for diet in User.DIET_VALID_VALUES})

    @staticmethod
    def smoking_status_match_default():
        return dict({str(smoking_status): __class__.RANK_5 for smoking_status in User.SMOKING_STATUS_VALID_VALUES})

    @staticmethod
    def relationship_status_match_default():
        return dict({str(relationship_status): __class__.RANK_5 for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES})

    @staticmethod
    def get_rank_description(rank):
        rank_descriptions = {
            __class__.RANK_0: _("No match"),
            __class__.RANK_1: _("One heart"),
            __class__.RANK_2: _("Two hearts"),
            __class__.RANK_3: _("Three hearts"),
            __class__.RANK_4: _("Four hearts"),
            __class__.RANK_5: _("Five hearts"),
        }
        return rank_descriptions.get(rank, "")

    user = models.OneToOneField(to=User, verbose_name=_('User'), primary_key=True, on_delete=models.CASCADE, related_name=RELATED_NAME)
    notify_on_like = models.PositiveIntegerField(verbose_name=_('On new likes'), choices=User.NOTIFICATIONS_CHOICES, default=User.NOTIFICATIONS_ON)
    active_languages = models.TextField(verbose_name=_('Active languages'), blank=True)
    height = models.SmallIntegerField(verbose_name=_('Height'), help_text=_('cm'), blank=True, null=True)
    profile_description = TranslatedField(
        field=models.TextField(verbose_name=_('Few words about me'), blank=True, null=True),
    )
    children = TranslatedField(
        field=models.TextField(verbose_name=_('Do you have children? How many?'), blank=True, null=True),
    )
    more_children = TranslatedField(
        field=models.TextField(verbose_name=_('Do you want (more) children?'), blank=True, null=True),
    )
    match_description = TranslatedField(
        field=models.TextField(verbose_name=_('My ideal match'), blank=True, null=True),
    )
    gender_to_match = ArrayField(models.SmallIntegerField(), verbose_name=_('Gender to match'), size=len(User.GENDER_VALID_VALUES), default=gender_to_match_default.__func__, blank=True, null=True)
    min_age_match = models.SmallIntegerField(verbose_name=_('Minimal age to match'), default=settings.MIN_AGE_MATCH_ALLOWED)
    max_age_match = models.SmallIntegerField(verbose_name=_('Maximal age to match'), default=settings.MAX_AGE_MATCH_ALLOWED)
    diet_match = JSONField(verbose_name=_('Diet match'), default=diet_match_default.__func__)
    smoking_status_match = JSONField(verbose_name=_('Smoking status match'), default=smoking_status_match_default.__func__)
    relationship_status_match = JSONField(verbose_name=_('Relationship status match'), default=relationship_status_match_default.__func__)
    activation_step = TranslatedField(
        field=models.PositiveSmallIntegerField(default=2),
    )

    objects = SiteProfileManager()

    @property
    def is_active(self):
        return ((self.user.is_active) and (get_language() in self.get_active_languages()))

    @property
    def is_active_and_valid(self):
        if (self.is_active):
            step, error_messages = self.validate_profile_and_activate(commit=False)
            error = False
            if (len(error_messages) > 0):
                error = True
            if (not (step == len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))):
                error = True
            if (error):
                logger.error("is_active_and_valid::user is active but not valid, step={step}, error_messages={error_messages}, self.user.pk={self_user_pk}, self.user.username={self_user_username}, self.user.slug={self_user_slug}".format(
                    step=step,
                    error_messages=error_messages,
                    self_user_pk=self.user.pk,
                    self_user_username=self.user.username,
                    self_user_slug=self.user.slug,
                ))
                return False
        return (self.is_active)

    class Meta:
        verbose_name = _('Speedy Match Profile')
        verbose_name_plural = _('Speedy Match Profiles')

    def __str__(self):
        return '{} @ Speedy Match'.format(super().__str__())

    def save(self, *args, **kwargs):
        if (self.activation_step < 2):
            self.activation_step = 2
        if (self.activation_step > len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)):
            self.activation_step = len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)
        if ((self.is_active) and (self.activation_step < len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))):
            self._deactivate_language(step=self.activation_step, commit=False)
        return super().save(*args, **kwargs)

    def _set_active_languages(self, languages):
        languages = sorted(list(set(languages)))
        self.active_languages = ','.join(set(languages))

    def _deactivate_language(self, step, commit=True):
        # Profile is invalid. Deactivate in this language.
        language_code = get_language()
        self._set_active_languages(set(self.get_active_languages()) - {language_code})
        self.activation_step = step
        if (commit):
            self.user.save_user_and_profile()

    def get_active_languages(self):
        return list(filter(None, (l.strip() for l in self.active_languages.split(','))))

    def validate_profile_and_activate(self, commit=True):
        # ~~~~ TODO: all the error messages in this function may depend on the current user's (or other user's) gender.
        from speedy.match.accounts import utils
        language_code = get_language()
        error_messages = []
        for step in utils.get_steps_range():
            fields = utils.get_step_fields_to_validate(step=step)
            for field_name in fields:
                try:
                    utils.validate_field(field_name=field_name, user=self.user)
                except ValidationError as e:
                    error_messages.append(str(e))
            if (len(error_messages) > 0):
                if (commit):
                    self._deactivate_language(step=step)
                return step, error_messages
        # Registration form is complete. Check if the user has a confirmed email address.
        step = len(__class__.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)
        if ((self.user.has_confirmed_email()) and (step >= self.activation_step)):
            if (commit):
                # Profile is valid. Activate in this language.
                self.activation_step = step
                languages = self.get_active_languages()
                if (not (language_code in languages)):
                    languages.append(language_code)
                    self._set_active_languages(languages=languages)
                self.user.save_user_and_profile()
        else:
            if (commit):
                self._deactivate_language(step=self.activation_step)
            error_messages.append(_("Please confirm your email address."))
        return step, error_messages

    def call_after_verify_email_address(self):
        pass

    def get_matching_rank(self, other_profile, second_call=True) -> int:
        if (self.user.pk == other_profile.user.pk):
            return self.__class__.RANK_0
        if True: # ---- matches run faster ---- ((self.is_active_and_valid) and (other_profile.is_active_and_valid)):
            # ---- matches run faster ---- if (Block.objects.there_is_block(user_1=self.user, user_2=other_profile.user)):
            # ---- matches run faster ----     return self.__class__.RANK_0
            if (other_profile.user.gender not in self.gender_to_match):
                return self.__class__.RANK_0
            if (not (self.min_age_match <= other_profile.user.get_age() <= self.max_age_match)):
                return self.__class__.RANK_0
            if (other_profile.user.diet == User.DIET_UNKNOWN):
                return self.__class__.RANK_0
            if (other_profile.user.smoking_status == User.SMOKING_STATUS_UNKNOWN):
                return self.__class__.RANK_0
            if (other_profile.user.relationship_status == User.RELATIONSHIP_STATUS_UNKNOWN):
                return self.__class__.RANK_0
            diet_rank = self.diet_match.get(str(other_profile.user.diet), self.__class__.RANK_0)
            smoking_status_rank = self.smoking_status_match.get(str(other_profile.user.smoking_status), self.__class__.RANK_0)
            relationship_status_rank = self.relationship_status_match.get(str(other_profile.user.relationship_status), self.__class__.RANK_0)
            rank = min([diet_rank, smoking_status_rank, relationship_status_rank])
            if (rank > self.__class__.RANK_0) and (second_call):
                other_user_rank = other_profile.get_matching_rank(other_profile=self, second_call=False)
                if (other_user_rank == self.__class__.RANK_0):
                    rank = self.__class__.RANK_0
            other_profile.rank = rank
            return rank
        else:
            if (not (self.is_active_and_valid)):
                logger.warning('get_matching_rank::get inside "if (not (self.is_active_and_valid)):", self={self}, other_profile={other_profile}'.format(self=self, other_profile=other_profile))
            if (not (other_profile.is_active_and_valid)):
                logger.warning('get_matching_rank::get inside "if (not (other_profile.is_active_and_valid)):", self={self}, other_profile={other_profile}'.format(self=self, other_profile=other_profile))
            return self.__class__.RANK_0

    def deactivate(self):
        self._set_active_languages([])
        self.activation_step = 2
        for language_code, language_name in django_settings.LANGUAGES:
            setattr(self, to_attribute(name='activation_step', language_code=language_code), 2)
        self.user.save_user_and_profile()

    def get_name(self):
        # Speedy Match name is user's first name.
        return self.user.get_first_name()

    def get_match_gender(self):
        if (len(self.gender_to_match) == 1):
            match_gender = User.GENDERS_DICT.get(self.gender_to_match[0])
        else:
            match_gender = User.GENDERS_DICT.get(User.GENDER_OTHER)
        return match_gender

    def get_like_gender(self):
        # No need to query the database if len(self.gender_to_match) is not 1.
        if ((len(self.gender_to_match) == 1) and ({self.get_match_gender()} == {like.to_user.get_gender() for like in UserLike.objects.get_like_list_to_queryset(user=self.user)} | {like.from_user.get_gender() for like in UserLike.objects.get_like_list_from_queryset(user=self.user)} | {self.get_match_gender()})):
            like_gender = self.get_match_gender()
        else:
            like_gender = User.GENDERS_DICT.get(User.GENDER_OTHER)
        return like_gender

    def get_diet_match_choices(self):
        return User.diet_choices(gender=self.get_match_gender())

    def get_smoking_status_match_choices(self):
        return User.smoking_status_choices(gender=self.get_match_gender())

    def get_relationship_status_match_choices(self):
        return User.relationship_status_choices(gender=self.get_match_gender())


