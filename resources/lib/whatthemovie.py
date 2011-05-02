# WhatTheMovie Python Class
# Copyright (C) Tristan 'sphere' Fischer 2011

from mechanize import Browser, LWPCookieJar
from BeautifulSoup import BeautifulSoup
from time import strptime


class WhatTheMovie:

    MAIN_URL = 'http://whatthemovie.com'

    def __init__(self):
        # Get browser stuff
        self.cookies = LWPCookieJar()
        self.browser = Browser()
        self.browser.set_cookiejar(self.cookies)
        # Set empty returns
        self.is_login = False
        self.shot = dict()
        self.username = None
        self.score = None
        self.answer = None

    def _checkLogin(self, url=None):
        self.is_login = False
        if url is not None:
            self.browser.open(url)
        try:
            html = self.browser.response().read()
        except:
            self.browser.open(self.MAIN_URL)
            html = self.browser.response().read()
        tree = BeautifulSoup(html)
        if tree.find('a', href='http://whatthemovie.com/user/logout'):
            self.is_login = True
        return self.is_login

    def login(self, user, password, cookie_path):
        login_url = '%s/user/login/' % self.MAIN_URL
        try:
            self.cookies.revert(cookie_path)
            # cookie found
        except:
            # no cookie found
            pass
        if self._checkLogin(login_url):
            # logged in via cookie
            self.username = user
        else:
            # need to login
            self.browser.select_form(nr=0)
            self.browser['name'] = user
            self.browser['upassword'] = password
            self.browser.submit()
            if self._checkLogin(login_url):
                # logged in via auth
                self.cookies.save(cookie_path)
                self.username = user
            else:
                # could not log in
                pass
        return self.is_login

    def getRandomShot(self):
        return self.getShot('random')

    def getShot(self, shot_id):
        self.shot = dict()
        random_url = '%s/shot/%s' % (self.MAIN_URL, shot_id)
        self.browser.open(random_url)
        html = self.browser.response().read()
        tree = BeautifulSoup(html)
        shot_id = tree.find('li', attrs={'class': 'number'}).string.strip()
        image_url = tree.find('img', alt='guess this movie snapshot')['src']
        lang_list = list()
        section = tree.find('ul', attrs={'class': 'language_flags'})
        langs = section.findAll(lambda tag: len(tag.attrs) == 0)
        for lang in langs:
            lang_list.append(str(lang.img['alt'])[:-6])

        date_info = tree.find('ul',
                              attrs={'class': 'nav_date'}).findAll('li')
        struct_date = strptime('%s %s %s' % (date_info[1].a.string,
                                             date_info[2].a.string,
                                             date_info[3].a.string[:-2]),
                               '%Y %B %d')
        sections = tree.find('ul',
                             attrs={'class': 'nav_shotinfo'}).findAll('li')
        posted_by = sections[0].a.string
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
        self.shot['shot_id'] = shot_id
        self.shot['image_url'] = image_url
        self.shot['lang_list'] = lang_list
        self.shot['posted_by'] = posted_by
        self.shot['solved'] = solved
        self.shot['struct_date'] = struct_date
        # fixme, only for debug
        print 'debug languages: %s' % str(self.shot['lang_list'])
        return self.shot

    def guessShot(self, title_guess, shot_id=None):
        self.answer = dict()
        self.answer['is_right'] = False
        if not shot_id:
            shot_id = self.shot['shot_id']
        post_url = '%s/shot/%s/guess' % (self.MAIN_URL, shot_id)
        self.browser.open(post_url, 'guess=%s' % title_guess)
        response = self.browser.response().read()
        response_c = response.replace('&amp;', '&').decode('unicode-escape')
        # fixme, only for debug (find html entities)
        print 'debug response: ' + response_c
        # ['right'|'wrong']
        if response_c[6:11] == 'right':
            self.answer['is_right'] = True
            self.answer['title_year'] = response_c.split('"')[3]
        return self.answer

    def getScore(self, username=None):
        self.score = 0
        if not username:
            # No username given trying logged in user
            if not self.username:
                # Not logged in
                return self.score
            else:
                username = self.username
        profile_url = '%s/user/%s/' % (self.MAIN_URL, username)
        self.browser.open(profile_url)
        html = self.browser.response().read()
        tree = BeautifulSoup(html)
        box = tree.find('div', attrs={'class': 'box_white'})
        self.score = box.p.strong.string[0:-13]
        return self.score
