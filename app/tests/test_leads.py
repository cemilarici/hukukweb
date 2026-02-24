from datetime import UTC, datetime

from app.cms import append_lead
from app.models import LeadEntry


def test_lead_append(isolated_data):
    entry = LeadEntry(
        timestamp=datetime.now(UTC),
        ip="127.0.0.1",
        user_agent="pytest",
        name="Test User",
        email="test@example.com",
        phone="",
        message="Merhaba dunya",
    )
    path = append_lead(entry)

    assert path.exists()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert "test@example.com" in lines[0]
