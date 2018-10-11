from requests_html import HTMLSession, HTML, Element
import getpass
import os
from typing import Dict, List, Any
import re
import datetime



session = HTMLSession()

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

class Assignment():
    def __init__(
        self,
        name: str,
        num_points: str,
        total_points: str,
        letter_grade: str,
        date: str
    ) -> None:
        self.name = name
        self.num_points = num_points
        self.total_points = total_points
        self.letter_grade = letter_grade

        spl = date.split("/")
        if len(spl[2]) != 4:
            year = "20" + spl[2]
            spl[2] = year
        self.date = "/".join(spl)

    def points_str(self) -> str:
        return "{0}/{1} ({2})".format(
            self.num_points,
            self.total_points,
            self.letter_grade
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __le__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            my_date = datetime.datetime.strptime(self.date, "%m/%d/%Y")
            their_date = datetime.datetime.strptime(other.date, "%m/%d/%Y")
            return my_date <= their_date
        else:
            return False

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (self <= other) and not self == other

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return not (self < other)

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (self >= other) and self != other

    def __str__(self) -> str:
        return "({0}) {1} {2}".format(
            self.date,
            self.name,
            self.points_str()
        )

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

class SkywardAPI():
    """Class for Skyward data retrieval.

    Parameters
    ----------
    usern : str
        Skyward username.
    passw : str
        Skyward password.

    Attributes
    ----------
    tries : int
        Number of request attempts, used to ensure
        minimal network failures.
    username : str
        Skyward username.
    password : str
        Skyward password.
    login_data : Dict[str, Any]
        Login parameters.

    """
    def __init__(self, service: str) -> None:
        self.tries = 0
        self.base_url = "https://skyward.iscorp.com/scripts/wsisa.dll/WService={0}".format(service)
        self.login_url = self.base_url + "/skyporthttp.w"
        self.session_params = {}

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Logs into Skyward and retreives session data.

        Returns
        -------
        Dict[str, Any]
            Login data for skyward.

        Raises
        -------
        ValueError
            Incorrect username or password.
        RuntimeError
            Skyward acting weird and not returning data.

        """
        params = skyward_req_conf
        params["codeValue"] = username
        params["login"] = username
        params["password"] = password
        req = session.post(self.login_url, data=params)
        text = req.text
        if "Invalid" in text:
            raise ValueError("Incorrect username or password")
        if text != "":
            return parse_login_text(self.base_url, text)
        elif self.tries < 5:
            return self.login(username, password)
        else:
            raise RuntimeError("For some reason, Skyward is returning nothing at login. Sorry try again!")

    def setup(self, username: str, password: str) -> None:
        data = self.login(username, password)
        self.login_data = data
        self.session_params = self.get_session_params()

    @staticmethod
    def from_session_data(service: str, sky_data: Dict[str, str]) -> "SkywardAPI":
        api = SkywardAPI(service)
        api.session_params = sky_data
        return api

    def get_session_params(self) -> Dict[str, str]:
        """Gets session data from Skyward for login.

        Returns
        -------
        Dict[str, str]
            Session variables.

        """
        ldata = self.login_data

        req2 = session.post(ldata["new_url"], data=ldata["params"])
        page = req2.html
        try:
            sessid = page.find("#sessionid", first=True).attrs["value"]

            encses = page.find("#encses", first=True).attrs["value"]
        except AttributeError:
            return self.get_session_params()

        return {
            "sessid": sessid,
            "encses": encses
        }

    def get_class_grades(
        self,
        sm_grade: Element,
        grid_count: int,
        constant_options: Dict[str, str],
        url: str,
        headers: Dict[str, str],
        sm_num: int
    ) -> Dict[str, List[Assignment]]:
        attrs = sm_grade.attrs
        specific_request_data = {
            "corNumId": attrs["data-cni"],
            "gridCount": grid_count,
            "gbId": attrs["data-gid"],
            "stuId": attrs["data-sid"],
            "section": attrs["data-sec"],
            "entityId": attrs["data-eid"]
        }
        grade_request_data = constant_options
        grade_request_data.update(specific_request_data)

        grade_req = session.post(
            url,
            data=grade_request_data,
            headers=headers,
            params={
                "file": "sfgradebook001.w"
            }
        )
        text = grade_req.text

        start_split = text.find("<![CDATA[") + len("<![CDATA[")
        end_split = text.find("]]")
        text_split = text[start_split : end_split + 1]

        doc = HTML(html=text_split)

        class_name = doc.find(".gb_heading", first=True).text
        class_name = class_name.replace("\xa0", " ")

        grades = {}
        grades[class_name] = []

        semester_info = doc.find("th", first=True)
        date_range = semester_info.find("span", first=True).text
        date_range = date_range.replace("(", "").replace(")", "")

        sem_start_date = date_range.split(" - ")[0]
        # Date range looks like "(START - END)" so removing ( ) and splitting
        # gives the start date.

        sem_grade = doc.find(".odd", first=True)
        sem_grade_spl = sem_grade.text.split("\n")
        sem_lg = sem_grade_spl[0]
        sem_percent = sem_grade_spl[1]
        sem_asign = Assignment(
            "SEM{0}".format(sm_num),
            sem_percent,
            "100",
            sem_lg,
            sem_start_date
        )
        grades[class_name].append(sem_asign)

        scope = doc.find("td")
        style_str = "padding-right:4px"
        scope = [
            row
            for row in scope
            if "style" in row.attrs and row.attrs["style"] == style_str
        ]
        scope_major = scope[0]
        scope_grades = scope[1]

        list_of_grades = scope_grades.find(".even") + scope_grades.find(".odd")
        list_of_major_grades = scope_major.find(".even") + scope_major.find(".odd")
        assignments = [
            assignment
            for assignment in list_of_grades
            if "zebra-same" not in assignment.attrs
        ]

        major_grades = [
            grade
            for grade in list_of_major_grades
            if "zebra-same" in grade.attrs and grade.attrs["zebra-same"] == "true"
        ]

        for assignment in assignments:
            assignment_info = assignment.find("td")
            name = ""
            date = ""
            try:
                date = assignment_info[0].text
                name = assignment_info[1].text
            except IndexError:
                continue
            assign = None
            try:
                lg = assignment_info[2].text
                point_str = assignment_info[4].text
                point_str_spl = point_str.split(" out of ")
                earned = point_str_spl[0]
                out_of = point_str_spl[1]
                assign = Assignment(name, earned, out_of, lg, date)
            except IndexError:
                assign = Assignment(name, "*", "*", "*", date)
            grades[class_name].append(assign)

        for grade in major_grades:
            grade_info = grade.find("td")
            name = ""
            lg = ""
            try:
                desc = grade_info[0].text
                desc = desc.replace("\n", "")
                colon_split = desc.split(":")
                name = colon_split[0]
                lg = colon_split[1][0]
            except IndexError as e:
                continue
            try:
                grade_data = grade_info[2].text
                str_split = grade_data.split(" out of ")
                earned = str_split[0]
                out_of = str_split[1]
                grades[class_name].append(
                    Assignment(
                        name,
                        earned,
                        out_of,
                        lg,
                        sem_start_date
                    )
                )
            except IndexError:
                grades[class_name].append(
                    Assignment(
                        name,
                        "*",
                        "*",
                        "*",
                        sem_start_date
                    )
                )

        grades[class_name] = sorted(grades[class_name], reverse=True)
        return grades

    def get_semester_grades(self, semester_num: int, page: HTML) -> Dict[str, List[Assignment]]:
        """Gets grades for a specific semester.

        Parameters
        ----------
        semester_num : int
            1 or 2 for first or second semester.
        page : HTML
            HTML Grade page to get buttons/links/etc.

        Returns
        -------
        Dict[str, List[Assignment]]
            Dictionary of class grades.

        """
        grades = {} # type: Dict[str, List[Assignment]]

        sessionp = self.session_params
        refresh_id = page.find("#reloadValue", first=True).attrs["value"]
        grade_buttons = page.find("#showGradeInfo")

        sm_grade_buttons = [
            button
            for button in grade_buttons
            if button.attrs["data-lit"] == "SM{0}".format(semester_num)
        ]
        grade_req_url = "{0}/httploader.p".format(self.base_url)

        dwd_start = page.text.find("sff.sv('dwd', '") + len("sff.sv('dwd', '")
        dwd = page.text[dwd_start : dwd_start+5]

        constant_options = {
            "requestId": refresh_id,
            "encses": sessionp["encses"],
            "sessionid": sessionp["sessid"],
            "wfaacl": sessionp["sessid"].split("\x15")[1],
            "ishttp": "true",
            "track": "0",
            "isEoc": "no",
            "fromHttp": "yes",
            "dwd": dwd,
            "dialogLevel": "1",
            "action": "viewGradeInfoDialog",
            "subjectId": "",
            "javascript.filesAdded": "jquery.1.8.2.js,qsfmain001.css,sfgradebook.css,qsfmain001.min.js,sfgradebook.js,sfprint001.js",
            "bucket": "SEM {0}".format(semester_num)
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referrer": grade_req_url,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        grid_count = 1


        for class_sm_grade in sm_grade_buttons:
            grades.update(
                self.get_class_grades(
                    class_sm_grade,
                    grid_count,
                    constant_options,
                    grade_req_url,
                    headers,
                    semester_num
                )
            )

        return grades

    def get_grades(self) -> Dict[str, List[Assignment]]:
        """Gets grades from both semesters.

        Returns
        -------
        Dict[str, List[Assignment]]
            Grades from both semesters.

        Raises
        ------
        RuntimeError
            If the session is destroyed, no data can be received.

        """
        grade_url = self.base_url + "/sfgradebook001.w"
        sessionp = self.session_params
        req3 = session.post(grade_url, data={
            "encses": sessionp["encses"],
            "sessionid": sessionp["sessid"]
        })
        new_text = req3.text
        new_text = new_text.replace(
            "src='",
            "src='{0}/".format(self.base_url)
        ).replace(
            "href='",
            "href='{0}/".format(self.base_url)
        )
        '''
            Replacing values here to make sure that all requests
            are being made to the skyward site and not the local
            computer.
        '''

        new_html = HTML(html=new_text)
        if "Your session has timed out" in new_text or "session has expired" in new_text:
            raise RuntimeError("Session destroyed.")
        new_html.render()

        grades = {} # type: Dict[str, List[Assignment]]
        grades.update(self.get_semester_grades(1, new_html))
        grades.update(self.get_semester_grades(2, new_html))
        if grades == {}:
            raise RuntimeError("Session destroyed.")

        return grades

    def get_grades_text(self) -> Dict[str, List[str]]:
        """Converts Assignments in get_grades() to strings

        Returns
        -------
        Dict[str, List[str]]
            Grades (as a string) from both semesters.

        """
        grades = self.get_grades()
        text_grades = {}
        for clas, class_grades in grades.items():
            str_grades = []
            for grade in class_grades:
                str_grades.append(str(grade))
            text_grades[clas] = str_grades

        return text_grades

    def get_grades_json(self) -> Dict[str, List[Dict[str, str]]]:
        grades = self.get_grades()
        json_grades = {} # type: Dict[str, List[Dict[str, str]]]
        for class_name, class_grades in grades.items():
            json_grade = []
            for grade in class_grades:
                json_grade.append(grade.__dict__)
            json_grades[class_name] = json_grade
        return json_grades
