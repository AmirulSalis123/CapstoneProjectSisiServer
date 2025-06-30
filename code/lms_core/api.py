from ninja import NinjaAPI, UploadedFile, File, Form
from ninja.responses import Response
from lms_core.schema import (
  CourseSchemaOut, CourseMemberOut, CourseSchemaIn, 
  CourseContentMini, CourseContentFull, CourseCommentOut, 
  CourseCommentIn, UserRegisterIn, BatchEnrollIn, 
  ModerateCommentIn, UserActivityOut, CourseAnalyticsOut, 
  UserProfileUpdate, CompletionIn, CompletionOut
)
from lms_core.models import (
  CourseMember, Course, CourseContent, Comment
)
from ninja_simple_jwt.auth.views.api import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
from ninja.pagination import paginate, PageNumberPagination
from ninja.errors import HttpError
from typing import List
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from django.contrib.auth.models import User

apiv1 = NinjaAPI()
apiv1.add_router("/auth/", mobile_auth_router)
apiAuth = HttpJwtAuth()

@apiv1.post("/register")
def register_user(request, payload: UserRegisterIn):
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Username sudah digunakan")
    if User.objects.filter(email=payload.email).exists():
        return Response({"error": "Email sudah digunakan"}, status=400)

    user = User.objects.create_user(
        username=payload.username,
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        password=payload.password
    )
    return {"message": "User berhasil didaftarkan", "user_id": user.id}

@apiv1.post("/course/batch-enroll", auth=apiAuth)
def batch_enroll(request, payload: BatchEnrollIn):
    try:
        course = Course.objects.get(id=payload.course_id)
    except Course.DoesNotExist:
        return Response({"error": "Kursus tidak ditemukan"}, status=404)

    enrolled = []
    skipped = []

    current_count = CourseMember.objects.filter(course_id=course.id).count()
    remaining_slots = course.max_students - current_count

    for user_id in payload.user_ids:
        if remaining_slots <= 0:
            break

        if not CourseMember.objects.filter(course_id=course.id, user_id=user_id).exists():
            CourseMember.objects.create(
                course_id=course,
                user_id=User.objects.get(id=user_id)
            )
            enrolled.append(user_id)
            remaining_slots -= 1
        else:
            skipped.append(user_id)

    return {
        "message": "Proses enroll selesai",
        "enrolled_users": enrolled,
        "already_enrolled": skipped,
        "remaining_quota": full
    }


@apiv1.post("/comment/moderate", auth=apiAuth)
def moderate_comment(request, payload: ModerateCommentIn):
    try:
        comment = Comment.objects.get(id=payload.comment_id)
    except Comment.DoesNotExist:
        raise HttpError(404, "Komentar tidak ditemukan")

    if comment.content_id.course_id.teacher != request.user:
        raise HttpError(403, "Bukan pemilik course")

    comment.is_approved = payload.is_approved
    comment.save()
    return {"message": "Komentar diperbarui"}

@apiv1.get("/comments/{content_id}")
def get_comments(request, content_id: int):
    comments = Comment.objects.filter(content_id=content_id, is_approved=True)
    result = []
    for c in comments:
        result.append({
            "id": c.id,
            "text": c.text,
            "is_approved": c.is_approved,
            "content_id": c.content.id,
            "member_id": c.member.id,
            "user_email": c.member.user_id.email,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        })
    return result

@apiv1.get("/user/activity", auth=apiAuth, response=UserActivityOut)
def get_user_activity(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"detail": "Unauthorized"}, status=401)

    memberships = CourseMember.objects.filter(user_id=user)
    joined_courses = [m.course_id for m in memberships]

    comments = Comment.objects.filter(member__user_id=user)
    total_comments = comments.count()

    return {
        "user_id": user.id,
        "email": user.email,
        "joined_courses": joined_courses,
        "total_comments": total_comments,
        "last_login": user.last_login,
    }

@apiv1.get("/course/analytics", response=List[CourseAnalyticsOut], auth=apiAuth)
def course_analytics(request):
    user = request.user
    courses = Course.objects.filter(teacher=user)
    
    result = []
    for course in courses:
        contents = CourseContent.objects.filter(course_id=course)
        content_ids = contents.values_list("id", flat=True)
        comments = Comment.objects.filter(content_id__in=content_ids)

        result.append({
            "course_id": course.id,
            "course_name": course.name,
            "total_members": CourseMember.objects.filter(course_id=course).count(),
            "total_contents": contents.count(),
            "total_comments": comments.count(),
            "approved_comments": comments.filter(is_approved=True).count()
        })
    return result

