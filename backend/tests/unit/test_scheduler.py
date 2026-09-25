import pytest

from app.engine.scheduler import rule_query, update_schedule


def test_schedule():
    s={"streak":0,"ease":2.5,"interval_days":0}
    for expected in (1,3):
        s=update_schedule(s,"correct");assert s["interval_days"]==expected
    s=update_schedule(s,"correct",True);assert s["interval_days"]>3
    s=update_schedule(s,"wrong");assert s["streak"]==0 and s["interval_days"]==0
    s["ease"]=1.3;assert update_schedule(s,"wrong")["ease"]==1.3
@pytest.mark.parametrize("filter",["wrong_only","correct_only","leech","any"])
def test_rules(filter):
    q,args=rule_query({"result_filter":filter,"specialties":["urology"],"kinds":["mcq"],"item_ids":[1],"direction":"en2es","min_wrong":1,"max_ease":2.,"seen_within_days":10})
    assert "q.profile_id=:profile" in q
    assert args["profile"]==1 and args["specialties0"]=="urology"
