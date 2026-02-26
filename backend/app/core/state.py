from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class AppState:
    started_at: datetime = datetime.now(timezone.utc)


app_state = AppState()

