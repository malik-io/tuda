import time

from .models.state import TrustLevel


class TrustEngine:
    """
    Trust is not time-based alone.
    It is quality-weighted and reversible.
    """

    USER_CONFIRMS_ANALYSIS = 2.0
    USER_CORRECTION_ADAPTED = 3.0
    FALSE_POSITIVE = 2.0
    OVERREACH_REJECTED = 5.0

    def __init__(self) -> None:
        self.score = 0.0
        self.last_decay_ts = time.time()

    def apply_positive_signal(self, weight: float = 1.0) -> None:
        self.score += weight

    def apply_negative_signal(self, weight: float = 1.0) -> None:
        self.score -= weight

    def decay(self) -> None:
        now = time.time()
        delta = now - self.last_decay_ts
        self.score -= delta * 0.0001
        self.last_decay_ts = now

    def resolve_trust_level(self) -> TrustLevel:
        self.decay()

        if self.score < 5:
            return TrustLevel.SEED
        if self.score < 20:
            return TrustLevel.PEER
        if self.score < 50:
            return TrustLevel.WARDEN
        return TrustLevel.INTEGRATED

    def record_user_confirmed_analysis(self) -> None:
        self.apply_positive_signal(self.USER_CONFIRMS_ANALYSIS)

    def record_user_correction_adapted(self) -> None:
        self.apply_positive_signal(self.USER_CORRECTION_ADAPTED)

    def record_false_positive(self) -> None:
        self.apply_negative_signal(self.FALSE_POSITIVE)

    def record_overreach_rejected(self) -> None:
        self.apply_negative_signal(self.OVERREACH_REJECTED)
