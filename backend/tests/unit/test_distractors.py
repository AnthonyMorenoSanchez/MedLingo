import random

import pytest
from rapidfuzz.distance.Levenshtein import distance

from app.engine.distractors import choose


def test_distractors():
    got=choose("riñón",["vejiga","corazón","pulmón","riñones","vejiga","cerebro"],random.Random(1))
    assert len(set(got))==3
    assert all(distance(a,b)>=3 and a[:4]!=b[:4] for i,a in enumerate(["riñón",*got]) for b in ["riñón",*got][i+1:])
    with pytest.raises(ValueError):choose("riñón",["riñón"],random.Random(1))
