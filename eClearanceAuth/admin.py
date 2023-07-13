from django.contrib import admin
from eClearanceAuth.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(UserType)
admin.site.register(Department)
admin.site.register(Session)
admin.site.register(Programme)
admin.site.register(StudentProfile)
admin.site.register(Office)
admin.site.register(AdministrativeProfile)
admin.site.register(InternalAuditClearance)
admin.site.register(StudentClearance)
admin.site.register(LibraryClearance)
admin.site.register(HostelClearance)
admin.site.register(SportClearance)
admin.site.register(DepartmentalClearance)
