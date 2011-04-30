import sys
import os
import urllib
import xbmcgui
import xbmc
import whatthemovie

getString = sys.modules['__main__'].getLocalizedString
getSetting = sys.modules['__main__'].getSetting


class GUI(xbmcgui.WindowXMLDialog):
    # Constants
    # CONTROL_IDs
    CID_BUTTON_GUESS = 3000
    CID_BUTTON_RANDOM = 3001
    CID_BUTTON_EXIT = 3002
    CID_IMAGE_MAIN = 1000
    CID_IMAGE_GIF = 1002
    CID_LABEL_STATE = 1001
    CID_LABEL_SCORE = 1003
    CID_LABEL_POSTED_BY = 1004
    CID_LABEL_SOLVED = 1005
    CID_LABEL_SOLUTION = 1006

    # STRING_IDs
    SID_GUESS = 3100
    SID_RANDOM = 3101
    SID_EXIT = 3102
    SID_ANSWER_RIGHT = 3103
    SID_ANSWER_WRONG = 3104
    SID_KEYBOARD_HEADING = 3105
    SID_NOT_LOGGED_IN = 3106
    SID_LOGGED_IN_AS = 3107
    SID_LOGIN_FAILED_HEADING = 3108
    SID_LOGIN_FAILED = 3109
    SID_YOUR_SCORE = 3110
    SID_POSTED_BY = 3203
    SID_SOLVED = 3204
    SID_UNSOLVED = 3205
    SID_SOLUTION = 3206

    # ACTION_IDs
    AID_EXIT_BACK = [10, 13]

    def __init__(self, *args, **kwargs):
        # __init__ will be called when python creates object from this class
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)

    def onInit(self):
        # onInit will be called from xbmc (after __init__)
        # store xbmc keycodes for exit and backspace
        self.startApi()

        # get controls
        self.button_guess = self.getControl(self.CID_BUTTON_GUESS)
        self.button_random = self.getControl(self.CID_BUTTON_RANDOM)
        self.button_exit = self.getControl(self.CID_BUTTON_EXIT)
        self.label_state = self.getControl(self.CID_LABEL_STATE)
        self.label_score = self.getControl(self.CID_LABEL_SCORE)
        self.label_posted_by = self.getControl(self.CID_LABEL_POSTED_BY)
        self.label_solved =  self.getControl(self.CID_LABEL_SOLVED)
        self.label_solution =  self.getControl(self.CID_LABEL_SOLUTION)
        self.image_main = self.getControl(self.CID_IMAGE_MAIN)
        self.image_gif = self.getControl(self.CID_IMAGE_GIF)

        # translate buttons
        self.button_guess.setLabel(getString(self.SID_GUESS))
        self.button_random.setLabel(getString(self.SID_RANDOM))
        self.button_exit.setLabel(getString(self.SID_EXIT))

        # start the api
        self.login()
        self.getRandomShot()

    def startApi(self):
        script_id = sys.modules['__main__'].__id__
        cookie_dir = 'special://profile/addon_data/%s' % script_id
        self.createCheckPath(cookie_dir)
        cookie_file = xbmc.translatePath('%s/cookie.txt' % cookie_dir)
        self.Quiz = whatthemovie.WhatTheMovie(cookie_file)

    def onAction(self, action):
        # onAction will be called on keyboard or mouse action
        # action is the action which was triggered
        if action in self.AID_EXIT_BACK:
            self.closeDialog()
        #else:
        #    print action.getId()

    def onFocus(self, controlId):
        # onFocus will be called on any focus
        pass

    def onClick(self, controlId):
        # onClick will be called on any click
        # controlID is the ID of the item which is clicked
        if controlId == self.CID_BUTTON_GUESS:
            self.guessTitle()
        if controlId == self.CID_BUTTON_RANDOM:
            self.getRandomShot()
        elif controlId == self.CID_BUTTON_EXIT:
            self.closeDialog()

    def closeDialog(self):
        self.close()

    def getRandomShot(self):
        self.image_gif.setVisible(True)
        shot = self.Quiz.getRandomShot()
        shot = self.Quiz.shot  # fixme, strange error without?!
        local_image_path = self.downloadPic(shot['image_url'],
                                            shot['shot_id'])
        self.image_main.setImage(local_image_path)
        self.label_posted_by.setLabel(getString(self.SID_POSTED_BY)
                                      % self.Quiz.shot['posted_by'])
        if self.Quiz.shot['solved']['status']:
            self.label_solved.setLabel(getString(self.SID_SOLVED)
                                       % (self.Quiz.shot['solved']['status'],
                                          self.Quiz.shot['solved']['first_by']))
        else:
            self.label_solved.setLabel(getString(self.SID_UNSOLVED))
        self.image_gif.setVisible(False)

    def guessTitle(self):
        heading = getString(self.SID_KEYBOARD_HEADING)
        keyboard = xbmc.Keyboard(default='', heading=heading)
        keyboard.doModal()
        if keyboard.isConfirmed():
            guess = keyboard.getText()
        else:
            return
        answer = self.Quiz.guessShot(guess)
        if answer['is_right'] == True:
            self.answerRight(answer['title_year'])
        else:
            self.answerWrong()

    def answerRight(self, title_year):
        message = getString(self.SID_ANSWER_RIGHT)
        self.getRandomShot()
        self.score += 1
        self.updateScore()
        print title_year  # fixme: plz put me in any label
        dialog = xbmcgui.Dialog()
        dialog.ok('right', message)  # fixme

    def answerWrong(self):
        message = getString(self.SID_ANSWER_WRONG)
        dialog = xbmcgui.Dialog()
        dialog.ok('wrong', message)  # fixme

    def login(self):
        self.score = 0
        if getSetting('login') == 'false':
            self.label_state.setLabel(getString(self.SID_NOT_LOGGED_IN))
        else:
            user = getSetting('username')
            password = getSetting('password')
            success = self.Quiz.login(user, password)
            if success == False:
                dialog = xbmcgui.Dialog()
                dialog.ok(getString(self.SID_LOGIN_FAILED_HEADING),
                          getString(self.SID_LOGIN_FAILED) % user)  # fixme
                label = getString(self.SID_NOT_LOGGED_IN)
            else:
                label = getString(self.SID_LOGGED_IN_AS) % user
                self.score = int(self.Quiz.getScore())
            self.label_state.setLabel(label)
        self.updateScore()

    def downloadPic(self, image_url, shot_id):
        script_id = sys.modules['__main__'].__id__
        cache_dir = 'special://profile/addon_data/%s/cache' % script_id
        self.createCheckPath(cache_dir)
        image_path = xbmc.translatePath('%s/%s.jpg' % (cache_dir, shot_id))
        dl = urllib.urlretrieve(image_url, image_path, )
        return image_path

    def updateScore(self):
        score_string = getString(self.SID_YOUR_SCORE) % str(self.score)
        self.label_score.setLabel(score_string)

    def createCheckPath(self, path):
        if not os.path.isdir(xbmc.translatePath(path)):
            os.makedirs(xbmc.translatePath(path))
