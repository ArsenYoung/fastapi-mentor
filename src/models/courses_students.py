import sqlalchemy as sa

from src.models.base import Base


courses_students = sa.Table(
    "courses_students",
    Base.metadata,
    sa.Column(
        "course_id",
        sa.ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "student_id",
        sa.ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
