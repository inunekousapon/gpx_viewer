"""APIルーター"""

from fastapi import APIRouter, Query

from src.services.geocoding import get_geocoding_service, AddressResult


router = APIRouter(prefix="/api", tags=["api"])


@router.get("/reverse-geocode")
async def reverse_geocode(
    lat: float = Query(..., description="緯度"),
    lng: float = Query(..., description="経度"),
) -> dict[str, str | None]:
    """
    逆ジオコーディング（緯度経度から住所を取得）

    サーバー側でリクエストをキューイングし、1秒に1回以上の
    Nominatim APIへのリクエストを行わないようにしています。
    """
    service = get_geocoding_service()
    result: AddressResult | None = await service.get_address(lat, lng)

    if result is None:
        return {
            "prefecture": None,
            "city": None,
            "road": None,
        }

    return {
        "prefecture": result.prefecture or None,
        "city": result.city or None,
        "road": result.road or None,
    }
