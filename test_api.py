from fastapi.testclient import TestClient
from app import app, detect_platform, human_filesize, format_duration

client = TestClient(app)

def test_routes():
    res = client.get("/api/supported-platforms")
    assert res.status_code == 200
    data = res.json()
    assert "categories" in data
    print("[OK] Supported platforms endpoint works! Categories:", len(data["categories"]))

def test_helpers():
    assert detect_platform("https://www.youtube.com/watch?v=123")["name"] == "YouTube"
    assert detect_platform("https://www.instagram.com/reel/123")["name"] == "Instagram"
    assert detect_platform("https://www.facebook.com/watch/?v=123")["name"] == "Facebook"
    assert detect_platform("https://www.terabox.com/s/123")["name"] == "TeraBox"
    assert detect_platform("https://www.hotstar.com/in/movies/123")["name"] == "Disney+ Hotstar"
    assert human_filesize(1048576) == "1.0 MB"
    assert format_duration(125) == "02:05"
    print("[OK] Helper functions work accurately!")

def test_static_files():
    res = client.get("/")
    assert res.status_code == 200
    assert "OmniStream" in res.text
    print("[OK] Static index.html loads cleanly!")

if __name__ == "__main__":
    test_routes()
    test_helpers()
    test_static_files()
    print("[SUCCESS] All API tests passed successfully!")
