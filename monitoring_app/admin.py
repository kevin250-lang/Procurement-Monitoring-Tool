from django.contrib import admin
from monitoring_app.models import *

# Register your models here.

admin.site.register(Tender)
admin.site.register(Procurement_doc)
admin.site.register(user_contact)
admin.site.register(Department)
admin.site.register(Method)
admin.site.register(Stage)
admin.site.register(Procedure)
admin.site.register(Duration)
admin.site.register(Overall_stages)
admin.site.register(Overall_method)
admin.site.register(Overall_department)
admin.site.register(Company)
admin.site.register(Plan_tenders_report)
admin.site.register(Tender_republished)
