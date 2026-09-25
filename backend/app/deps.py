from fastapi import Request

from app.db import db


def user_session(request: Request):
    with db(request.app) as conn:
        yield conn

def seed_session(request: Request):
    with db(request.app, seed=True) as conn:
        yield conn

def current_profile():
    return 1
