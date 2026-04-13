"""
Smart Study Schedule System ORM models.

This module keeps the application schema, SQLite setup helpers, and a small
smoke-test entrypoint in one place. Enum columns store their lowercase string
values so the ORM and Alembic migration share the same on-disk representation.
"""

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    event,
    func,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker, validates


def _new_uuid() -> str:
    return str(uuid.uuid4())


def _value_enum(enum_cls: type[enum.Enum]) -> Enum:
    """Persist enum values instead of enum member names."""
    return Enum(
        enum_cls,
        values_callable=lambda members: [str(member.value) for member in members],
        native_enum=False,
        validate_strings=True,
    )


class Base(DeclarativeBase):
    """Shared declarative base."""


class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ConfidenceRating(enum.IntEnum):
    """FSRS-compatible post-review rating scale."""

    AGAIN = 1
    HARD = 2
    GOOD = 3
    EASY = 4


class SyncStatus(str, enum.Enum):
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"


class BadgeSlug(str, enum.Enum):
    FIRST_REVIEW = "first_review"
    WEEK_WARRIOR = "week_warrior"
    HUNDRED_TOPICS = "hundred_topics"
    STREAK_7 = "streak_7"
    STREAK_30 = "streak_30"
    PERFECT_WEEK = "perfect_week"
    EARLY_BIRD = "early_bird"
    NIGHT_OWL = "night_owl"
    SPEED_LEARNER = "speed_learner"
    MASTER_MIND = "master_mind"


class NotificationType(str, enum.Enum):
    MORNING_SUMMARY = "morning_summary"
    OVERDUE_ALERT = "overdue_alert"
    EXAM_REMINDER = "exam_reminder"
    STREAK_WARNING = "streak_warning"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )


