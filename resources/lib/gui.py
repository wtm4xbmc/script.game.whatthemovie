import sys
import os
import datetime
import traceback
import xbmcgui
import xbmc
import whatthemovie


class GUI(xbmcgui.WindowXMLDialog):
    # Constants
    RATING_STAR_WIDTH = 18
    RATING_STAR_DISTANCE = 10
    RATING_STAR_POSX = 3

    # CONTROL_IDs
    CID_BUTTON_GUESS = 3000
    CID_BUTTON_RANDOM = 3001
    CID_BUTTON_BACK = 3002
    CID_BUTTON_FIRST = 3004
    CID_BUTTON_PREV = 3005
    CID_BUTTON_NEXT = 3006
    CID_BUTTON_LAST = 3007
    CID_BUTTON_FAV = 3008
    CID_BUTTON_BOOKMARK = 3009
    CID_BUTTON_SOLUTION = 3010
    CID_BUTTON_JUMP = 3011
    CID_IMAGE_GIF = 1002
    CID_IMAGE_SOLUTION = 1006
    CID_IMAGE_MAIN = 1000
    CID_IMAGE_STARS = 1015
    CID_LABEL_LOGINSTATE = 1001
    CID_LABEL_SCORE = 1003
    CID_LABEL_POSTED_BY = 1004
    CID_LABEL_SOLVED = 1005
    CID_LABEL_SOLUTION = 1007
    CID_LABEL_SHOT_ID = 1008
    CID_LABEL_SHOT_DATE = 1011
    CID_LABEL_SHOT_TYPE = 1012
    CID_LABEL_RATING = 1014
    CID_LIST_FLAGS = 1013
    CID_GROUP_RATING = 1016

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
    SID_OVERALL_RATING = 3116
    SID_OWN_RATING = 3117
    SID_RATING_HIDDEN = 3118
    SID_RATING_UNRATED = 3119
    SID_REJECTED_SHOT = 3120
    SID_ALREADY_SOLVED = 3121
    #  Misc
    SID_DATE_FORMAT = 3300

    # ACTION_IDs
    AID_EXIT_BACK = [9, 10, 13]
    AID_CONTEXT_MENU = [117]
    AID_NUMBERS = [59, 60, 61, 62, 63,
                   64, 65, 66, 67, 58]

    # ADDON_CONSTANTS
    ADDON_ID = sys.modules['__main__'].__id__
    ADDON_VERSION = sys.modules['__main__'].__version__

    def __init__(self, xmlFilename, scriptPath, defaultSkin, defaultRes):
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
        self.label_rating = self.getControl(self.CID_LABEL_RATING)
        self.image_main = self.getControl(self.CID_IMAGE_MAIN)
        self.image_gif = self.getControl(self.CID_IMAGE_GIF)
        self.image_solution = self.getControl(self.CID_IMAGE_SOLUTION)
        self.image_stars = self.getControl(self.CID_IMAGE_STARS)
        self.list_flags = self.getControl(self.CID_LIST_FLAGS)
        self.group_rating = self.getControl(self.CID_GROUP_RATING)

        # set control visibility depending on xbmc-addon settings
        self.hideLabels()

        # start the api
        user_agent = 'XBMC-ADDON - %s - V%s' % (self.ADDON_ID,
                                                self.ADDON_VERSION)
        self.Quiz = whatthemovie.WhatTheMovie(user_agent)
        # try to login and get first random shot. If it fails exit
        try:
            self.login()
            self.getShot('random')
        except Exception, error:
            self.errorMessage(self.getString(self.SID_ERROR_LOGIN),
                              str(error))
            self.close()

    def onAction(self, action):
        if action in self.AID_EXIT_BACK:
            self.closeDialog()
        elif action in self.AID_CONTEXT_MENU:
            self.askShotID()
        elif action in self.AID_NUMBERS:
            user_rate = self.AID_NUMBERS.index(action.getId()) + 1
            self.rateShot(self.shot['shot_id'], user_rate)
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
            self.getShot('random')
        elif controlId == self.CID_BUTTON_BACK:
            self.getShot('last')
        elif controlId == self.CID_BUTTON_FIRST:
            self.getShot('first')
        elif controlId == self.CID_BUTTON_LAST:
            self.getShot('last')
        elif controlId == self.CID_BUTTON_FAV:
            self.favouriteShot(self.shot['shot_id'])
        elif controlId == self.CID_BUTTON_BOOKMARK:
            self.bookmarkShot(self.shot['shot_id'])
        elif controlId == self.CID_BUTTON_SOLUTION:
            self.solveShot(self.shot['shot_id'])
        elif controlId == self.CID_BUTTON_JUMP:
            self.askShotID()
        elif controlId in (self.CID_BUTTON_PREV, self.CID_BUTTON_NEXT):
            if self.getSetting('only_unsolved_nav') == 'true':
                unsolved_toggle = '_unsolved'
            else:
                unsolved_toggle = ''
            if controlId == self.CID_BUTTON_PREV:
                self.getShot('prev' + unsolved_toggle)
            elif controlId == self.CID_BUTTON_NEXT:
                self.getShot('next' + unsolved_toggle)

    def closeDialog(self):
        self.setWTMProperty('main_image', '')
        self.close()

    def getShot(self, shot_id=None):
        # set busy_gif
        self.setWTMProperty('busy', 'loading')
        # hide label_status
        self.setWTMProperty('solved_status', 'inactive')
        # scrape shot and download picture
        try:
            self.shot = self.Quiz.getShot(shot_id)
            shot = self.shot
            image_path = self.downloadPic(shot['image_url'],
                                          shot['shot_id'])
        except Exception, error:
            self.errorMessage(self.getString(self.SID_ERROR_SHOT),
                              str(error))
            self.setWTMProperty('busy', '')
            return
        self._showShotImage(image_path)
        self._showShotType(shot['shot_type'])
        self._showShotPostedBy(shot['posted_by'])
        self._showShotSolvedStatus(shot['solved'])
        self._showShotAlreadSolved(shot['already_solved'])
        self._showShotID(shot['shot_id'])
        self._showShotDate(shot['date'])
        self._showShotFlags(shot['lang_list']['all'])
        self._showShotRating(shot['voting'])
        self._showShotButtonState('favourite', shot['favourite'])
        self._showShotButtonState('bookmarked', shot['bookmarked'])
        self._showSolvableState(shot['solvable'])
        # unset busy_gif
        self.setWTMProperty('busy', '')

    def _showShotType(self, shot_type):
        if shot_type == 0:
            type_string = 'FIND ME PLEASE'
        elif shot_type == 1:
            type_string = self.getString(self.SID_NEW_SUBM)
        elif shot_type == 2:
            type_string = self.getString(self.SID_FEATURE_FILMS)
        elif shot_type == 3:
            type_string = self.getString(self.SID_THE_ARCHIVE)
        elif shot_type == 4:
            type_string = self.getString(self.SID_REJECTED_SHOT)
        self.label_shot_type.setLabel(type_string)

    def _showShotPostedBy(self, posted_by=None):
        if posted_by is None:
            posted_by = self.getString(self.SID_DEL_USER)
        self.label_posted_by.setLabel(self.getString(self.SID_POSTED_BY)
                                      % posted_by)

    def _showShotSolvedStatus(self, solved_status):
        if solved_status['status']:
            self.label_solved.setLabel(self.getString(self.SID_SOLVED)
                                       % (solved_status['count'],
                                          solved_status['first_by']))
        else:
            self.label_solved.setLabel(self.getString(self.SID_UNSOLVED))

    def _showShotAlreadSolved(self, alread_solved):
        if alread_solved:
            self.image_solution.setColorDiffuse('FFFFFFFF')
            self.label_solution.setLabel(self.getString(self.SID_ALREADY_SOLVED))
            self.setWTMProperty('solved_status', 'solved')

    def _showShotID(self, shot_id):
        self.label_shot_id.setLabel(self.getString(self.SID_SHOT_ID)
                                    % shot_id)

    def _showShotDate(self, date):
        if date is not None:
            date_format = str(self.getString(self.SID_DATE_FORMAT))
            date_string = date.strftime(date_format)
        else:
            date_string = self.getString(self.SID_NOT_RELEASED)
        self.label_shot_date.setLabel(self.getString(self.SID_SHOT_DATE)
                                      % date_string)

    def _showShotRating(self, rating):
        if rating['overall_rating'] != u'hidden':
            overall_rating = rating['overall_rating']
            self._setRatingStarsImageWidth(float(overall_rating))
        else:
            overall_rating = self.getString(self.SID_RATING_HIDDEN)
        if rating['own_rating'] is not None:
            own_rating = rating['own_rating']
        else:
            own_rating = self.getString(self.SID_RATING_UNRATED)
        votes = rating['votes']
        rating_string = '[CR]'.join((self.getString(self.SID_OVERALL_RATING),
                                     self.getString(self.SID_OWN_RATING)))
        self.label_rating.setLabel(rating_string % (overall_rating,
                                                    votes,
                                                    own_rating))

    def _setRatingStarsImageWidth(self, rating):
        rating_intervals = int(rating)
        rating_stars_width = (self.RATING_STAR_WIDTH * rating)
        rating_gaps_width = (self.RATING_STAR_DISTANCE * rating_intervals)
        rating_width = (self.RATING_STAR_POSX + rating_stars_width +
                        rating_gaps_width)
        self.image_stars.setWidth(int(rating_width + 0.5))

    def _showShotFlags(self, language_list):
        visible_flags = list()
        for i in (1, 2, 3, 4, 5):
            visible_flags.append(self.getSetting('flag%s' % i))
        self.list_flags.reset()
        for flag in visible_flags:
            flag_img = 'flags/%s.png' % flag
            flag_item = xbmcgui.ListItem(iconImage=flag_img)
            if flag not in language_list:
                flag_item.setProperty('unavailable', 'True')
            self.list_flags.addItem(flag_item)

    def _showShotImage(self, image_path):
        self.setWTMProperty('main_image', image_path)

    def _showShotButtonState(self, prop, state):
        if prop == 'favourite':
            element = self.getControl(self.CID_BUTTON_FAV)
        elif prop == 'bookmarked':
            element = self.getControl(self.CID_BUTTON_BOOKMARK)
        if state is None:
            element.setEnabled(False)
            element.setSelected(False)
        elif state == False:
            element.setEnabled(True)
            element.setSelected(False)
        elif state == True:
            element.setEnabled(True)
            element.setSelected(True)

    def _showSolvableState(self, state):
        element = self.getControl(self.CID_BUTTON_SOLUTION)
        if state == True:
            element.setEnabled(True)
            element.setSelected(True)
        else:
            element.setEnabled(False)
            element.setSelected(False)

    def _showUserScore(self, score):
        score_string = self.getString(self.SID_YOUR_SCORE) % str(score)
        self.label_score.setLabel(score_string)

    def rateShot(self, shot_id, own_rating):
        try:
            self.Quiz.rateShot(shot_id, own_rating)
            rating = self.shot['voting']
            self._showShotRating(rating)
        except Exception, error:
            self.errorMessage(self.getString(self.SID_ERROR_SHOT),
                              str(error))

    def favouriteShot(self, shot_id):
        state = self.shot['favourite']
        if state == True:
            newstate = False
        else:
            newstate = True
        try:
            self.Quiz.favouriteShot(shot_id, newstate)
            self._showShotButtonState('favourite', newstate)
        except Exception, error:
            self.errorMessage(self.getString(self.SID_ERROR_SHOT),
                              str(error))

    def bookmarkShot(self, shot_id):
        state = self.shot['bookmarked']
        if state == True:
            newstate = False
        else:
            newstate = True
        try:
            self.Quiz.bookmarkShot(shot_id, newstate)
            self._showShotButtonState('bookmarked', newstate)
        except Exception, error:
            self.errorMessage(self.getString(self.SID_ERROR_SHOT),
                              str(error))

    def solveShot(self, shot_id):
        try:
            solved_title = self.Quiz.solveShot(shot_id)
            print solved_title
            # fixme: show solved_title
        except Exception, error:
            self.errorMessage(self.getString(self.SID_ERROR_SHOT),
                              str(error))

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
                solution = self.Quiz.guessShot(guess, shot_id)
            except Exception, error:
                self.errorMessage(self.getString(self.SID_ERROR_GUESS),
                                  str(error))
                self.setWTMProperty('solved_status', 'inactive')
                return
            # call answerRight or answerWrong
            if solution['is_right'] == True:
                self.answerRight(solution['title_year'],
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
        if gives_point == True:
            self.score += 1
            self._showUserScore(self.score)
        # if user wants auto_jump, do so
        if self.getSetting('auto_jump_enabled') == 'true':
            time_to_sleep = int(self.getSetting('auto_jump_sleep')) * 1000
            xbmc.sleep(time_to_sleep)
            if self.getSetting('auto_jump_to') == '0':
                jump_to = 'random'
            elif self.getSetting('auto_jump_to') == '1':
                jump_to = 'next'
            self.getShot(jump_to)

    def answerWrong(self, guess):
        # enter wrong status
        message = self.getString(self.SID_ANSWER_WRONG)
        self.label_solution.setLabel(message % guess)
        self.setWTMProperty('solved_status', 'wrong')
        self.image_solution.setColorDiffuse('FFFF0000')

    def login(self):
        self.score = 0
        # if login disabled skip, else login and get user score
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
        self._showUserScore(self.score)

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
        if self.getSetting('visible_shot_rating') == 'false':
            self.label_rating.setVisible(False)
            self.group_rating.setVisible(False)
        if self.getSetting('visible_tool_buttons') == 'false':
            controls = (self.CID_BUTTON_FAV, self.CID_BUTTON_BOOKMARK, 
                        self.CID_BUTTON_SOLUTION, self.CID_BUTTON_JUMP)
            for control in controls:
                self.getControl(control).setVisible(False)

    def errorMessage(self, heading, error):
        print 'ERROR: %s: %s ' % (heading, str(error))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print 'TRACEBACK:' + repr(traceback.format_exception(exc_type,
                                                             exc_value,
                                                             exc_traceback))
        dialog = xbmcgui.Dialog()
        dialog.ok(heading, error)
