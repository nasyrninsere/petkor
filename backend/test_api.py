import asyncio
import httpx

API_KEY = "d5c9cc9debf7cdab53435da4518723b5e860ff13c9987dd798505afdc94d432d"
BASE = "https://apis.data.go.kr/B551011/KorPetTourService2"

async def test():
    async with httpx.AsyncClient(timeout=15.0) as client:
        # areaBasedList2 - 지역 기반 목록 (강원=32)
        r = await client.get(f"{BASE}/areaBasedList2", params={
            "serviceKey": API_KEY, "MobileOS": "ETC", "MobileApp": "PetApp",
            "_type": "json", "numOfRows": 5, "pageNo": 1, "areaCode": "32",
        })
        data = r.json()
        body = data.get("response", {}).get("body", {})
        print("== areaBasedList2 (강원=32) ==")
        print(f"totalCount: {body.get('totalCount')}")
        items = body.get("items", {})
        item_list = items.get("item", []) if items else []
        if isinstance(item_list, dict):
            item_list = [item_list]
        for it in item_list[:3]:
            print(f"  - {it.get('title')} | {it.get('addr1')} | lat={it.get('mapy')} lng={it.get('mapx')}")

        # searchKeyword2
        r2 = await client.get(f"{BASE}/searchKeyword2", params={
            "serviceKey": API_KEY, "MobileOS": "ETC", "MobileApp": "PetApp",
            "_type": "json", "numOfRows": 3, "pageNo": 1, "keyword": "강릉",
        })
        data2 = r2.json()
        body2 = data2.get("response", {}).get("body", {})
        print(f"\n== searchKeyword2 (keyword=강릉) ==")
        print(f"status: {r2.status_code}, totalCount: {body2.get('totalCount')}")

        # locationBasedList2
        r3 = await client.get(f"{BASE}/locationBasedList2", params={
            "serviceKey": API_KEY, "MobileOS": "ETC", "MobileApp": "PetApp",
            "_type": "json", "numOfRows": 3, "pageNo": 1,
            "mapX": "128.8764", "mapY": "37.8813", "radius": 5000,
        })
        print(f"\n== locationBasedList2 (강릉 좌표) ==")
        print(f"status: {r3.status_code}")
        if r3.status_code == 200:
            b3 = r3.json().get("response", {}).get("body", {})
            print(f"totalCount: {b3.get('totalCount')}")

asyncio.run(test())
