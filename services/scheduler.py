from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from math import ceil

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import ConfidenceRating, PerformanceLog, Revision, Topic
from services.forgetting_curve import ForgettingCurveModel

RATING_TO_SCORE: dict[ConfidenceRating, int] = {
    ConfidenceRating.AGAIN: 1,
    ConfidenceRating.HARD: 2,
    ConfidenceRating.GOOD: 3,
    ConfidenceRating.EASY: 4,
}

RATING_TO_STABILITY_FACTOR: dict[ConfidenceRating, float] = {
    ConfidenceRating.AGAIN: 0.55,
    ConfidenceRating.HARD: 1.15,
    ConfidenceRating.GOOD: 1.65,
    ConfidenceRating.EASY: 2.2,
}

RATING_TO_DIFFICULTY_DELTA: dict[ConfidenceRating, float] = {
    ConfidenceRating.AGAIN: 0.12,
    ConfidenceRating.HARD: 0.05,
    ConfidenceRating.GOOD: -0.04,
    ConfidenceRating.EASY: -0.09,
}

INITIAL_STABILITY_BY_DIFFICULTY: dict[str, float] = {
    "easy": 1.6,
    "medium": 1.1,
    "hard": 0.8,
}

INITIAL_INTERVAL_BY_DIFFICULTY: dict[str, int] = {
    "easy": 2,
    "medium": 1,
    "hard": 1,
}
MAX_INTERVAL_DAYS = 365


@dataclass(frozen=True)
class FsrsSnapshot:
    stability: float
    difficulty: float
    next_interval_days: int


