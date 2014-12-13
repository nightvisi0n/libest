#!/usr/bin/env python

__author__ = 'jneureuther'
__license__ = 'CC BY-SA 4.0'
__version__ = '1.0'
__est_version__ = 'Version 2.0.2360'

import filecmp
import requests
from bs4 import BeautifulSoup
import magic
from collections import OrderedDict


class libest:

    def __init__(self):
        self.s = requests.session()
        self.base_url = 'https://est.informatik.uni-erlangen.de'

    def __del__(self):
        self.s.close()

    # login to est
    # returns True if successfully logged in
    def authenticate(self, user, passwd):
            params = {'login': user, 'password': passwd, 'submit': 'login'}
            est_error = self.parse_html_id(self.s.post(self.base_url + '/login.html?action=student',
                                                       params=params).text, 'estError')
            return True if est_error is None else est_error.next.strip()

    # returns the file id of the file name. If it not exists, it returns 2
    def search_file(self, file_name, lecture_id):
        est_file_id_tag = self.parse_html_text(self.s.get(self.base_url + '/encodingchecker.html?lectureId='
                                                                        + str(lecture_id) + '&action=submit&tab=upload').text, file_name, "label")
        if est_file_id_tag is None:
            return 2
        else:
            return est_file_id_tag['for']

    # submits a file to est
    def submit_file(self, name, path, lecture_id, submission_member_code):
        est_file_id = self.search_file(name, lecture_id)
        if est_file_id is 2:
            return 2
        my_magic = magic.Magic(mime=True)
        mime_type = my_magic.from_file(path)
        if mime_type == 'inode/x-empty':
            return 3

        loc_file = [(est_file_id, (name, open(path, 'rb'), mime_type))]
        params = {'upload': 'upload', 'lectureId': str(lecture_id),
                  'submitterCode_' + est_file_id[:4]: submission_member_code, 'action': 'submit', 'tab': 'upload'}
        est_error = self.parse_html_id(self.s.post(self.base_url + '/encodingchecker.html', files=loc_file, data=params)
                                       .text, 'estError')
        if est_error is None:
            return 1
        else:
            return est_error.next.strip()

    # checks, if the given file is the same like in est
    def check_file(self, name, path, lecture_id):
        file_url = self.base_url + '/' + self.parse_html_text(self.s.get(self.base_url + '/judging.html?lectureId=' +
                                                                         str(lecture_id) + '&action=submit&tab=overview')
                                                              .text, name, "td").find_next("a").get('href')
        temp_file_path = "/tmp/" + name
        self.download_file(file_url, temp_file_path)
        if filecmp.cmp(path, temp_file_path, shallow=False):
            return 1
        else:
            return 0

    # returns the status of a file on est
    def check_status(self, name, lecture_id):
        name_tag = self.parse_html_text(self.s.get(self.base_url + '/judging.html?lectureId=' +
                                                   str(lecture_id) + '&action=submit&tab=overview').text, name, "td")
        if name_tag is not None:
            return name_tag.find_previous("span").get('title')

    # downloads a file from est to path
    def download_file(self, url, path):
        # local_filename = url.split('/')[-1]
        r = self.s.get(url, stream=True)
        f = open(path, 'wb')
        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
        f.close()
        return

    # returns the lecture ids of the logged in person
    def get_lecture_ids(self):
        ids = []
        for a in self.parse_html_id(self.s.get(self.base_url).text, 'estContent').find_all_next("a"):
            if 'index.html?lectureId' in a['href']:
                ids.append(a['href'].split('=')[1].split('&')[0])
                ids.append(a.next.strip())
        return list(OrderedDict.fromkeys(ids))

    # returns the current est version
    def get_est_version(self):
        try:
            return self.parse_html_id(self.s.get(self.base_url).text, 'footermenu').find_next("li").text
        except requests.exceptions.ConnectionError:
            return '-1'

    # returns True if the current est version is supported
    def check_est_version(self):
        est_version = self.get_est_version()
        return True if __est_version__ in est_version else est_version

    # returns the name of the group submission partner
    def get_submission_with(self, group_submission_code, lecture_id):
        return self.parse_html_text(self.s.get(self.base_url + '/submissiongroupdynamic.html?lectureId='
                                               + str(lecture_id) + '&action=submit&tab=overview').text,
                                    group_submission_code, "span").previous_element[:-2].strip()

    # returns the name of the group submission partner
    def get_group_submission_code(self, file_name, lecture_id):
        element = self.parse_html_text(self.s.get(self.base_url + '/submissiongroupdynamic.html?lectureId='
                                            + str(lecture_id) + '&action=submit&tab=overview').text, file_name, 'td')
        if element is None:
            return ''
        while not 'submissionGroupDynamicCode' in str(element):
            if not element.next_element is None:
                element = element.next_element
            else:
                return ''
        return BeautifulSoup(str(element)).find('span', class_='submissionGroupDynamicCode').next_element

    @staticmethod
    def parse_html_id(html, html_id):
        soup = BeautifulSoup(html)
        return soup.find(id=html_id)

    @staticmethod
    def parse_html_text(html, text, html_type):
        soup = BeautifulSoup(html)
        return soup.find(html_type, text=text)

    @staticmethod
    def parse_html_find_all(html, html_type):
        soup = BeautifulSoup(html)
        return soup.find_all(html_type)
