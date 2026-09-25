import json

from app.config import ROOT
from app.engine.normalize import check, normalize


def test_shared():
    for original,expected in json.loads((ROOT/"tests/shared/normalize_cases.json").read_text()):assert normalize(original)==expected

def test_results():
    assert check("rinon",["riñón"])==("correct","accents")
    assert check("glóbulo rojoo",["glóbulo rojo"])[1]=="near_miss"
    assert check("bladder",["vejiga"])[0]=="wrong"
    assert check("la vejiga",["vejiga"])[0]=="correct"
    assert check("vejiga",["la vejiga"],True)[0]=="wrong"
