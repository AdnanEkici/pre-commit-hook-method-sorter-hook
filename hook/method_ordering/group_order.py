from __future__ import annotations

METHOD_GROUP_ORDER: dict[str, int] = {
    "dunder": 0,
    "property": 1,
    "abstract_public": 2,
    "abstract_protected": 3,
    "abstract_private": 4,
    "decorated_public": 5,
    "decorated_protected": 6,
    "decorated_private": 7,
    "public": 8,
    "protected": 9,
    "private": 10,
    "unknown": 999,
}
