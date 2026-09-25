import pytest

from ingest.specialty_map import RULES, map_specialties


@pytest.mark.parametrize("specialty,prefixes",list(RULES.items()))
def test_mesh(specialty,prefixes):assert specialty in map_specialties({"en":"example","trees":[prefixes[0]+".001"]})
@pytest.mark.parametrize("code,specialty",[("N40","urology"),("N70","obgyn"),("D50","hematology"),("I00","cardiology"),("J01","pulmonology"),("K00","gastroenterology"),("G00","neurology"),("F00","psychiatry"),("O01","obgyn"),("M01","orthopedics"),("P01","pediatrics"),("S01","emergency"),("R01","general_medicine")])
def test_icd(code,specialty):assert specialty in map_specialties({"en":"example","icd10_codes":[code]})
def test_labels():
    assert "anatomy" in map_specialties({"en":"example","semantic_type":"anatomy"})
    assert "urology" in map_specialties({"en":"urinary frequency"})
    assert "general_medicine" in map_specialties({"en":"example","icd10_codes":["","XYZ"]})
