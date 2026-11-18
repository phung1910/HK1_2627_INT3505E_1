"""Shared in-memory user data for Week 9 Lab 1 (URI Path Versioning)."""

USERS = {
    1: {
        "id": 1,
        "first_name": "Văn",
        "last_name": "Nguyễn",
        "email": "van.nguyen@example.com",
    },
    2: {
        "id": 2,
        "first_name": "An",
        "last_name": "Trần",
        "email": "an.tran@example.com",
    },
}


def get_user(uid: int):
    return USERS.get(uid)
