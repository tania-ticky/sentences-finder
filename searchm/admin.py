from django.contrib import admin
from searchm.models import Topic,Webpage,AccessRecord,User
admin.site.register(AccessRecord)
admin.site.register(Topic)
admin.site.register(Webpage)
admin.site.register(User)
