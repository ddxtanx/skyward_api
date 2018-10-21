from typing import Any, Dict

default_login_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language":	"en-US,en;q=0.5",
    "Connection":	"keep-alive",
    "Content-Type":	"application/x-www-form-urlencoded",
    "Host":	"skyward.iscorp.com",
    "Referrer": "https://skyward.iscorp.com/scripts/wsisa.dll/WService=wseduoakparkrfil/fwemnu01.w"
}
skyward_req_conf = {
    "requestAction": "eel",
    "method": "extrainfo",
    "codeType": "tryLogin",
    "hCompName": "SKYWEB31E",
    "hOSName": "Windows NT",
    "SecurityMenuID": 0,
    "HomePageMenuID": 0,
    "nameid": -1,
    "hNavSearchOption": "all",
    "hSecCache": "0 items in 0 entities",
    "CurrentProgram": "skyportlogin.w",
    "PaCVersion": "05.18.10.00.02-11.7",
    "Browser": "Chrome",
    "BrowserVersion": 69,
    "BrowserPlatform": "MacIntel",
    "TouchDevice": "false",
    "noheader": "yes",
    "duserid": -1,
    "HomePage": "sepadm01.w",
    "loginID": -1,
    "hScrollBarWidth": 17,
    "UserSecLevel": 5,
    "UserLookupLevel": 5,
    "AllowSpecial": "false",
    "hNotificationsJSON": "[]",
    "hDisplayBorder": "true",
    "hAlternateColors": "true",
    "screenWidth": 1440,
    "screenHeight": 900,
    "hforgotLoginPage": "fwemnu01",
    "subversion": 69,
    "supported": "true",
    "pageused": "Desktop",
    "recordLimit": 30,
    "disableAnimations": "yes",
    "hOpenSave": "no",
    "hAutoOpenPref": "no",
    "hButtonHotKeyIDs": "bCancel",
    "hButtonHotKeys": "B",
    "hLoadTime": ".045",
    "lip": "192.168.0.100",
    "cUserRole": "family/student",
    "hIPInfo": "SkywardUpdater"
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
