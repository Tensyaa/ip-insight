import re
import requests
import requests_mock
from app_eb_trial import is_private_ip, get_ip_info

def test_is_private_ip_patterns():
    assert is_private_ip("10.0.0.1")
    assert is_private_ip("172.16.5.9")
    assert is_private_ip("172.31.255.255")
    assert is_private_ip("192.168.1.100")
    assert is_private_ip("127.0.0.1")
    assert not is_private_ip("8.8.8.8")
    assert not is_private_ip("1.1.1.1")

def test_get_ip_info_success():
    with requests_mock.Mocker() as m:
        m.get("https://ipapi.co/8.8.8.8/json/", json={
            "ip":"8.8.8.8",
            "city":"Mountain View",
            "country_name":"United States",
            "org":"Google LLC",
            "asn":"AS15169",
            "latitude":37.4056,
            "longitude":-122.0775
        }, status_code=200)
        data = get_ip_info("8.8.8.8")
        assert data["ip"] == "8.8.8.8"
        assert data["asn"] == "AS15169"

def test_get_ip_info_rate_limited():
    with requests_mock.Mocker() as m:
        m.get("https://ipapi.co/1.2.3.4/json/", status_code=429)
        data = get_ip_info("1.2.3.4")
        assert "error" in data
        assert "limit" in data["error"].lower()

def test_get_ip_info_api_error():
    with requests_mock.Mocker() as m:
        m.get("https://ipapi.co/9.9.9.9/json/", json={"error": True, "reason": "Bad IP"}, status_code=200)
        data = get_ip_info("9.9.9.9")
        assert "error" in data
        assert "bad ip" in data["error"].lower()
