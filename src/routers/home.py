"""ホームページルーター"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from typing import Any

from src.dependencies import TemplateResponse
from src.services.gpx_parser import GpxParser, GpxParseError


router = APIRouter()

# 日本時間
JST = timezone(timedelta(hours=9))


def parse_iso_time(time_str: str) -> datetime | None:
    """ISO8601形式の時刻文字列をdatetimeに変換"""
    try:
        # Zで終わる場合はUTC
        if time_str.endswith("Z"):
            dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(time_str)
        return dt
    except (ValueError, TypeError):
        return None


def get_time_range(
    points: list[Any],
) -> dict[str, str] | None:
    """ポイントリストから時間範囲を取得"""
    times: list[datetime] = []
    for p in points:
        if p.time:
            dt = parse_iso_time(p.time)
            if dt:
                times.append(dt)

    if not times:
        return None

    min_time = min(times)
    max_time = max(times)

    # 日本時間に変換
    min_time_jst = min_time.astimezone(JST)
    max_time_jst = max_time.astimezone(JST)

    return {
        "start": min_time.isoformat(),
        "end": max_time.isoformat(),
        "start_local": min_time_jst.strftime("%Y年%m月%d日 %H:%M:%S"),
        "end_local": max_time_jst.strftime("%Y年%m月%d日 %H:%M:%S"),
        "start_date": min_time_jst.strftime("%Y-%m-%d"),
        "start_time": min_time_jst.strftime("%H:%M:%S"),
    }


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> Any:
    """ホームページ（アップロードフォーム）"""
    return (
        TemplateResponse(request)
        .add_context(title="GPXファイルをアップロード", gpx_data=None, error=None)
        .render("index.html")
    )


@router.post("/upload", response_class=HTMLResponse)
async def upload_gpx(request: Request, file: UploadFile = File(...)) -> Any:
    """GPXファイルアップロード処理"""
    # ファイル名チェック
    if file.filename is None or not file.filename.lower().endswith(".gpx"):
        return (
            TemplateResponse(request)
            .add_context(
                title="エラー",
                gpx_data=None,
                error="GPXファイル（.gpx）を選択してください",
            )
            .render("index.html")
        )

    # ファイル読み込み
    try:
        content = await file.read()
    except Exception:
        return (
            TemplateResponse(request)
            .add_context(
                title="エラー",
                gpx_data=None,
                error="ファイルの読み込みに失敗しました",
            )
            .render("index.html")
        )

    # GPXパース
    parser = GpxParser()
    try:
        gpx_data = parser.parse(content)
    except GpxParseError as e:
        return (
            TemplateResponse(request)
            .add_context(
                title="エラー",
                gpx_data=None,
                error=f"GPXファイルの解析に失敗しました: {e}",
            )
            .render("index.html")
        )

    # ポイント数チェック
    points = gpx_data.get_all_points()
    if not points:
        return (
            TemplateResponse(request)
            .add_context(
                title="エラー",
                gpx_data=None,
                error="GPXファイルに位置情報が含まれていません",
            )
            .render("index.html")
        )

    # 地図表示用データ作成
    center = gpx_data.get_center()
    bounds = gpx_data.get_bounds()
    time_range = get_time_range(points)

    # JavaScript用にポイントデータを変換
    points_for_js = [
        {
            "lat": p.latitude,
            "lng": p.longitude,
            "ele": p.elevation,
            "time": p.time,
        }
        for p in points
    ]

    return (
        TemplateResponse(request)
        .add_context(
            title="地図表示",
            gpx_data={
                "filename": file.filename,
                "point_count": len(points),
                "center": {"lat": center[0], "lng": center[1]} if center else None,
                "bounds": {
                    "min_lat": bounds[0],
                    "min_lng": bounds[1],
                    "max_lat": bounds[2],
                    "max_lng": bounds[3],
                }
                if bounds
                else None,
                "points": points_for_js,
                "time_range": time_range,
            },
            error=None,
        )
        .render("map.html")
    )
