import os
import pytz
import datetime
from django.contrib import admin
from django.utils.html import format_html
from .models import Position, Procedure, Treatment, Clinic, City, Visit


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    model = Position
    list_display = ['name']
    list_filter = ['name']


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    model = Procedure
    list_display = ['name']
    list_filter = ['name']


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    model = Clinic
    list_display = ['name']
    list_filter = ['name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    model = City
    list_display = ['name']
    list_filter = ['name']



@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    def status(obj):
        now = datetime.datetime.now(tz=pytz.UTC)
        days_passed = (now - obj.date_start).days
        if days_passed < obj.days:
            return '💊 В процесі'
        return '✅ Готово'
    status.short_description = 'Статус'

    model = Treatment
    list_display = ['date_start', 'days', 'receipt', 'name', 'user', status]
    list_filter = ['date_start', 'name', 'days',]


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    model = Visit
    list_display = ['user', 'date', 'position', 'procedure', 'clinic', 'procedure_details', 'city', 'file_preview']
    list_filter = ['user', 'date', 'position', 'procedure', 'clinic', 'city']

    def file_preview(self, obj):
        if obj.document:
            url = obj.document.url
            name, extension = os.path.splitext(obj.document.name)
            name = name.split('/')[-1]
            if extension in ('.jpg', '.jpeg', '.png'):
                return format_html(f'<a href="{url}" target="_blank"><img src="{url}" style="max-width: 100px; max-height: 100px;" /></a>')
            return format_html(f'<a href="{url}" target="_blank">{name}[{extension.upper()}]</a>')
        else:
            return 'No File'
    file_preview.short_description = 'File Preview'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_preview'] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
