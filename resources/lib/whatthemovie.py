# WhatTheMovie Python Class
# Copyright (C) Tristan 'sphere' Fischer 2011

from mechanize import Browser, LWPCookieJar, Request
from urllib import urlencode
from BeautifulSoup import BeautifulSoup
from time import strptime, mktime
from datetime import datetime, timedelta
from re import compile, search


class WhatTheMovie:

    MAIN_URL = 'http://whatthemovie.com'

    def __init__(self, user-agent):
        # Get browser stuff
        self.cookies = LWPCookieJar()
        self.browser = Browser()
        self.browser.set_cookiejar(self.cookies)
        self.browser.addheaders = [('user-agent', user_agent)]        
        # Set empty returns
        self.shot = dict()
        self.last_shots = list()

    def _checkLogin(self, url=None):
        is_login = False
        if url is not None:
            self.browser.open(url)
        try:
            html = self.browser.response().read()
        except:
            self.browser.open(self.MAIN_URL)
            html = self.browser.response().read()
        tree = BeautifulSoup(html)
        if tree.find('a', href='http://whatthemovie.com/user/logout'):
            is_login = True
        return is_login

    def login(self, user, password, cookie_path, options=None):
        is_login = False
        login_url = '%s/user/login/' % self.MAIN_URL
        try:
            self.cookies.revert(cookie_path)
            # cookie found
        except:
            # no cookie found
            pass
        is_login = self._checkLogin(login_url)
        if not is_login:
            # need to login
            self.browser.select_form(nr=0)
            self.browser['name'] = user
            self.browser['upassword'] = password
            self.browser.submit()
            is_login = self._checkLogin(login_url)
            if is_login:
                # logged in via auth
                self.cookies.save(cookie_path)
            else:
                # could not log in
                pass
        if is_login:
            if options and len(options) > 0:
                    self.setOptions(options)
        return is_login

    def setOptions(self, options_dict):
        option_url = '%s/shot/setrandomoptions' % self.MAIN_URL
        if options_dict['include_archive'] == '0':
            options_dict.pop('include_archive')
        if options_dict['include_solved'] == '0':
            options_dict.pop('include_solved')
        self._sendAjaxReq(option_url, options_dict)

    def _sendAjaxReq(self, url, data_dict=None):
        if data_dict:
            post_data = urlencode(data_dict)
        else:
            post_data = ' '
        req = Request(url, post_data)
        req.add_header('Accept', 'text/javascript, */*')
        req.add_header('Content-Type',
                       'application/x-www-form-urlencoded; charset=UTF-8')
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        self.browser.open(req)

    def getRandomShot(self):
        return self.getShot('random')

    def getLastShot(self):
        if len(self.last_shots) > 0:
            self.shot = self.last_shots.pop()
        return self.shot

    def getShot(self, shot_id):
        if self.shot:  # if there is already a shot - put it in list
            self.last_shots.append(self.shot)
        self.shot = dict()
        shot_url = '%s/shot/%s' % (self.MAIN_URL, shot_id)
        self.browser.open(shot_url)
        html = self.browser.response().read()
        tree = BeautifulSoup(html)
        # id
        shot_id = tree.find('li', attrs={'class': 'number'}).string.strip()
        # image url
        image_url = tree.find('img', alt='guess this movie snapshot')['src']
        # languages
        lang_list = dict()
        lang_list['main'] = list()
        lang_list['hidden'] = list()
        section = tree.find('ul', attrs={'class': 'language_flags'})
        langs_main = section.findAll(lambda tag: len(tag.attrs) == 0)
        for lang in langs_main:
            if lang.img:
                lang_list['main'].append(lang.img['src'][-6:-4])
        langs_hidden = section.findAll('li',
                                       attrs={'class': 'hidden_languages'})
        for lang in langs_hidden:
            if lang.img:
                lang_list['hidden'].append(lang.img['src'][-6:-4])
        # date
        date = None
        date_info = tree.find('ul',
                              attrs={'class': 'nav_date'}).findAll('li')
        if len(date_info) >= 4:
            struct_date = strptime('%s %s %s' % (date_info[1].a.string,
                                                 date_info[2].a.string,
                                                 date_info[3].a.string[:-2]),
                                   '%Y %B %d')
            date = datetime.fromtimestamp(mktime(struct_date))
        # posted by
        sections = tree.find('ul',
                             attrs={'class': 'nav_shotinfo'}).findAll('li')
        try:
            posted_by = sections[0].a.string
        except:
            posted_by = ''  # fixme: catch deleted accounts (not in a.string)
        # solved
        solved = dict()
        try:
            solved_string, solved_count = sections[1].string[8:].split()
            if solved_string == 'solved':
                solved['status'] = True
                solved['count'] = int(solved_count.strip('()'))
        except:
            solved['status'] = False
            solved['count'] = 0
        try:
            solved['first_by'] = sections[2].a.string
        except:
            solved['first_by'] = 'nobody'
        # gives_point
        js_list = tree.findAll('script',
                               attrs={'type': 'text/javascript'},
                               text=compile('guess_problem'))
        if len(js_list) == 0 and date:
            # at least no guess_problem
            gives_point = True
            age = datetime.now() - date
            if age > timedelta(days=30):
                # from archive
                gives_point = False
        else:
            # already solved
            gives_point = False
        # voting
        voting = dict()
        section = tree.find('script',
                            attrs={'type': 'text/javascript'},
                            text=compile('tt_shot_rating_stars'))
        r = '<strong>(?P<rating>[0-9.]+|hidden)</strong> \((?P<votes>[0-9]+)'
        if section:
            voting = search(r, section).groupdict()
        # tags
        tags = list()
        tags_list = tree.find('ul', attrs={'id':
                                           'shot_tag_list'}).findAll('li')
        for tag in tags_list:
            if tag.a:
                tags.append(tag.a.string)
        # create return dict
        self.shot['shot_id'] = shot_id
        self.shot['image_url'] = image_url
        self.shot['lang_list'] = lang_list
        self.shot['posted_by'] = posted_by
        self.shot['solved'] = solved
        self.shot['date'] = date
        self.shot['gives_point'] = gives_point
        self.shot['voting'] = voting
        self.shot['tags'] = tags
        return self.shot

    def downloadFile(self, url, local_path):
        self.browser.retrieve(url, local_path, )

    def guessShot(self, title_guess, shot_id=None):
        answer = dict()
        answer['is_right'] = False
        if not shot_id:
            shot_id = self.shot['shot_id']
        post_url = '%s/shot/%s/guess' % (self.MAIN_URL, shot_id)
        post_data = urlencode({'guess': title_guess.encode('utf8')})
        self.browser.open(post_url, post_data)
        response = self.browser.response().read()
        response_c = response.replace('&amp;', '&').decode('unicode-escape')
        # ['right'|'wrong']
        if response_c[6:11] == 'right':
            answer['is_right'] = True
            answer['title_year'] = response_c.split('"')[3]
        return answer

    def getScore(self, username):
        score = 0
        profile_url = '%s/user/%s/' % (self.MAIN_URL, username)
        self.browser.open(profile_url)
        html = self.browser.response().read()
        tree = BeautifulSoup(html)
        box = tree.find('div', attrs={'class': 'box_white'})
        score = box.p.strong.string[0:-13]
        return score
