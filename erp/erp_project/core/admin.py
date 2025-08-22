from django.contrib import admin
from .models import Company, Permission, Role, User, UserCompanyMembership, AuditLog

admin.site.register(Company)
admin.site.register(Permission)
admin.site.register(Role)
admin.site.register(User)
admin.site.register(UserCompanyMembership)
admin.site.register(AuditLog)
