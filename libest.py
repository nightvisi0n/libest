#!/usr/bin/env python

__author__ = 'jneureuther, sedrubal'
__license__ = 'CC BY-SA 4.0'
__version__ = '1.2.0'
__est_version__ = 'Version 2.0.2384'

import requests
import magic
from filecmp import cmp
from bs4 import BeautifulSoup
from collections import OrderedDict


class LibEst:
    """
    A class containing functions and helpers to handle the est
    """
    def __init__(self):
        self.s = requests.session()
        self.est_urls = dict()
        self.est_urls['base'] = 'https://est.informatik.uni-erlangen.de'
        self.est_urls['login'] = self.est_urls['base'] + '/login.html?action=student'
        self.est_urls['upload'] = self.est_urls['base'] + '/exercise.html'
        self.est_urls['upload_view'] = self.est_urls['upload'] + '?lectureId={lec_id}&action=submit&tab=upload'
        self.est_urls['check'] = self.est_urls['base'] + '/judging.html?lectureId={lec_id}&action=submit&tab=overview'
        self.est_urls['group'] = self.est_urls['base'] +\
                                 '/submissiongroupdynamic.html?lectureId={lec_id}&action=submit&tab=overview'

    def __del__(self):
        if self.s is not None:
            try:
                self.s.close()
            except (TypeError, AttributeError):
                # strange errors
                from sys import stderr
                print('Error in LibEst') >> stderr

    def authenticate(self, user, passwd):
        """
        Login to est
        :type user: str
        :type passwd: str
        :param user: the user to login
        :param passwd: the password for the user
        :return: True on success, an error message if login not succeeded
        """
        params = {'login': user, 'password': passwd, 'submit': 'login'}
        est_error = self.parse_html_id(self.s.post(self.est_urls['login'],
                                                   params=params).text, 'estError')
        return True if est_error is None else est_error.next.strip()

    def search_file(self, file_name, lecture_id):
        """
        Searches the id of a file in est
        :type file_name: str
        :type lecture_id: str
        :param file_name: the name of the file to search the id
        :param lecture_id: the id of the lecture to search the file in
        :return: 2 if file not exists, else the file id
        """
        est_file_id_tag = self.parse_html_text(self.s.get(
            self.est_urls['upload_view'].format(lec_id=lecture_id)).text, file_name, "label")
        if est_file_id_tag is None:
            return 2
        else:
            return est_file_id_tag['for']

    def submit_file(self, filename, path, lecture_id, submission_member_code=""):
        """
        Submits a file to est
        :type filename: str
        :type path: str
        :type lecture_id: str
        :type submission_member_code: str
        :param filename: the name of the file
        :param path: the path to the file locally
        :param lecture_id: the id of the lecture in est
        :param submission_member_code: the code of the partner for group submission
        :return:
        """
        est_file_id = self.search_file(filename, lecture_id)
        if est_file_id is 2:
            return 2
        my_magic = magic.Magic(mime=True)
        mime_type = my_magic.from_file(path)
        if mime_type == 'inode/x-empty':
            return 3

        loc_file = [(est_file_id, (filename, open(path, 'rb'), mime_type))]
        params = {'upload': 'upload', 'lectureId': str(lecture_id),
                  'submitterCode_' + est_file_id[:4]: submission_member_code,
                  'action': 'submit', 'tab': 'upload'}
        est_error = self.parse_html_id(self.s.post(self.est_urls['upload_view'], files=loc_file, data=params)
                                       .text, 'estError')
        if est_error is None:
            return 1
        else:
            return est_error.next.strip()

    def check_file(self, filename, path, lecture_id):
        """
        Checks, if the given file is the same like in est
        :type filename: str
        :type path: str
        :type lecture_id: str
        :param filename: the name of the file
        :param path: the path to the file locally
        :param lecture_id: the id of the lecture in est
        :return:
        """
        file_url = self.est_urls['base'] + '/' + self.parse_html_text(self.s.get(
            self.est_urls['check'].format(lec_id=lecture_id)).text, filename, "td").find_next("a").get('href')
        temp_file_path = "/tmp/" + filename
        self.download_file(file_url, temp_file_path)
        if cmp(path, temp_file_path, shallow=False):
            return 1
        else:
            return 0

    def check_status(self, filename, lecture_id):
        """
        Returns the status of a file on est
        :type filename: str
        :type lecture_id: str
        :param filename: the name of the file
        :param lecture_id: the id of the lecture in est
        :return: the status message from est for the file
        """
        name_tag = self.parse_html_text(self.s.get(
            self.est_urls['check'].format(lec_id=lecture_id)).text, filename, "td")
        if name_tag is not None:
            return name_tag.find_previous("span").get('title')

    def download_file(self, url, path):
        """
        Downloads a file from est to path
        :type url: str
        :type path: str
        :param url: the url in est
        :param path: the path where the file should be downloaded to on this pc
        :return:
        """
        # local_filename = url.split('/')[-1]
        r = self.s.get(url, stream=True)
        f = open(path, 'wb')
        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
        f.close()
        return

    def get_lecture_ids(self):
        """
        Returns the lecture ids of the logged in person
        :return: the lecture ids of the logged in person
        """
        ids = []
        for a in self.parse_html_id(self.s.get(self.est_urls['base']).text, 'estContent').find_all_next("a"):
            if 'index.html?lectureId' in a['href']:
                ids.append(a['href'].split('=')[1].split('&')[0])
                ids.append(a.next.strip())
        return list(OrderedDict.fromkeys(ids))

    def get_est_version(self):
        """
        Returns the current est version
        :return: the current est version
        """
        try:
            return self.parse_html_id(self.s.get(self.est_urls['base']).text, 'footermenu').find_next("li").text
        except requests.exceptions.ConnectionError:
            return '-1'

    def check_est_version(self):
        """
        Checks if the current est version is supported
        :return: True if the current est version is supported, else the est_version
        """
        est_version = self.get_est_version()
        return True if __est_version__ in est_version else est_version

    def get_submission_with(self, group_submission_code, lecture_id):
        """
        Returns the name of the group submission partner
        :type group_submission_code: str
        :type lecture_id: str
        :param group_submission_code: the code of the partner for group submission
        :param lecture_id: the id of the lecture in est
        :return: the name of the partner
        """
        return self.parse_html_text(self.s.get(
            self.est_urls['group'].format(lec_id=lecture_id)).text,
            group_submission_code, "span").previous_element[:-2].strip()

    def get_group_submission_code(self, filename, lecture_id):
        """
        Returns the group submission code for the file
        :param filename: the name of the file
        :param lecture_id: the id of the lecture in est
        :return: the group submission code for group submission for this file
        """
        element = self.parse_html_text(self.s.get(
            self.est_urls['group'].format(lec_id=lecture_id)).text, filename, 'td')
        if element is None:
            return ''
        while 'submissionGroupDynamicCode' not in str(element):
            if element.next_element is not None:
                element = element.next_element
            else:
                return ''
        return BeautifulSoup(str(element)).find('span', class_='submissionGroupDynamicCode').next_element

    @staticmethod
    def parse_html_id(html, html_id):
        """
        Returns the element with the first occurrence of the id in html
        :param html: the html of a website
        :param html_id: the id value of a html element
        :return: the html element
        """
        soup = BeautifulSoup(html)
        return soup.find(id=html_id)

    @staticmethod
    def parse_html_text(html, text, html_type):
        """

        :param html:
        :param text:
        :param html_type:
        :return:
        """
        soup = BeautifulSoup(html)
        return soup.find(html_type, text=text)

    @staticmethod
    def parse_html_find_all(html, html_type):
        """

        :param html:
        :param html_type:
        :return:
        """
        soup = BeautifulSoup(html)
        return soup.find_all(html_type)