class SchedulerService:
    def __init__(
        self,
        session: Session,
        today_provider: callable | None = None,
        forgetting_curve_model: ForgettingCurveModel | None = None,
    ) -> None:
        self.session = session
        self._today_provider = today_provider or date.today
        self.forgetting_curve_model = forgetting_curve_model or ForgettingCurveModel(session)

    def _today(self) -> date:
        return self._today_provider()

    def get_due_today(self, *, for_date: date | None = None) -> list[Revision]:
        current_date = for_date or self._today()
        stmt = (
            select(Revision)
            .where(Revision.is_completed.is_(False), Revision.scheduled_date == current_date)
            .order_by(Revision.scheduled_date, Revision.created_at)
        )
        return list(self.session.scalars(stmt))

    def get_overdue(self, *, for_date: date | None = None) -> list[Revision]:
        current_date = for_date or self._today()
        stmt = (
            select(Revision)
            .where(Revision.is_completed.is_(False), Revision.scheduled_date < current_date)
            .order_by(Revision.scheduled_date, Revision.created_at)
        )
        return list(self.session.scalars(stmt))

    def schedule_new_topic(self, topic_id: str, *, scheduled_for: date | None = None) -> Revision:
        topic = self._require_topic(topic_id)
        if self._active_revision_for_topic(topic_id) is not None:
            raise ValueError(f"Topic {topic_id} already has an active scheduled revision")

        start_date = scheduled_for or self._today()
        initial_interval = INITIAL_INTERVAL_BY_DIFFICULTY[topic.difficulty.value]
        initial_stability = INITIAL_STABILITY_BY_DIFFICULTY[topic.difficulty.value]
        initial_difficulty = self._normalize_difficulty(topic)

        topic.fsrs_stability = initial_stability
        topic.fsrs_difficulty = initial_difficulty
        topic.fsrs_last_review = None
        topic.fsrs_review_count = 0
        topic.fsrs_due_date = start_date

        revision = Revision(
            topic_id=topic.id,
            scheduled_date=start_date,
            interval_days_before=0,
            interval_days_after=initial_interval,
            scheduler_source="fsrs",
        )
        self.session.add(revision)
        self.session.flush()
        return revision

    def record_revision(
        self,
        revision_id: str,
        *,
        rating: ConfidenceRating,
        completed_at: datetime | None = None,
    ) -> Revision:
        revision = self._require_revision(revision_id)
        topic = revision.topic
        finished_at = completed_at or datetime.combine(self._today(), time(9, 0, 0))
        review_day = finished_at.date()

        days_since_last_review = self._days_since_last_review(topic, review_day)
        snapshot = self._next_fsrs_snapshot(
            topic=topic,
            rating=rating,
            scheduled_days_overdue=max((review_day - revision.scheduled_date).days, 0),
            days_since_last_review=days_since_last_review,
        )

        revision.is_completed = True
        revision.is_missed = False
        revision.completed_at = finished_at
        revision.confidence_rating = rating
        revision.interval_days_before = self._previous_interval_days(topic)
        revision.scheduled_days_overdue = max((review_day - revision.scheduled_date).days, 0)

        user_id = topic.subject.user_id
        self.forgetting_curve_model.train_if_needed(user_id)
        personal_features = self.forgetting_curve_model.build_features_for_topic(
            topic=topic,
            days_since_review=days_since_last_review,
            time_of_day=finished_at.hour,
        )
        personalized_interval = self.forgetting_curve_model.predict_interval(
            user_id=user_id,
            fsrs_interval=snapshot.next_interval_days,
            features=personal_features,
        )
        chosen_interval = personalized_interval or snapshot.next_interval_days
        revision.interval_days_after = chosen_interval
        revision.fsrs_interval_days = snapshot.next_interval_days
        revision.personalized_interval_days = personalized_interval

        topic.fsrs_stability = snapshot.stability
        topic.fsrs_difficulty = snapshot.difficulty
        topic.fsrs_last_review = review_day
        topic.fsrs_review_count += 1
        topic.fsrs_due_date = review_day.fromordinal(review_day.toordinal() + chosen_interval)

        self.session.add(
            PerformanceLog(
                topic_id=topic.id,
                revision_id=revision.id,
                days_since_last_review=days_since_last_review,
                review_count_at_time=topic.fsrs_review_count,
                difficulty_score_at_time=topic.difficulty_score,
                scheduled_days_overdue=revision.scheduled_days_overdue,
                hour_of_day=finished_at.hour,
                day_of_week=finished_at.weekday(),
                confidence_rating=rating,
                predicted_confidence=RATING_TO_SCORE[rating] / 4,
                scheduler_source="personalized" if personalized_interval is not None else "fsrs",
            )
        )

        next_revision = Revision(
            topic_id=topic.id,
            scheduled_date=topic.fsrs_due_date,
            interval_days_before=chosen_interval,
            interval_days_after=chosen_interval,
            fsrs_interval_days=snapshot.next_interval_days,
            personalized_interval_days=personalized_interval,
            scheduler_source="personalized" if personalized_interval is not None else "fsrs",
        )
        self.session.add(next_revision)
        self.session.flush()
        self.forgetting_curve_model.train_if_needed(user_id)
        return next_revision

    def reschedule_after_miss(
        self,
        revision_id: str,
        *,
        reschedule_from: date | None = None,
    ) -> Revision:
        revision = self._require_revision(revision_id)
        topic = revision.topic
        current_date = reschedule_from or self._today()
        overdue_days = max((current_date - revision.scheduled_date).days, 0)

        revision.is_missed = True
        revision.scheduled_days_overdue = overdue_days

        current_stability = topic.fsrs_stability or INITIAL_STABILITY_BY_DIFFICULTY[topic.difficulty.value]
        penalized_stability = max(current_stability * max(0.45, 1 - overdue_days * 0.08), 0.35)
        topic.fsrs_stability = penalized_stability
        topic.fsrs_due_date = current_date

        self.session.add(
            PerformanceLog(
                topic_id=topic.id,
                revision_id=revision.id,
                days_since_last_review=self._days_since_last_review(topic, current_date),
                review_count_at_time=topic.fsrs_review_count,
                difficulty_score_at_time=topic.difficulty_score,
                scheduled_days_overdue=overdue_days,
                hour_of_day=None,
                day_of_week=current_date.weekday(),
                confidence_rating=ConfidenceRating.AGAIN,
                predicted_confidence=0.25,
                scheduler_source="missed_review",
            )
        )
        self.session.flush()
        return revision

    def _next_fsrs_snapshot(
        self,
        *,
        topic: Topic,
        rating: ConfidenceRating,
        scheduled_days_overdue: int,
        days_since_last_review: int,
    ) -> FsrsSnapshot:
        current_stability = topic.fsrs_stability or INITIAL_STABILITY_BY_DIFFICULTY[topic.difficulty.value]
        current_difficulty = topic.fsrs_difficulty or self._normalize_difficulty(topic)

        overdue_penalty = max(0.55, 1 - scheduled_days_overdue * 0.08)
        retrievability_bonus = 1 + min(days_since_last_review, 10) * 0.03
        stability = max(
            current_stability * RATING_TO_STABILITY_FACTOR[rating] * overdue_penalty * retrievability_bonus,
            0.35,
        )
        difficulty = min(max(current_difficulty + RATING_TO_DIFFICULTY_DELTA[rating], 0.1), 0.95)

        interval = min(MAX_INTERVAL_DAYS, max(1, ceil(stability * (1.4 - difficulty))))
        return FsrsSnapshot(stability=round(stability, 3), difficulty=round(difficulty, 3), next_interval_days=interval)

    def _normalize_difficulty(self, topic: Topic) -> float:
        if topic.fsrs_difficulty is not None:
            return topic.fsrs_difficulty
        return min(max(topic.difficulty_score or 0.5, 0.1), 0.95)

    def _previous_interval_days(self, topic: Topic) -> int:
        if topic.fsrs_last_review and topic.fsrs_due_date:
            return max((topic.fsrs_due_date - topic.fsrs_last_review).days, 0)
        return 0

    def _days_since_last_review(self, topic: Topic, current_date: date) -> int:
        if topic.fsrs_last_review is None:
            return 0
        return max((current_date - topic.fsrs_last_review).days, 0)

    def _active_revision_for_topic(self, topic_id: str) -> Revision | None:
        stmt = (
            select(Revision)
            .where(Revision.topic_id == topic_id, Revision.is_completed.is_(False))
            .order_by(Revision.scheduled_date)
        )
        return self.session.scalars(stmt).first()

    def _require_topic(self, topic_id: str) -> Topic:
        topic = self.session.get(Topic, topic_id)
        if topic is None:
            raise ValueError(f"Topic {topic_id} does not exist")
        return topic

    def _require_revision(self, revision_id: str) -> Revision:
        revision = self.session.get(Revision, revision_id)
        if revision is None:
            raise ValueError(f"Revision {revision_id} does not exist")
        return revision
