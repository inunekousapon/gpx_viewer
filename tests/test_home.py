"""ホームページのテスト"""

from fastapi.testclient import TestClient


def test_home_returns_html(client: TestClient) -> None:
    """ホームページがHTMLを返す"""
    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "GPX Map Viewer" in response.text


def test_upload_with_valid_gpx_returns_map(client: TestClient) -> None:
    """有効なGPXファイルをアップロードすると地図が表示される"""
    # Arrange
    gpx_content = b"""<?xml version="1.0" encoding="UTF-8"?>
    <gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
        <trk>
            <trkseg>
                <trkpt lat="35.6861" lon="139.6844">
                    <ele>38.9</ele>
                </trkpt>
            </trkseg>
        </trk>
    </gpx>"""

    # Act
    response = client.post(
        "/upload",
        files={"file": ("test.gpx", gpx_content, "application/gpx+xml")},
    )

    # Assert
    assert response.status_code == 200
    assert "leaflet" in response.text.lower()


def test_upload_with_invalid_extension_returns_error(client: TestClient) -> None:
    """GPX以外のファイルをアップロードするとエラーになる"""
    # Arrange
    content = b"test content"

    # Act
    response = client.post(
        "/upload",
        files={"file": ("test.txt", content, "text/plain")},
    )

    # Assert
    assert response.status_code == 200
    assert "GPXファイル" in response.text


def test_upload_with_empty_gpx_returns_error(client: TestClient) -> None:
    """位置情報のないGPXファイルをアップロードするとエラーになる"""
    # Arrange
    gpx_content = b"""<?xml version="1.0" encoding="UTF-8"?>
    <gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
    </gpx>"""

    # Act
    response = client.post(
        "/upload",
        files={"file": ("empty.gpx", gpx_content, "application/gpx+xml")},
    )

    # Assert
    assert response.status_code == 200
    assert "位置情報が含まれていません" in response.text
