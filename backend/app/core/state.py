from dataclasses import dataclass
from datetime import datetime, UTC


@dataclass
class AppState:
    started_at: datetime = datetime.now(UTC)


app_state = AppState()
