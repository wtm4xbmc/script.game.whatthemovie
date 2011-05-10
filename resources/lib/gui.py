import sys
import os
import datetime
import traceback
import xbmcgui
import xbmc
import whatthemovie


class GUI(xbmcgui.WindowXMLDialog):
    # Constants
    # CONTROL_IDs
    CID_BUTTON_GUESS = 3000
    CID_BUTTON_RANDOM = 3001
    CID_BUTTON_BACK = 3002
    CID_IMAGE_GIF = 1002
    CID_IMAGE_SOLUTION = 1006
    CID_IMAGE_MAIN = 1000
    CID_LABEL_LOGINSTATE = 1001
    CID_LABEL_SCORE = 1003
    CID_LABEL_POSTED_BY = 1004
    CID_LABEL_SOLVED = 1005
    CID_LABEL_SOLUTION = 1007
    CID_LABEL_SHOT_ID = 1008
    CID_LABEL_SHOT_DATE = 1011
    CID_LABEL_SHOT_TYPE = 1012
    CID_LIST_FLAGS = 1013

    # STRING_IDs
    #  Messages
    SID_LOGIN_FAILED_HEADING = 3050
    SID_LOGIN_FAILED = 3051
    SID_ENTER_ID = 3052
    SID_KEYBOARD_HEADING = 3053
    SID_ERROR_LOGIN = 3054
    SID_ERROR_SHOT = 3055
    SID_ERROR_GUESS = 3056
    #  Labels
    SID_CHECKING = 3100
    SID_ANSWER_RIGHT = 3101
    SID_ANSWER_WRONG = 3102
    SID_NOT_LOGGED_IN = 3103
    SID_LOGGED_IN_AS = 3104
    SID_YOUR_SCORE = 3105
    SID_SOLVED = 3106
    SID_UNSOLVED = 3107
    SID_SHOT_ID = 3108
    SID_SHOT_DATE = 3109
    SID_POSTED_BY = 3110
    SID_NOT_RELEASED = 3111
    SID_DEL_USER = 3112
    SID_NEW_SUBM = 3113
    SID_FEATURE_FILMS = 3114
    SID_THE_ARCHIVE = 3115
    #  Misc
    SID_DATE_FORMAT = 3300

    # ACTION_IDs
    AID_EXIT_BACK = [9, 10, 13]
    AID_CONTEXT_MENU = [117]

    # ADDON_CONSTANTS
    ADDON_ID = sys.modules['__main__'].__id__
    ADDON_VERSION = sys.modules['__main__'].__version__

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
        self.window_home = xbmcgui.Window(10000)
        self.setWTMProperty('solved_status', 'inactive')
        self.setWTMProperty('busy', 'loading')

    def onInit(self):
        # get XBMC Addon instance and methods
        Addon = sys.modules['__main__'].Addon
        self.getString = Addon.getLocalizedString
        self.getSetting = Addon.getSetting

        # get controls
        self.button_guess = self.getControl(self.CID_BUTTON_GUESS)
        self.button_random = self.getControl(self.CID_BUTTON_RANDOM)
        self.button_back = self.getControl(self.CID_BUTTON_BACK)
        self.label_loginstate = self.getControl(self.CID_LABEL_LOGINSTATE)
        self.label_score = self.getControl(self.CID_LABEL_SCORE)
        self.label_posted_by = self.getControl(self.CID_LABEL_POSTED_BY)
        self.label_solved = self.getControl(self.CID_LABEL_SOLVED)
        self.label_solution = self.getControl(self.CID_LABEL_SOLUTION)
        self.label_shot_id = self.getControl(self.CID_LABEL_SHOT_ID)
        self.label_shot_date = self.getControl(self.CID_LABEL_SHOT_DATE)
        self.label_shot_type = self.getControl(self.CID_LABEL_SHOT_TYPE)
        self.image_main = self.getControl(self.CID_IMAGE_MAIN)
        self.image_gif = self.getControl(self.CID_IMAGE_GIF)
        self.image_solution = self.getControl(self.CID_IMAGE_SOLUTION)
        self.list_flags = self.getControl(self.CID_LIST_FLAGS)

        # set control visibility depending on xbmc-addon settings
        self.hideLabels()

        # start the api
        user_agent = 'XBMC-ADDON - %s - V%s' % (self.ADDON_ID,
                                                self.ADDON_VERSION)
        self.Quiz = whatthemovie.WhatTheMovie(user_agent)
        # try to login and get first random shot. If it fails exit
        try:
            self.login()
            self.getRandomShot()
        except Exception, error:
            self.errorMessage(self.getString(self.SID_ERROR_LOGIN),
                              str(error))
            self.close()

    def onAction(self, action):
        if action in self.AID_EXIT_BACK:
            self.closeDialog()
        elif action in self.AID_CONTEXT_MENU:
            self.askShotID()
        #else:
        #    print action.getId()

    def askShotID(self):
        Dialog = xbmcgui.Dialog()
        shot_id = Dialog.numeric(0, self.getString(self.SID_ENTER_ID))
        if shot_id and shot_id is not '':
            self.getShot(shot_id)

    def onFocus(self, controlId):
        pass

    def onClick(self, controlId):
        if controlId == self.CID_BUTTON_GUESS:
            self.guessTitle(self.shot['shot_id'])
        elif controlId == self.CID_BUTTON_RANDOM:
            self.setWTMProperty('solved_status', 'inactive')
            self.getRandomShot()
        elif controlId == self.CID_BUTTON_BACK:
            self.getShot('last')

    def closeDialog(self):
        self.setWTMProperty('main_image', '')
        self.close()

    def getRandomShot(self):
        self.getShot()

    def getShot(self, shot_id=None):
        # set busy_gif
        self.setWTMProperty('busy', 'loading')
        # scrape shot and download picture
        try:
            if shot_id:
                if shot_id.isdigit():
                    shot = self.Quiz.getShot(shot_id)
                elif shot_id == 'last':
                    shot = self.Quiz.getLastShot()
            else:
                shot = self.Quiz.getRandomShot()
            self.shot = shot
            local_image_path = self.downloadPic(shot['image_url'],
                                                shot['shot_id'])
        except Exception, error:
            self.errorMessage(self.getString(self.SID_ERROR_SHOT),
                              str(error))
            self.setWTMProperty('busy', '')
            return
        # set label shot_type
        if shot['shot_type'] == 1:
            shot_type = self.getString(self.SID_NEW_SUBM)
        elif shot['shot_type'] == 2:
            shot_type = self.getString(self.SID_FEATURE_FILMS)
        elif shot['shot_type'] == 3:
            shot_type = self.getString(self.SID_THE_ARCHIVE)
        self.label_shot_type.setLabel(shot_type)
        # set picture
        self.setWTMProperty('main_image', local_image_path)
        # set label posted_by
        if shot['posted_by']:
            user = shot['posted_by']
        else:
            user = self.getString(self.SID_DEL_USER)
        self.label_posted_by.setLabel(self.getString(self.SID_POSTED_BY)
                                      % user)
        # set label solved
        if shot['solved']['status']:
            self.label_solved.setLabel(self.getString(self.SID_SOLVED)
                                       % (shot['solved']['count'],
                                          shot['solved']['first_by']))
        else:
            self.label_solved.setLabel(self.getString(self.SID_UNSOLVED))
        # set label shot_id
        self.label_shot_id.setLabel(self.getString(self.SID_SHOT_ID)
                                    % shot['shot_id'])
        # set label shot_date
        date = shot['date']
        if date:
            date_format = str(self.getString(self.SID_DATE_FORMAT))
            date_string = date.strftime(date_format)
        else:
            date_string = self.getString(self.SID_NOT_RELEASED)
        self.label_shot_date.setLabel(self.getString(self.SID_SHOT_DATE)
                                      % date_string)
        # set shot languages
        languages = shot['lang_list']['main']
        # languages = shot['lang_list']['main'] + shot['lang_list']['hidden']
        self.addFlags(languages)
        # unset busy_gif
        self.setWTMProperty('busy', '')

    def addFlags(self, language_list):
        self.list_flags.reset()
        avail_flags = ('am', 'bg', 'cn', 'de', 'dk', 'en', 'es', 'et', 'fi',
                       'fr', 'gr', 'hu', 'il', 'in', 'is', 'it', 'jp', 'kr',
                       'lt', 'lv', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'se',
                       'tr', 'ua')
        for language in (l for l in language_list if l in avail_flags):
            flag_img = 'flags/%s.png' % language
            flag_item = xbmcgui.ListItem(iconImage=flag_img)
            self.list_flags.addItem(flag_item)

    def guessTitle(self, shot_id):
        # clear solved_status
        self.setWTMProperty('solved_status', 'inactive')
        # open xbmc keyboard
        heading = self.getString(self.SID_KEYBOARD_HEADING)
        keyboard = xbmc.Keyboard('', heading)
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText() is not '':
            guess = keyboard.getText().decode('utf8')
            # enter checking status            
            self.image_solution.setColorDiffuse('FFFFFF00')
            self.setWTMProperty('solved_status', 'checking')
            message = self.getString(self.SID_CHECKING)
            self.label_solution.setLabel(message % guess)
            # try to check the guess. If it fails abort checking
            try:
                answer = self.Quiz.guessShot(guess, shot_id)
            except Exception, error:
                self.errorMessage(self.getString(self.SID_ERROR_GUESS),
                                  str(error))
                self.setWTMProperty('solved_status', 'inactive')
                return
            # call answerRight or answerWrong
            if answer['is_right'] == True:
                self.answerRight(answer['title_year'],
                                 self.shot['gives_point'])
            else:
                self.answerWrong(guess)

    def answerRight(self, title_year, gives_point):
        # enter right status 
        message = self.getString(self.SID_ANSWER_RIGHT)
        self.label_solution.setLabel(message % title_year)
        self.setWTMProperty('solved_status', 'correct')
        self.image_solution.setColorDiffuse('FF00FF00')
        # if this shout gives points, do so
        if gives_point:
            self.score += 1
            self.updateScore()
        # if user wants auto_random, do so
        if self.getSetting('auto_random') == 'true':
            time_to_sleep = int(self.getSetting('auto_random_sleep')) * 1000
            xbmc.sleep(time_to_sleep)
            self.getRandomShot()
        self.setWTMProperty('solved_status', 'inactive')  # fixme

    def answerWrong(self, guess):
        # enter wrong status
        message = self.getString(self.SID_ANSWER_WRONG)
        self.label_solution.setLabel(message % guess)
        self.setWTMProperty('solved_status', 'wrong')
        self.image_solution.setColorDiffuse('FFFF0000')

    def login(self):
        self.score = 0
        # if login disabled skip, if not login and get user score
        if self.getSetting('login') == 'false':
            label = self.getString(self.SID_NOT_LOGGED_IN)
            self.label_loginstate.setLabel(label)
        else:
            cookie_dir = 'special://profile/addon_data/%s' % self.ADDON_ID
            self.checkCreatePath(cookie_dir)
            cookie_file = xbmc.translatePath('%s/cookie.txt' % cookie_dir)
            user = self.getSetting('username')
            password = self.getSetting('password')
            options = self.getOptions()
            # do the login
            success = self.Quiz.login(user, password, cookie_file, options)
            if success == False:
                # login failed
                dialog = xbmcgui.Dialog()
                dialog.ok(self.getString(self.SID_LOGIN_FAILED_HEADING),
                          self.getString(self.SID_LOGIN_FAILED) % user)
                label = self.getString(self.SID_NOT_LOGGED_IN)
            else:
                # login successfully
                label = self.getString(self.SID_LOGGED_IN_AS) % user
                self.score = int(self.Quiz.getScore(user))
            self.label_loginstate.setLabel(label)
        # show the score
        self.updateScore()

    def getOptions(self):
        options = dict()
        if self.getSetting('difficulty') == '2':  # 'all'
            options['difficulty'] = 'all'
        elif self.getSetting('difficulty') == '1':  # 'medium'
            options['difficulty'] = 'medium'
        elif self.getSetting('difficulty') == '0':  # 'easy'
            options['difficulty'] = 'easy'
        if self.getSetting('include_archive') == 'true':
            options['include_archive'] = '1'
        else:
            options['include_archive'] = '0'
        if self.getSetting('include_solved') == 'true':
            options['include_solved'] = '1'
        else:
            options['include_solved'] = '0'
        return options

    def downloadPic(self, image_url, shot_id):
        subst_image_url = 'http://static.whatthemovie.com/images/substitute'
        if not image_url.startswith(subst_image_url):
            cache_dir = ('special://profile/addon_data/%s/cache'
                         % self.ADDON_ID)
            self.checkCreatePath(cache_dir)
            image_path = xbmc.translatePath('%s/%s.jpg' % (cache_dir, shot_id))
            if not os.path.isfile(image_path):
                self.Quiz.downloadFile(image_url, image_path)
        else:
            image_path = image_url
        return image_path

    def updateScore(self):
        score_string = self.getString(self.SID_YOUR_SCORE) % str(self.score)
        self.label_score.setLabel(score_string)

    def checkCreatePath(self, path):
        result = False
        if os.path.isdir(xbmc.translatePath(path)):
            result = True
        else:
            result = os.makedirs(xbmc.translatePath(path))
        return result

    def setWTMProperty(self, prop, value):
        self.window_home.setProperty('wtm.%s' % prop, value)

    def hideLabels(self):
        if self.getSetting('visible_posted_by') == 'false':
            self.label_posted_by.setVisible(False)
        if self.getSetting('visible_solved') == 'false':
            self.label_solved.setVisible(False)
        if self.getSetting('visible_shot_id') == 'false':
            self.label_shot_id.setVisible(False)
        if self.getSetting('visible_shot_date') == 'false':
            self.label_shot_date.setVisible(False)
        if self.getSetting('visible_shot_flags') == 'false':
            self.list_flags.setVisible(False)

    def errorMessage(self, heading, error):
        print 'ERROR: %s: %s ' % (heading, str(error))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print 'TRACEBACK:' + repr(traceback.format_exception(exc_type,
                                                             exc_value,
                                                             exc_traceback))
        dialog = xbmcgui.Dialog()
        dialog.ok(heading, error)
