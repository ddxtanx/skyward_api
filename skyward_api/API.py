from requests_html import HTMLSession, HTML, Element, HTMLResponse
from skyward_api.assignment import Assignment
from skyward_api.helpers import parse_login_text, skyward_req_conf
from skyward_api.skyward_class import SkywardClass
import requests
import getpass
import os
from typing import Dict, List, Any
import re
import time
import lxml

session = HTMLSession()

def edit_srcs(page: HTMLResponse, url: str) -> HTML:
    new_text = page.text
    new_text = new_text.replace(
        "src='",
        "src='{0}/".format(url)
    ).replace(
        "href='",
        "href='{0}/".format(url)
    )
    '''
        Replacing values here to make sure that all requests
        are being made to the skyward site and not the local
        computer.
    '''

    new_html = HTML(html=new_text)
    return new_html
class SkywardError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)

class SessionError(SkywardError):
    def __init__(self, message: str) -> None:
        super().__init__(message)

class SkywardAPI():
    """Class for Skyward data retrieval.

    Parameters
    ----------
    service: str
        Skyward service for school.
    timout: int
        Request timeout (the default is 60)

    Attributes
    ----------
    timeout : int
        Seconds until request times out.
    base_url: str
        Base url for requests
    login_url: str
        URL for login.
    session_params : Dict[str, Any]
        Parameters for session.

    """
    def __init__(
        self,
        service: str,
        timeout: int = 60
    ) -> None:
        self.base_url = "https://skyward.iscorp.com/scripts/wsisa.dll/WService={0}".format(service)
        self.login_url = self.base_url + "/skyporthttp.w"
        self.timeout = timeout
        self.session_params = {} # type: Dict[str, str]

    def timed_request(
        self,
        url: str,
        data: Dict[str, str] = {},
        headers: Dict[str, str] = {},
        method: str = "post",
        params: Dict[str, str] = {}
    ) -> HTMLResponse:
        """Issues a requests-html request with timeout functionality. Automatically
            closes session at end of request.

        Parameters
        ----------
        url : str
            URL for request.
        data : Dict[str, str]
            Data for request (the default is {}).
        headers : Dict[str, str]
            Headers for request (the default is {}).
        method : str
            Method of request (the default is "post").
        params : Dict[str, str]
            Params for request (the default is {}).

        Returns
        -------
        HTMLResponse
            Response of request.

        Raises
        -------
        SkywardError
            Unable to connect to skyward.

        """
        start_time = time.time()
        return_data = None
        while True:
            try:
                return_data = session.request(
                    method,
                    url,
                    data=data,
                    headers=headers,
                    params=params
                )
                break
            except requests.exceptions.ConnectionError:
                if time.time() > start_time + self.timeout:
                    raise SkywardError('Request to Skyward failed.')
                else:
                    time.sleep(1)
        return return_data

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Logs into Skyward and retreives session data.

        Parameters
        ----------
        username: str
            Skyward username.
        password: str
            Skyward password.

        Returns
        -------
        Dict[str, Any]
            Login data for skyward.

        Raises
        -------
        ValueError
            Incorrect username or password.
        SkywardError
            Unable to connect to Skyward.

        """
        params = skyward_req_conf
        params["codeValue"] = username
        params["login"] = username
        params["password"] = password
        req = self.timed_request(self.login_url, data=params)
        text = req.html.text
        if "Invalid" in text:
            raise ValueError("Incorrect username or password")
        times = 0
        while text == "" and times <= 5:
            req = self.timed_request(self.login_url, data=params)
            text = req.html.text
            times += 1
        if text != "":
            data = parse_login_text(self.base_url, text)
            return data
        else:
            raise SkywardError("Skyward returning no login data.")

    def setup(self, username: str, password: str) -> None:
        """Sets up api session data using username and password.

        Parameters
        ----------
        username : str
            Skyward username.
        password : str
            Skyward password.
        """
        data = self.login(username, password)
        self.login_data = data
        self.session_params = self.get_session_params()


    @staticmethod
    def from_username_password(
        username: str,
        password: str,
        service: str,
        timeout: int = 60
    ) -> "SkywardAPI":
        """Returns a logged-in SkywardAPI object using username and password provided.

        Parameters
        ----------
        username : str
            Skyward username.
        password : str
            Skyward password.
        service : str
            Skyward service.
        timeout : int
            Timeout of requests made to Skyward (the default is 60).

        Returns
        -------
        SkywardAPI
            API object logged in with supplied credentials.

        Raises
        -------
        ValueError
            Incorrect username and password (from setup).
        SkywardError
            Unable to connect to Skyward (from setup).

        """
        api = SkywardAPI(service, timeout=timeout)
        api.setup(username, password)
        return api

    @staticmethod
    def from_session_data(
        service: str,
        sky_data: Dict[str, str],
        timeout: int = 60
    ) -> "SkywardAPI":
        """Generates an API given a service and session data.

        Parameters
        ----------
        service : str
            Skyward service to be used.
        sky_data : Dict[str, str]
            Session data from skyward.

        Returns
        -------
        SkywardAPI
            An api for the user given the session info.

        """
        api = SkywardAPI(service, timeout=timeout)
        api.session_params = sky_data
        grade_url = api.base_url + "/sfhome01.w"
        sessionp = api.session_params
        req3 = api.timed_request(grade_url, data={
            "encses": sessionp["encses"],
            "sessionid": sessionp["sessid"]
        })
        new_html = edit_srcs(req3, api.base_url)
        other_data = new_html.render(reload=False, script="""
            () => {
                return {
                    dwd: sff.getValue('dwd'),
                    nameid: sff.getValue('nameid'),
                    wfaacl: sff.getValue('wfaacl'),
                }
            }
        """)
        os.system("killall Chromium")
        api.session_params.update(other_data)

        return api

    def get_session_params(self) -> Dict[str, str]:
        """Gets session data from Skyward for login.

        Returns
        -------
        Dict[str, str]
            Session variables.

        """
        ldata = self.login_data

        req2 = self.timed_request(ldata["new_url"], data=ldata["params"])
        page = req2.html
        obj = {}
        try:
            obj["sessid"] = page.find("#sessionid", first=True).attrs["value"]

            obj["encses"] = page.find("#encses", first=True).attrs["value"]
        except AttributeError:
            obj = self.get_session_params()
        obj["dwd"] = ldata["params"]["dwd"]
        obj["nameid"] = ldata["params"]["nameid"]
        obj["wfaacl"] = ldata["params"]["wfaacl"]
        return obj

    def get_class_grades(
        self,
        sm_grade: Element,
        grid_count: int,
        constant_options: Dict[str, str],
        url: str,
        sm_num: int
    ) -> SkywardClass:
        """Gets class grades given elements and request options.

        Parameters
        ----------
        sm_grade : Element
            HTML element containing request information.
        grid_count : int
            Grid count parameter on page.
        constant_options : Dict[str, str]
            Constant options provided to ensure valid request.
        url : str
            Request url.
        sm_num : int
            Semester number in question.

        Returns
        -------
        SkywardClass
            Grades from a class.

        """
        attrs = sm_grade.attrs
        specific_request_data = {
            "corNumId": attrs["data-cni"],
            "gbId": attrs["data-gid"],
            "stuId": attrs["data-sid"],
            "section": attrs["data-sec"],
            "entityId": attrs["data-eid"]
        }
        grade_request_data = constant_options
        grade_request_data.update(specific_request_data)

        grade_req = self.timed_request(
            url,
            data=grade_request_data,
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

        sky_class = SkywardClass(class_name, [])

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
        sky_class.add_grade(sem_asign)

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
            sky_class.add_grade(assign)

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
                sky_class.add_grade(
                    Assignment(
                        name,
                        earned,
                        out_of,
                        lg,
                        sem_start_date
                    )
                )
            except IndexError:
                sky_class.add_grade(
                    Assignment(
                        name,
                        "*",
                        "*",
                        "*",
                        sem_start_date
                    )
                )

        sky_class.sort_grades_by_date()
        return sky_class

    def get_semester_grades(self, semester_num: int, page: HTML) -> List[SkywardClass]:
        """Gets grades for a specific semester.

        Parameters
        ----------
        semester_num : int
            1 or 2 for first or second semester.
        page : HTML
            HTML Grade page to get buttons/links/etc.

        Returns
        -------
        List[SkywardClass]
            List of class grades.

        """
        grades = [] # type: List[SkywardClass]

        sessionp = self.session_params
        grade_buttons = page.find("#showGradeInfo")

        sm_grade_buttons = [
            button
            for button in grade_buttons
            if button.attrs["data-lit"] == "SM{0}".format(semester_num)
        ]
        grade_req_url = "{0}/httploader.p".format(self.base_url)

        constant_options = {
            "encses": sessionp["encses"],
            "sessionid": sessionp["sessid"],
            "ishttp": "true",
            "fromHttp": "yes",
            "action": "viewGradeInfoDialog",
            "bucket": "SEM {0}".format(semester_num)
        }
        grid_count = 1


        for class_sm_grade in sm_grade_buttons:
            grades.append(
                self.get_class_grades(
                    class_sm_grade,
                    grid_count,
                    constant_options,
                    grade_req_url,
                    semester_num
                )
            )
        return grades

    def get_grades(self) -> List[SkywardClass]:
        """Gets grades from both semesters.

        Returns
        -------
        List[SkywardClass]
            Grades from both semesters.

        Raises
        ------
        SessionError
            If the session is destroyed, no data can be received.

        """
        grade_url = self.base_url + "/sfgradebook001.w"
        sessionp = self.session_params
        req3 = self.timed_request(grade_url, data={
            "encses": sessionp["encses"],
            "sessionid": sessionp["sessid"]
        })
        new_html = edit_srcs(req3, self.base_url)
        if "Your session has timed out" in new_html.text or "session has expired" in new_html.text:
            raise SessionError("Session destroyed. Session timed out.")
        ret_data = new_html.render()


        grades = self.get_semester_grades(1, new_html)
        grades += self.get_semester_grades(2, new_html)
        if grades == {}:
            raise SessionError("Session destroyed. No grades returned.")
        os.system("killall Chromium")
        return grades

    def get_grades_text(self) -> Dict[str, List[str]]:
        """Converts Assignments in get_grades() to strings

        Returns
        -------
        Dict[str, List[str]]
            Grades (as a string) from both semesters.

        """
        grades = self.get_grades()
        str_grades = {}
        for sky_class in grades:
            str_grades[sky_class.skyward_title()] = sky_class.grades_to_text()
        return str_grades

    def get_grades_json(self) -> Dict[str, List[Dict[str, Any]]]:
        """Converts Assignments in get_grades() to strings

        Returns
        -------
        Dict[str, List[str]]
            Grades (as a string) from both semesters.

        """
        grades = self.get_grades()
        json_grades = {}
        for sky_class in grades:
            class_grades = sky_class.grades
            class_grades_json = list(
                map(
                    lambda grade_obj: grade_obj.__dict__,
                    class_grades
                )
            )
            json_grades[sky_class.skyward_title()] = class_grades_json

        return json_grades

    def keep_alive(self) -> None:
        """Issues a keep-alive request for the session.

        """
        grade_url = self.base_url + "/qsuprhttp000.w?"
        sessionp = self.session_params
        req = self.timed_request(grade_url, data={
            "dwd": sessionp["dwd"],
            "idleTimeout": 300000,
            "myIdleSeconds": 60,
            "nameid": sessionp["nameid"],
            "requestAction": "mySession",
            "wfaacl": sessionp["wfaacl"]
        }, method = "get")