class SyncMixin:
    sync_status: Mapped[SyncStatus] = mapped_column(
        _value_enum(SyncStatus), default=SyncStatus.PENDING, nullable=False
    )
    device_id: Mapped[str] = mapped_column(String(64), nullable=True)
    last_synced_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class UserProfile(TimestampMixin, SyncMixin, Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    avatar_initials: Mapped[str] = mapped_column(String(3), nullable=True)
    xp_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_activity_date: Mapped[date] = mapped_column(Date, nullable=True)

    preferences: Mapped["UserPreferences"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    subjects: Mapped[list["Subject"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    study_sessions: Mapped[list["StudySession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    badges: Mapped[list["UserBadge"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    nlp_feedback: Mapped[list["NLPFeedback"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    theme: Mapped[str] = mapped_column(String(20), default="system", nullable=False)
    font_size_px: Mapped[int] = mapped_column(Integer, default=14, nullable=False)
    high_contrast: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notification_time: Mapped[str] = mapped_column(String(5), default="08:00", nullable=False)
    notify_morning_summary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_overdue_alert: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_exam_reminder_days: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    daily_goal_topics: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    default_session_minutes: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    pomodoro_break_minutes: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    cloud_sync_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    supabase_url: Mapped[str] = mapped_column(String(255), nullable=True)
    supabase_anon_key: Mapped[str] = mapped_column(String(255), nullable=True)
    last_full_sync_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user: Mapped["UserProfile"] = relationship(back_populates="preferences")

    __table_args__ = (
        CheckConstraint("font_size_px BETWEEN 10 AND 24", name="ck_font_size"),
        CheckConstraint("daily_goal_topics >= 1", name="ck_daily_goal"),
    )


class Subject(TimestampMixin, SyncMixin, Base):
    __tablename__ = "subjects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    color_tag: Mapped[str] = mapped_column(String(7), default="#7F77DD", nullable=False)
    exam_date: Mapped[date] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["UserProfile"] = relationship(back_populates="subjects")
    topics: Mapped[list["Topic"]] = relationship(
        back_populates="subject", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_subject_user_name"),
        Index("ix_subjects_user_id", "user_id"),
    )


class Topic(TimestampMixin, SyncMixin, Base):
    __tablename__ = "topics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    subject_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    parent_topic_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        _value_enum(DifficultyLevel), default=DifficultyLevel.MEDIUM, nullable=False
    )
    difficulty_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    difficulty_source: Mapped[str] = mapped_column(String(20), default="manual", nullable=False)
    completion_date: Mapped[date] = mapped_column(Date, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fsrs_stability: Mapped[float] = mapped_column(Float, nullable=True)
    fsrs_difficulty: Mapped[float] = mapped_column(Float, nullable=True)
    fsrs_due_date: Mapped[date] = mapped_column(Date, nullable=True)
    fsrs_last_review: Mapped[date] = mapped_column(Date, nullable=True)
    fsrs_review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    subject: Mapped["Subject"] = relationship(back_populates="topics")
    parent: Mapped["Topic"] = relationship(
        "Topic", remote_side="Topic.id", back_populates="children"
    )
    children: Mapped[list["Topic"]] = relationship("Topic", back_populates="parent")
    revisions: Mapped[list["Revision"]] = relationship(
        back_populates="topic", cascade="all, delete-orphan"
    )
    performance_logs: Mapped[list["PerformanceLog"]] = relationship(
        back_populates="topic", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("difficulty_score BETWEEN 0.0 AND 1.0", name="ck_difficulty_score"),
        Index("ix_topics_subject_id", "subject_id"),
        Index("ix_topics_fsrs_due_date", "fsrs_due_date"),
        Index("ix_topics_parent_topic_id", "parent_topic_id"),
    )

    @validates("difficulty")
    def _sync_difficulty_score(self, _key: str, value: DifficultyLevel) -> DifficultyLevel:
        mapping = {
            DifficultyLevel.EASY: 0.25,
            DifficultyLevel.MEDIUM: 0.5,
            DifficultyLevel.HARD: 0.85,
        }
        self.difficulty_score = mapping[value]
        return value


class StudySession(TimestampMixin, SyncMixin, Base):
    __tablename__ = "study_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    is_pomodoro: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pomodoro_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    topics_attempted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    topics_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_confidence: Mapped[float] = mapped_column(Float, nullable=True)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    user: Mapped["UserProfile"] = relationship(back_populates="study_sessions")
    revisions: Mapped[list["Revision"]] = relationship(back_populates="study_session")

    __table_args__ = (
        Index("ix_study_sessions_user_id", "user_id"),
        Index("ix_study_sessions_started_at", "started_at"),
        CheckConstraint("ended_at IS NULL OR ended_at >= started_at", name="ck_session_time_order"),
    )

    @property
    def hour_of_day(self) -> int:
        return self.started_at.hour

    @property
    def day_of_week(self) -> int:
        return self.started_at.weekday()


class Revision(TimestampMixin, SyncMixin, Base):
    __tablename__ = "revisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    topic_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    study_session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("study_sessions.id", ondelete="SET NULL"), nullable=True
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_missed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confidence_rating: Mapped[ConfidenceRating] = mapped_column(
        _value_enum(ConfidenceRating), nullable=True
    )
    time_spent_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    interval_days_before: Mapped[int] = mapped_column(Integer, nullable=True)
    interval_days_after: Mapped[int] = mapped_column(Integer, nullable=True)
    scheduled_days_overdue: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    scheduler_source: Mapped[str] = mapped_column(String(20), default="fsrs", nullable=False)

    topic: Mapped["Topic"] = relationship(back_populates="revisions")
    study_session: Mapped["StudySession"] = relationship(back_populates="revisions")

    __table_args__ = (
        Index("ix_revisions_topic_id", "topic_id"),
        Index("ix_revisions_scheduled_date", "scheduled_date"),
        Index("ix_revisions_completed_at", "completed_at"),
        CheckConstraint(
            "NOT (is_completed = 1 AND confidence_rating IS NULL)",
            name="ck_completed_needs_rating",
        ),
    )


class PerformanceLog(TimestampMixin, Base):
    __tablename__ = "performance_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    topic_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    revision_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("revisions.id", ondelete="CASCADE"), nullable=False
    )
    days_since_last_review: Mapped[int] = mapped_column(Integer, nullable=True)
    review_count_at_time: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty_score_at_time: Mapped[float] = mapped_column(Float, nullable=False)
    scheduled_days_overdue: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hour_of_day: Mapped[int] = mapped_column(Integer, nullable=True)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=True)
    confidence_rating: Mapped[ConfidenceRating] = mapped_column(
        _value_enum(ConfidenceRating), nullable=False
    )
    predicted_confidence: Mapped[float] = mapped_column(Float, nullable=True)
    scheduler_source: Mapped[str] = mapped_column(String(20), nullable=False)

    topic: Mapped["Topic"] = relationship(back_populates="performance_logs")

    __table_args__ = (
        Index("ix_perf_log_topic_id", "topic_id"),
        Index("ix_perf_log_created_at", "created_at"),
    )


class NLPFeedback(TimestampMixin, Base):
    __tablename__ = "nlp_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    topic_name_raw: Mapped[str] = mapped_column(Text, nullable=False)
    predicted_difficulty: Mapped[DifficultyLevel] = mapped_column(
        _value_enum(DifficultyLevel), nullable=False
    )
    predicted_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    actual_difficulty: Mapped[DifficultyLevel] = mapped_column(
        _value_enum(DifficultyLevel), nullable=False
    )
    used_for_retraining: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["UserProfile"] = relationship(back_populates="nlp_feedback")

    __table_args__ = (
        Index("ix_nlp_feedback_user_id", "user_id"),
        Index("ix_nlp_feedback_retrain", "used_for_retraining"),
    )


class UserBadge(TimestampMixin, Base):
    __tablename__ = "user_badges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    badge_slug: Mapped[BadgeSlug] = mapped_column(_value_enum(BadgeSlug), nullable=False)
    awarded_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    xp_granted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["UserProfile"] = relationship(back_populates="badges")

    __table_args__ = (
        UniqueConstraint("user_id", "badge_slug", name="uq_user_badge"),
        Index("ix_user_badges_user_id", "user_id"),
    )


class NotificationLog(TimestampMixin, Base):
    __tablename__ = "notification_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        _value_enum(NotificationType), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    was_clicked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_notif_log_user_id", "user_id"),
        Index("ix_notif_log_sent_at", "sent_at"),
    )


def _configure_sqlite_connection(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
    except Exception:
        pass
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


def get_engine(db_path: str = "smart_study.db") -> Engine:
    """Create the app SQLite engine with SQLite-specific pragmas enabled."""
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    event.listen(engine, "connect", _configure_sqlite_connection)
    return engine


def init_db(engine: Engine) -> None:
    """Create all tables if they do not exist yet."""
    Base.metadata.create_all(engine)


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return the configured SQLAlchemy session factory."""
    return sessionmaker(bind=engine, autoflush=True, expire_on_commit=False)


if __name__ == "__main__":
    engine = get_engine(":memory:")
    init_db(engine)

    SessionFactory = get_session_factory(engine)
    with SessionFactory() as session:
        user = UserProfile(display_name="Harshvardhan", avatar_initials="HVR")
        prefs = UserPreferences(user=user, daily_goal_topics=8, theme="dark")
        subject = Subject(user=user, name="Mathematics", color_tag="#534AB7")
        chapter = Topic(subject=subject, name="Calculus", difficulty=DifficultyLevel.HARD)
        leaf1 = Topic(
            subject=subject,
            parent=chapter,
            name="Limits and Continuity",
            difficulty=DifficultyLevel.MEDIUM,
        )
        leaf2 = Topic(
            subject=subject,
            parent=chapter,
            name="Derivatives",
            difficulty=DifficultyLevel.HARD,
        )
        session.add_all([user, prefs, subject, chapter, leaf1, leaf2])
        session.commit()

        loaded = session.get(Topic, chapter.id)
        print(f"Chapter: {loaded.name}")
        for child in loaded.children:
            print(f"  - {child.name} difficulty={child.difficulty.value} score={child.difficulty_score}")

    print("All tables created and sample data inserted successfully.")
