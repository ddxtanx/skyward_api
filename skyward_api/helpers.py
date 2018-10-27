from typing import Any, Dict

skyward_req_conf = {
    "requestAction": "eel",
    "codeType": "tryLogin"
}

def parse_login_text(base_url: str, text: str) -> Dict[str, Any]:
    text = text.replace("<li>", "").replace("</li>", "")

    values = text.split("^")

    try:
        new_url = base_url + "/" + values[7]
        encses = values[14]
        data = {
            "params": {
                "dwd": values[0],
                "web-data-recid": values[1],
                "wfaacl-recid": values[2],
                "wfaacl": values[3],
                "nameid": values[4],
                "duserid": values[5],
                "User-Type": values[6],
                "enc": values[13],
                "encses": encses
            },
            "new_url": new_url,
            "encses": values[14]
        }
        return data
    except IndexError as e:
        raise e
