from django.contrib import admin
from django.contrib.auth.models import User
from import_export import resources
from import_export.admin import ExportMixin
from image_cropping import ImageCroppingMixin

from manager.models import Organizer, Event, Attendee, Collaborator, Hardware, \
    Software, Installer, Installation, Room, ContactType, Contact, Activity, \
    ContactMessage, EventUser, InstallationMessage, Ticket, EventDate, AttendeeAttendanceDate, EventUserAttendanceDate
from manager.security import create_reporters_group


class EventoLAdmin(admin.ModelAdmin):
    def filter_event(self, events, queryset):
        return queryset.filter(event__in=events)

    def queryset(self, request):
        self.get_queryset(request)

    def get_queryset(self, request):
        queryset = super(EventoLAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return queryset
        reporters = create_reporters_group()
        if request.user.groups.filter(name=reporters.name).exists():
            return queryset
        organizers = Organizer.objects.filter(event_user__user=request.user)
        events = [organizer.event_user.event for organizer in organizers]
        if len(events) > 0:
            return self.filter_event(events, queryset)
        return queryset.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.is_superuser:
            return super(EventoLAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        events = [organizer.event_user.event for organizer in Organizer.objects.filter(event_user__user=request.user)]
        if db_field.name == "room":
            kwargs["queryset"] = Room.objects.filter(event__in=events).distinct()
        if db_field.name == "event":
            kwargs["queryset"] = Event.objects.filter(pk__in=[event.pk for event in events]).distinct()
        if db_field.name == "event_user":
            kwargs["queryset"] = EventUser.objects.filter(event__in=events).distinct()
        if db_field.name == "attendee":
            kwargs["queryset"] = Attendee.objects.filter(event__in=events).distinct()
        if db_field.name == "installer":
            kwargs["queryset"] = Installer.objects.filter(event_user__event__in=events).distinct()
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.none()
        return super(EventoLAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class EventoLEventUserAdmin(ExportMixin, EventoLAdmin):
    def filter_event(self, events, queryset):
        return queryset.filter(event_user__event__in=events)


class OrganizerResource(resources.ModelResource):
    class Meta(object):
        model = Organizer
        fields = ('event_user__user__first_name', 'event_user__user__last_name', 'event_user__user__username',
                  'event_user__user__email', 'event_user__user__date_joined')
        export_order = fields


class OrganizerAdmin(EventoLEventUserAdmin):
    resource_class = OrganizerResource


class EventUserResource(resources.ModelResource):
    class Meta(object):
        model = EventUser
        fields = (
            'user__first_name', 'user__last_name', 'user__username', 'user__email', 'user__date_joined')
        export_order = fields


class EventUserAdmin(ExportMixin, EventoLAdmin):
    resource_class = EventUserResource


class EventDateAdminInline(admin.TabularInline):
    model = EventDate


class EventAdmin(EventoLAdmin):
    inlines = [EventDateAdminInline]

    def filter_event(self, events, queryset):
        return queryset.filter(pk__in=[event.pk for event in events])


class InstallerResource(resources.ModelResource):
    class Meta(object):
        model = Installer
        fields = ('event_user__user__first_name', 'event_user__user__last_name', 'event_user__user__username',
                  'event_user__user__email', 'level', 'event_user__user__date_joined')
        export_order = fields


class InstallerAdmin(EventoLEventUserAdmin):
    resource_class = InstallerResource


class InstallationResource(resources.ModelResource):
    class Meta(object):
        model = Installation
        fields = ('hardware__type', 'hardware__manufacturer', 'hardware__model', 'software__type', 'software__name',
                  'attendee__email', 'installer__user__username', 'notes')
        export_order = fields


class InstallationAdmin(ExportMixin, EventoLAdmin):
    resource_class = InstallationResource

    def filter_event(self, events, queryset):
        return queryset.filter(installer__event__in=events)


class TicketResource(resources.ModelResource):
    class Meta(object):
        model = Ticket
        fields = ('sent',)
        export_order = fields


class TicketAdmin(EventoLAdmin):
    resource_class = TicketResource


class AttendeeResource(resources.ModelResource):
    class Meta(object):
        model = Attendee
        fields = ('first_name', 'last_name', 'nickname', 'email', 'email_confirmed', 'is_installing',
                  'additional_info', 'registration_date')
        export_order = fields


class AttendeeAdmin(ExportMixin, EventoLAdmin):
    resource_class = AttendeeResource


class ActivityResource(resources.ModelResource):
    class Meta(object):
        model = Activity


class ActivityAdmin(ImageCroppingMixin, ExportMixin, EventoLAdmin):
    resource_class = ActivityResource


class CollaboratorResource(resources.ModelResource):
    class Meta(object):
        model = Collaborator
        fields = ('event_user__user__first_name', 'event_user__user__last_name', 'event_user__user__username',
                  'event_user__user__email', 'event_user__user__date_joined', 'phone', 'address',
                  'assignation', 'time_availability', 'additional_info')
        export_order = fields


class CollaboratorAdmin(EventoLEventUserAdmin):
    resource_class = CollaboratorResource


admin.site.register(Event, EventAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(Organizer, OrganizerAdmin)
admin.site.register(Collaborator, CollaboratorAdmin)
admin.site.register(Hardware)
admin.site.register(Software)
admin.site.register(Installer, InstallerAdmin)
admin.site.register(Installation, InstallationAdmin)
admin.site.register(InstallationMessage, EventoLAdmin)
admin.site.register(Room, EventoLAdmin)
admin.site.register(ContactType)
admin.site.register(Contact, EventoLAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ContactMessage, EventoLAdmin)
admin.site.register(EventUser, EventUserAdmin)
admin.site.register(AttendeeAttendanceDate, EventoLAdmin)
admin.site.register(EventUserAttendanceDate, EventoLEventUserAdmin)
