from django.contrib import admin
from lms_core.models import Course, CourseMember, CourseContent, Comment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "description", "teacher", 'created_at']
    list_filter = ["teacher"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]

@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "course_id", "parent_id", "created_at"]
    search_fields = ["name"]
    list_filter = ["course_id"]

@admin.register(CourseMember)
class CourseMemberAdmin(admin.ModelAdmin):
    list_display = ["id", "course_id", "user_id", "roles", "created_at"]
    list_filter = ["roles", "course_id"]
    search_fields = ["user_id__username"]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "content", "member", "text", "is_approved", "created_at"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["text"]
    readonly_fields = ["created_at", "updated_at"]
