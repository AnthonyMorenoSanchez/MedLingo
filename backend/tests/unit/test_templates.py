import pytest

from app.engine.templates import TemplateRenderError, plural, render


@pytest.mark.parametrize("word,gender,number,det,indef,adj",[("mano","f","sg","la","una","inflamada"),("ojo","m","sg","el","un","inflamado"),("manos","f","pl","las","unas","inflamadas"),("ojos","m","pl","los","unos","inflamados"),("agua","f","sg","el","un","inflamada")])
def test_agreement(word,gender,number,det,indef,adj):
    slots={"X":{"es":word,"en":"word","gender_es":gender,"number_es":number}}
    assert render("{DET:X} {X} {ADJ:X:inflamado}",slots)==f"{det} {word} {adj}"
    assert render("{INDEF:X}",slots)==indef
    assert render("{X}",slots,"en")=="word"

def test_plural_errors():
    assert plural("luz")=="luces"
    assert plural("dolor")=="dolores"
    assert render("{PL:X}",{"X":{"es":"luz"}})=="luces"
    with pytest.raises(TemplateRenderError):render("{DET:X}",{"X":{"es":"unknown"}})
    with pytest.raises(TemplateRenderError):render("{BAD:X}",{"X":{"es":"ojo","gender_es":"m"}})

def test_multislot_selection():
    from app.engine.templates import expand_slots
    template={'specialty':'urology','slots':{'SYMPTOM':{'type':'symptom'},'ACTION':{'type':'fixed','options':[{'en':'urinate','es':'orina'}]}}}
    groups={'urology':[{'en':'pain','es':'dolor','pos':'noun','semantic_type':'symptom'}]}
    selected=next(expand_slots(template,groups))
    assert render('¿Siente {SYMPTOM} cuando {ACTION}?',selected)=='¿Siente dolor cuando orina?'
    assert list(expand_slots(template,{}))==[]
    assert list(expand_slots({'slots':{},'specialty':'urology'},{}))==[{}]
