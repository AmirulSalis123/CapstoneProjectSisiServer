from ninja import Schema
from typing import Optional
from datetime import datetime
from typing import List
from django.contrib.auth.models import User

class UserOut(Schema):
    id: int
    email: str
    first_name: str
    last_name: str


class CourseSchemaOut(Schema):
    id: int
    name: str
    description: str
    price: int
    image : Optional[str]
    teacher: UserOut
    created_at: datetime
    updated_at: datetime

class CourseMemberOut(Schema):
    id: int 
    course_id: CourseSchemaOut
    user_id: UserOut
    roles: str


class CourseSchemaIn(Schema):
    name: str
    description: str
    price: int


class CourseContentMini(Schema):
    id: int
    name: str
    description: str
    course_id: CourseSchemaOut
    created_at: datetime
    updated_at: datetime


class CourseContentFull(Schema):
    id: int
    name: str
    description: str
    video_url: Optional[str]
    file_attachment: Optional[str]
    course_id: CourseSchemaOut
    created_at: datetime
    updated_at: datetime

class CourseCommentOut(Schema):
    id: int
    text: Optional[str]
    is_approved: bool
    content_id: CourseContentMini
    member_id: int
    user_email: str
    comment: str
    created_at: datetime
    updated_at: datetime

class CourseCommentIn(Schema):
    comment: str

class UserRegisterIn(Schema):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str

class BatchEnrollIn(Schema):
    course_id: int
    user_ids: List[int]

class ModerateCommentIn(Schema):
    comment_id: int
    is_approved: bool

class CourseMiniOut(Schema):
    id: int
    name: str

class UserActivityOut(Schema):
    user_id: int
    email: str
    joined_courses: list[CourseMiniOut]
    total_comments: int
    last_login: Optional[datetime]

class CourseAnalyticsOut(Schema):
    course_id: int
    course_name: str
    total_members: int
    total_contents: int
    total_comments: int
    approved_comments: int

class UserProfileUpdate(Schema):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    handphone: Optional[str]
    description: Optional[str]
    profile_picture: Optional[str]

class CompletionIn(Schema):
    content_id: int

class CompletionOut(Schema):
    content_id: int
    completed_at: datetime
