from datetime import datetime
from django.conf import settings
from django.db import models


class CoreModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Position(CoreModel):
    name = models.CharField(max_length=256, blank=False, unique=True)

    def __str__(self):
        return self.name

class Procedure(CoreModel):
    name = models.CharField(max_length=256, blank=False, unique=True)
    def __str__(self):
        return self.name

class Clinic(CoreModel):
    name = models.CharField(max_length=256, blank=False, unique=True)
    def __str__(self):
        return self.name

class City(CoreModel):
    name = models.CharField(max_length=256, blank=False, unique=True)
    def __str__(self):
        return self.name


class Treatment(CoreModel):
    date_start = models.DateTimeField(default=datetime.now)
    name = models.CharField(max_length=256, blank=False)
    days = models.IntegerField(blank=False)
    receipt = models.CharField(max_length=1024, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='treatments', on_delete=models.CASCADE,
                             blank=True, null=True)
    def __str__(self):
        return self.name

class Visit(CoreModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='visits', on_delete=models.CASCADE,
                             blank=True, null=True)
    date = models.DateTimeField(default=datetime.now)
    position = models.ForeignKey(Position, blank=True, null=True, on_delete=models.SET_NULL)
    doctor = models.CharField(max_length=256, blank=True)
    procedure = models.ForeignKey(Procedure, blank=True, null=True, on_delete=models.SET_NULL)
    procedure_details = models.CharField(max_length=1024, blank=True)
    clinic = models.ForeignKey(Clinic, blank=True, null=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.SET_NULL)
    document = models.FileField(upload_to='documents/', blank=True, null=True)
    link = models.CharField(max_length=1024, blank=True)
    comment = models.CharField(max_length=4096, blank=True)

    class Meta:
        ordering = ('-date', )

    def __str__(self):
        position = self.position and f' - {self.position.name}' or ''
        return f'{self.date.strftime("%d.%m.%Y")}{position} - {self.procedure.name}'
