import json
import datetime
import os
import sys
import mechanicalsoup
import logging


class BambooHRScraper():

    def __init__(self):
        self.logger = None
        self.setupLogging()
        self.logger.debug("Starting...")
        self.setup()
        self.browser = mechanicalsoup.StatefulBrowser()
        self.fname = 'bamboohr_scraper.json'
        self.urls = {
            "home": f"https://{os.environ['COMPANY']}.bamboohr.com/home/",
            "login": f"https://{os.environ['COMPANY']}.bamboohr.com/login.php",
            "employees": f"https://{os.environ['COMPANY']}.bamboohr.com/employee_directory/ajax/get_directory_info"
        }
        self.logger.debug("Initialized.")

    def setup(self):
        if not all(required in os.environ for required in ['USERNAME', 'PASSWORD', 'COMPANY']):
            self.logger.error('You must set your username, password, and company in your env variables.')
            sys.exit(1)

    def setupLogging(self):
        """Configure basic logging."""
        formatter_string = '[%(levelname)-5.5s %(threadName)s-%(name)s] %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=formatter_string)
        self.logger = logging.getLogger('BambooHRScraper')

    def login(self):
        self.browser.open(self.urls.get('login'))
        self.browser.get_current_page()
        self.browser.select_form()
        self.logger.debug(f"Setting username: {os.environ['USERNAME']}")
        self.logger.debug(f"Setting password:  {'*'*len(os.environ['PASSWORD'])}")
        self.browser["username"] = os.environ['USERNAME']
        self.browser["password"] = os.environ['PASSWORD']
        self.browser.submit_selected()

    def getEmployeesJSON(self):
        response = self.browser.open(self.urls.get('employees'))
        self.browser.get_current_page()
        try:
            return json.loads(response.text)
        except Exception as e:
            self.logger.error(f"{str(e)}")
            return None

    def dumpEmployeesToFile(self):
        today = str((datetime.datetime.today().strftime('%Y-%m-%d')))
        employees = self.getEmployeesJSON()
        if not employees:
            self.logger.error("Error getting employees.")
            exit(1)
        if 'employees' not in employees:
            self.logger.error("Error getting employees.")
            exit(1)
        with open(self.fname, 'r+') as f:
            try:
                curr = json.load(f)
                if today not in curr:
                    curr[today] = employees
                f.seek(0)
                json.dump(curr, f)
                f.truncate()
            except ValueError as e:
                employees = {today: employees}
                json.dump(employees, f)
                f.truncate()
            f.close()
            return

    def run(self):
        self.login()
        self.dumpEmployeesToFile()

def main():
    scraper = BambooHRScraper()
    scraper.run()

if __name__ == '__main__':
    scraper = BambooHRScraper()
    scraper.run()
