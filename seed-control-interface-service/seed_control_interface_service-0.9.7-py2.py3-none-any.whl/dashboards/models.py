from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from services.models import Service


@python_2_unicode_compatible
class WidgetData(models.Model):

    """ Metric a widget has data from
    """
    title = models.CharField(max_length=200)
    key = models.CharField(max_length=200)
    service = models.ForeignKey(
        Service, related_name='services_metrics', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, related_name='widgetdata_created', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        User, related_name='widgetdata_updated', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    user = property(lambda self: self.created_by)

    class Meta:
        verbose_name = 'widget data'
        verbose_name_plural = 'widget data sources'

    def __str__(self):  # __unicode__ on Python 2
        return "%s (%s)" % (self.title, self.key)


@python_2_unicode_compatible
class Widget(models.Model):

    """ Metric a widget has data from
    """
    WIDGET_TYPES = (
        ('bars', 'Bar Graph'),
        ('last', 'Last'),
        ('lines', 'Lines'),
        ('pie', 'Pie Chart'),
    )
    SHOW_NULLS = (
        ('omit', 'Omit'),
        ('zeroize', 'Zeroize'),
    )
    title = models.CharField(max_length=200)
    type_of = models.CharField(max_length=10, choices=WIDGET_TYPES)
    data_from = models.CharField(max_length=20)
    interval = models.CharField(max_length=20)
    nulls = models.CharField(max_length=20, choices=SHOW_NULLS,
                             null=False, blank=False, default='zeroize',
                             help_text="What to do with intervals that have"
                             " no data.<br/>'Omit' is advised for pie charts, "
                             "'Zeroize' is advised for all other widget types")
    data = models.ManyToManyField(
        WidgetData, blank=True, help_text="Data sources to pull from.<br/>"
        "'Last' metrics are advised for 'last' widgets. 'Sum' metrics are "
        "advised for all other widget types.<br/>")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, related_name='widget_created', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        User, related_name='widget_updated', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    user = property(lambda self: self.created_by)

    class Meta:
        verbose_name = 'widget'
        verbose_name_plural = 'widgets'

    def __str__(self):  # __unicode__ on Python 2
        return "%s (%s)" % (self.title, self.type_of)


@python_2_unicode_compatible
class Dashboard(models.Model):

    """ Base Dashboard config that Widgets are collected into
    """
    name = models.CharField(max_length=200)
    widgets = models.ManyToManyField(Widget, blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, related_name='dashboard_created', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        User, related_name='dashboard_updated', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    user = property(lambda self: self.created_by)

    def __str__(self):  # __unicode__ on Python 2
        return "%s" % self.name

    class Meta:
        verbose_name = 'dashboard'
        verbose_name_plural = 'dashboards'


@python_2_unicode_compatible
class UserDashboard(models.Model):

    """ Dashboards a user is interested in
    """
    # the seed auth api user this dashboard is a profile for
    user_id = models.IntegerField(null=False, blank=False)
    dashboards = models.ManyToManyField(Dashboard, related_name='dashboards')
    default_dashboard = models.ForeignKey(
        Dashboard, related_name='default', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, related_name='userdashboard_created', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        User, related_name='userdashboard_updated', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    user = property(lambda self: self.created_by)

    class Meta:
        verbose_name = 'user dashboard'
        verbose_name_plural = 'users dashboards'

    def __str__(self):  # __unicode__ on Python 2
        return "Dashboards for %s" % (self.user_id, )


@python_2_unicode_compatible
class Definition(models.Model):

    """ Definitions page
    """
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, related_name='definition_created', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        User, related_name='definition_updated', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    user = property(lambda self: self.created_by)

    def __str__(self):  # __unicode__ on Python 2
        return "%s" % self.title
