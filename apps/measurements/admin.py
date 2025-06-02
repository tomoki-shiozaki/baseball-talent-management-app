from django.contrib import admin

from apps.measurements.models import Measurement, MeasurementApproval

# Register your models here.
admin.site.register(Measurement)
admin.site.register(MeasurementApproval)
