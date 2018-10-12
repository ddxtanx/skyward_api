from typing import Any, Dict

skyward_req_conf = {
    "AllowSpecial": "false",
    "Browser": "Moz",
    "BrowserPlatform": "MacIntel",
    "BrowserVersion": "61",
    "CurrentProgram": "skyportlogin.w",
    "CurrentVersion": "010173",
    "HomePage": "sepadm01.w",
    "HomePageMenuID": "0",
    "PaCVersion": "05.18.06.00.09-11.7",
    "SecurityMenuID": "0",
    "SuperVersion": "012090",
    "TouchDevice": "false",
    "UserLookupLevel": "5",
    "UserSecLevel": "5",
    "brwsInfo": "Firefox 61",
    "cUserRole": "family/student",
    "codeType": "tryLogin",
    "disableAnimations": "yes",
    "duserid": "-1",
    "fwtimestamp": "1536275256905",
    "hAlternateColors": "true",
    "hAnon": "bjlbYpAByijcxUsV",
    "hAutoOpenPref": "no",
    "hButtonHotKeyIDs": "bCancel",
    "hButtonHotKeys": "B",
    "hCompName": "SKYWEB31A",
    "hDisplayBorder": "true",
    "hIPInfo": "",
    "hLoadTime": ".042",
    "hNavSearchOption": "all",
    "hNotificationsJSON": "[]",
    "hOSName": "Windows NT",
    "hOpenSave": "no",
    "hScrollBarWidth": "17",
    "hSecCache": "0 items in 0 entities",
    "hforgotLoginPage": "fwemnu01",
    "lip": "192.168.0.100",
    "loginID": "-1",
    "method": "extrainfo",
    "nameid": "-1",
    "noheader": "yes",
    "osName": "",
    "pCountry": "US",
    "pState": "IL",
    "pageused": "Desktop",
    "recordLimit": "30",
    "requestAction": "eel",
    "screenHeight": "900",
    "screenWidth": "1440",
    "subversion": "61",
    "supported": "true",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0"
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
