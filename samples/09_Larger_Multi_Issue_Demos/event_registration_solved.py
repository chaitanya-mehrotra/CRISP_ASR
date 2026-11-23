"""Event registration classroom fixture. Importing this file runs no demo."""

import json
import random
import string
import tempfile
from dataclasses import dataclass

import yaml


TICKET_ALPHABET = string.ascii_letters + string.digits
MAX_INPUT_LENGTH = 20_000


@dataclass(frozen=True)
class Event:
    title: str
    capacity: int
    location: str


@dataclass(frozen=True)
class Registration:
    name: str
    email: str
    ticket_token: str


def read_event_config(text: str) -> Event:
    if len(text) > MAX_INPUT_LENGTH:
        raise ValueError("Event configuration is too long")
    config = yaml.safe_load(text)
    if not isinstance(config, dict):
        raise ValueError("Expected a configuration object")

    title = config.get("title")
    capacity = config.get("capacity")
    location = config.get("location", "Main hall")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Missing event title")
    if type(capacity) is not int or not 1 <= capacity <= 1_000:
        raise ValueError("Capacity must be between 1 and 1,000")
    if not isinstance(location, str):
        raise ValueError("Invalid event location")
    return Event(title.strip(), capacity, location.strip())


def read_attendee_data(payload: str) -> tuple[str, str]:
    if len(payload) > MAX_INPUT_LENGTH:
        raise ValueError("Attendee data is too long")
    record = json.loads(payload)
    if not isinstance(record, dict):
        raise ValueError("Expected an attendee object")

    name = record.get("name")
    email = record.get("email")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Missing attendee name")
    if not isinstance(email, str) or "@" not in email:
        raise ValueError("Missing attendee email")
    return name.strip(), email.strip().lower()


def make_ticket_token() -> str:
    return "".join(random.SystemRandom().choices(TICKET_ALPHABET, k=32))


def register(event: Event, payloads: list[str]) -> list[Registration]:
    if len(payloads) > event.capacity:
        raise ValueError("Event capacity exceeded")
    registrations = []
    seen_emails = set()
    for payload in payloads:
        name, email = read_attendee_data(payload)
        if email in seen_emails:
            raise ValueError("Duplicate email")
        seen_emails.add(email)
        registrations.append(Registration(name, email, make_ticket_token()))
    return registrations


def render_roster(event: Event, registrations: list[Registration]) -> str:
    lines = [event.title, f"Location: {event.location}", f"Registrations: {len(registrations)}"]
    lines.extend(f"{index}. {entry.name}" for index, entry in enumerate(registrations, 1))
    return "\n".join(lines) + "\n"


def round_trip_roster(roster: str) -> str:
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as handle:
        handle.write(roster)
        handle.seek(0)
        return handle.read()


def build_roster(config_text: str, payloads: list[str]) -> str:
    event = read_event_config(config_text)
    return round_trip_roster(render_roster(event, register(event, payloads)))
