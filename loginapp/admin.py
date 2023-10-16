from django.contrib import admin
from .models import Test
# Register your models here.

@admin.register(Test)
class UserAdmin(admin.ModelAdmin):
    #顯示相應字段
    list_display = [
        'id',
        'name',
        'age',
        'info',
        'sex',
        'create_time'
    ]
    #將字段設定為只讀
    readonly_fields = ['create_time']
    #添加過濾器
    list_filter = ('sex',)
    #搜索
    search_fields = ['name','info']
    #排序
    ordering = ['id']#正序
    # ordering = ['-id']#倒序
    #分頁
    list_per_page = 2

