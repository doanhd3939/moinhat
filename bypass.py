"""
Xử lý logic lấy mã bypass cho từng loại.
"""
import requests
import re
from typing import Any, Dict, Union

BYPASS_URLS: Dict[str, Any] = {
    'm88': ('taodeptrai', 'https://bet88ec.com/cach-danh-bai-sam-loc', 'https://bet88ec.com/'),
    'fb88': ('taodeptrai', 'https://fb88mg.com/ty-le-cuoc-hong-kong-la-gi', 'https://fb88mg.com/'),
    '188bet': ('taodeptrailamnhe', 'https://88betag.com/cach-choi-game-bai-pok-deng', 'https://88betag.com/'),
    'w88': ('taodeptrai', 'https://188.166.185.213/tim-hieu-khai-niem-3-bet-trong-poker-la-gi', 'https://188.166.185.213/'),
    'v9bet': [
        "https://traffic-user.net/GET_MA.php?codexn=taodeptrai&url=https://v9betdi.com/cuoc-thang-ap-dao-la-gi&loai_traffic=https://v9betdi.com/&clk=1000",
        "https://traffic-user.net/GET_MA.php?codexn=taodeptrai&url=https://v9betho.com/ca-cuoc-bong-ro-ao&loai_traffic=https://v9betho.com/&clk=1000",
        "https://traffic-user.net/GET_MA.php?codexn=taodeptrai&url=https://v9betxa.com/cach-choi-craps&loai_traffic=https://v9betxa.com/&clk=1000",
    ],
    'bk8': ('taodeptrai', 'https://bk8xo.com/lo-ba-cang-la-gi', 'https://bk8xo.com/'),
    'vn88': ('deobiet', 'https://vn88ie.com/cach-choi-mega-6-45', 'https://vn88ie.com/'),
}

def get_bypass_code(bypass_type: str) -> Union[Dict[str, Any], None]:
    """
    Lấy mã bypass cho từng loại, trả về dict chứa 'code' hoặc 'codes'.
    """
    if bypass_type not in BYPASS_URLS:
        return None
    urls = BYPASS_URLS[bypass_type]
    if isinstance(urls, list):
        results = []
        for url in urls:
            try:
                response = requests.post(url, timeout=15)
                html = response.text
                match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', html)
                if match:
                    results.append(match.group(1))
            except Exception:
                continue
        if results:
            return {"codes": results}
        else:
            return None
    else:
        code_key, url, ref = urls
        try:
            response = requests.post(
                f'https://traffic-user.net/GET_MA.php?codexn={code_key}&url={url}&loai_traffic={ref}&clk=1000',
                timeout=15
            )
            html = response.text
            match = re.search(r'<span id="layma_me_vuatraffic"[^>]*>\s*(\d+)\s*</span>', html)
            if match:
                code = match.group(1)
                return {"code": code}
            else:
                return None
        except Exception:
            return None
