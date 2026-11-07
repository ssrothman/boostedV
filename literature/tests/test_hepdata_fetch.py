import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import hepdata_fetch as hf  # noqa: E402


def test_safe_name_replaces_unsafe_characters():
    assert hf.safe_name("Coupling limits (DM mediator)") == "Coupling_limits_DM_mediator"
    assert hf.safe_name("a/b\\c") == "a_b_c"
    assert hf.safe_name("///") == "table"


def test_table_urls_quotes_spaces_and_skips_missing():
    record = {"data_tables": [
        {"name": "T 1", "data": {"json": "https://www.hepdata.net/download/table/ins1/Coupling limits (DM)/json"}},
        {"name": "T 2", "data": {}},
    ]}
    assert hf.table_urls(record) == [
        ("T 1", "https://www.hepdata.net/download/table/ins1/Coupling%20limits%20%28DM%29/json")]


def test_table_urls_keeps_hepdata_percent_escapes():
    record = {"data_tables": [{"name": "L", "data": {
        "json": "https://www.hepdata.net/download/table/ins2/Limits for 10%25 width and $%5Calpha_{%5Cmathrm{t}}$/json"}}]}
    assert hf.table_urls(record) == [("L",
        "https://www.hepdata.net/download/table/ins2/Limits%20for%2010%25%20width%20and%20%24%5Calpha_%7B%5Cmathrm%7Bt%7D%7D%24/json")]


def test_table_urls_empty_record():
    assert hf.table_urls({}) == []


def test_is_json_rejects_html_error_page():
    assert hf.is_json(b'{"values": []}')
    assert not hf.is_json(b"<!DOCTYPE html><title>HEPData Error</title>")
    assert not hf.is_json(b"")
