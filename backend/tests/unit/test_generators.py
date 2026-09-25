import pytest

from app.engine.generators import REGISTRY
from app.schemas.questions import Payload


@pytest.mark.parametrize("kind",[k for k in REGISTRY if k!="encounter"])
@pytest.mark.parametrize("direction",["en2es","es2en"])
def test_generator(kind,direction):
    source={"id":1,"en":"kidney","es":"riñón","gender_es":"m"}
    args=(source,direction,"fingerprint",["vejiga","cerebro","estómago","lung","brain","stomach"])
    a=REGISTRY[kind]().generate(*args)
    assert a==REGISTRY[kind]().generate(*args)
    assert Payload.model_validate(a).giveup["answer_display"]

def test_encounter():
    source={"id":"n1","encounter_id":"test","patient_es":"Me duele.","patient_en":"It hurts.","options":[{"id":"a","es":"¿Dónde?","en":"Where?","correct":True,"feedback_en":"Clarify."}]}
    p=REGISTRY["encounter"]().generate(source,"en2es","fingerprint",[])
    assert p["correct_id"]=="a"
