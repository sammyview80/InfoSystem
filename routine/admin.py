from django.contrib import admin

from .models import  Routine, Day, BatchSemester, Room, Group, AutoMatedRoutine, TeacherWithSubject,Period

admin.site.register(Routine)
admin.site.register(Day)
admin.site.register(BatchSemester)
admin.site.register(Room)
admin.site.register(Group)
admin.site.register(AutoMatedRoutine)
admin.site.register(TeacherWithSubject)
admin.site.register(Period)