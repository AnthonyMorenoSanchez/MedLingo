from ingest.dedupe import dedupe, normalized


def test_dedupe():
    rows=[{"en":" Kidney. ","es":" Riñón ","specialties":["urology"]},{"en":"kidney","es":"riñón","specialties":["anatomy"]}]
    got=dedupe(rows)
    assert len(got)==1 and got[0]["specialties"]==["anatomy","urology"]
    assert normalized({"en":"anemia","es":"anemia"}) is None
    assert normalized({"en":"","es":"a"}) is None
    assert normalized({"en":"a"*121,"es":"a"}) is None
    assert normalized({"en":"DNA","es":"ADN"})["en"]=="DNA"
