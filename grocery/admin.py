from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Booking)
admin.site.register(Profile)
admin.site.register(Send_Feedback)
admin.site.register(Status)
admin.site.register(Cart)



from django.contrib import admin
from .models import Doctor

class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'fee', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

admin.site.register(Doctor, DoctorAdmin)
