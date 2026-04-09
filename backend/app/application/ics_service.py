from datetime import timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event

from app.domain.entities import Visit
from app.domain.value_objects import BODY_REGION_LABELS

KYIV_TZ = ZoneInfo("Europe/Kyiv")
DEFAULT_DURATION = timedelta(hours=1)


def derive_summary(visit: Visit) -> str:
    parts = []
    if visit.procedure and visit.procedure.name:
        parts.append(visit.procedure.name)
    elif visit.position and visit.position.name:
        parts.append(visit.position.name)
    if visit.clinic and visit.clinic.name:
        parts.append(visit.clinic.name)
    return " — ".join(parts) if parts else "Візит"


def derive_location(visit: Visit) -> Optional[str]:
    parts = []
    if visit.clinic and visit.clinic.name:
        parts.append(visit.clinic.name)
    if visit.city and visit.city.name:
        parts.append(visit.city.name)
    return ", ".join(parts) if parts else None


def derive_description(visit: Visit) -> Optional[str]:
    lines = []
    if visit.doctor:
        lines.append(f"Лікар: {visit.doctor}")
    if visit.body_region:
        label = BODY_REGION_LABELS.get(visit.body_region, visit.body_region)
        lines.append(f"Область: {label}")
    if visit.comment:
        lines.append(visit.comment)
    return "\n".join(lines) if lines else None


def generate_ics(visit: Visit) -> bytes:
    cal = Calendar()
    cal.add("prodid", "-//MedTracker//EN")
    cal.add("version", "2.0")

    event = Event()
    event.add("uid", f"visit-{visit.id}@medtracker")
    event.add("summary", derive_summary(visit))

    dt_start = visit.date.astimezone(KYIV_TZ)
    event.add("dtstart", dt_start)
    event.add("dtend", dt_start + DEFAULT_DURATION)

    location = derive_location(visit)
    if location:
        event.add("location", location)

    description = derive_description(visit)
    if description:
        event.add("description", description)

    cal.add_component(event)
    return cal.to_ical()