@apiv1.get("/course/{course_id}/available-contents", response=List[CourseContentMini])
def list_available_contents(request, course_id: int):
    now = timezone.now()
    contents = CourseContent.objects.filter(course_id=course_id, available_at__lte=now)
    return contents

@apiv1.post("/course/{course_id}/complete", auth=apiAuth)
def complete_course(request, course_id: int):
    try:
        member = CourseMember.objects.get(course_id=course_id, user_id=request.user)
        member.is_completed = True
        member.save()
        return {"message": "Kursus ditandai selesai"}
    except CourseMember.DoesNotExist:
        raise HttpError(404, "Anda belum mendaftar di kursus ini")

@apiv1.get("/course/{course_id}/certificate", auth=apiAuth)
def get_certificate(request, course_id: int):
    try:
        member = CourseMember.objects.get(course_id=course_id, user_id=request.user)
        if not member.is_completed:
            return Response({"error": "Kursus belum diselesaikan"}, status=400)
        
        html_content = render_to_string("certificate.html", {
            "user": request.user,
            "course": member.course_id,
            "date": timezone.now()
        })
        return HttpResponse(html_content)
    except CourseMember.DoesNotExist:
        raise HttpError(404, "Data tidak ditemukan")

@apiv1.get("/user/{user_id}/profile", auth=apiAuth)
def show_profile(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
        courses_joined = CourseMember.objects.filter(user_id=user).values_list('course_id__name', flat=True)
        courses_created = Course.objects.filter(teacher=user).values_list('name', flat=True)
        user_profile = user.userprofile

        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "handphone": getattr(user, "handphone", ""),
            "description": getattr(user, "description", ""),
            "profile_picture": getattr(user, "profile_picture", ""),
            "courses_joined": list(courses_joined),
            "courses_created": list(courses_created),
        }
    except User.DoesNotExist:
        raise HttpError(404, "Pengguna tidak ditemukan")

@apiv1.put("/user/profile", auth=apiAuth)
def edit_profile(request, data: UserProfileUpdate):
    user = request.user

    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    user.save()

    return {"message": "Profil berhasil diperbarui"}

@apiv1.post("/completion", auth=apiAuth)
def mark_completed(request, payload: CompletionIn):
    try:
        content = CourseContent.objects.get(id=payload.content_id)
        member = CourseMember.objects.get(course_id=content.course_id, user_id=request.user)

        # Cegah duplikasi
        ContentCompletion.objects.get_or_create(member=member, content=content)
        return {"message": "Content ditandai selesai"}
    except (CourseContent.DoesNotExist, CourseMember.DoesNotExist):
        raise HttpError(404, "Data tidak ditemukan")

@apiv1.get("/completion/{course_id}", auth=apiAuth, response=List[CompletionOut])
def list_completion(request, course_id: int):
    try:
        member = CourseMember.objects.get(course_id=course_id, user_id=request.user)
        completions = ContentCompletion.objects.filter(member=member)
        return completions
    except CourseMember.DoesNotExist:
        raise HttpError(404, "Kamu belum ikut kursus ini")

@apiv1.delete("/completion/{content_id}", auth=apiAuth)
def delete_completion(request, content_id: int):
    try:
        content = CourseContent.objects.get(id=content_id)
        member = CourseMember.objects.get(course_id=content.course_id, user_id=request.user)
        completion = ContentCompletion.objects.get(member=member, content=content)
        completion.delete()
        return {"message": "Data completion dihapus"}
    except (CourseContent.DoesNotExist, CourseMember.DoesNotExist, ContentCompletion.DoesNotExist):
        raise HttpError(404, "Data tidak ditemukan")

@apiv1.get("/course/{course_id}/completion-progress", auth=apiAuth)
def completion_progress(request, course_id: int):
    try:
        member = CourseMember.objects.get(course_id=course_id, user_id=request.user)
        total_contents = CourseContent.objects.filter(course_id=course_id).count()
        completed = ContentCompletion.objects.filter(member=member).count()

        percent = (completed / total_contents * 100) if total_contents > 0 else 0
        return {
            "total_contents": total_contents,
            "completed": completed,
            "progress_percent": round(percent, 2)
        }
    except CourseMember.DoesNotExist:
        raise HttpError(404, "Kamu belum ikut kursus ini")
