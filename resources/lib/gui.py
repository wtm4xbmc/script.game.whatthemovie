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
    # CONTOL_IDs
    CID_BUTTON_GUESS = 3000
    CID_BUTTON_RANDOM = 3001
    CID_BUTTON_EXIT = 3002
    CID_IMAGE_MAIN = 1000
    CID_IMAGE_GIF = 1002
    CID_LABEL_STATE = 1001
    CID_LABEL_SCORE = 1003

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

    # ACTION_IDs
    AID_EXIT_BACK = [10, 13]

    def __init__(self, *args, **kwargs):
        # __init__ will be called when python creates object from this class
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)

    def onInit(self):
        # onInit will be called from xbmc (after __init__)
        # store xbmc keycodes for exit and backspace
        self.Quiz = whatthemovie.WhatTheMovie()

        # get controls
        self.button_guess = self.getControl(self.CID_BUTTON_GUESS)
        self.button_random = self.getControl(self.CID_BUTTON_RANDOM)
        self.button_exit = self.getControl(self.CID_BUTTON_EXIT)
        self.label_state = self.getControl(self.CID_LABEL_STATE)
        self.label_score = self.getControl(self.CID_LABEL_SCORE)
        self.image_main = self.getControl(self.CID_IMAGE_MAIN)
        self.image_gif = self.getControl(self.CID_IMAGE_GIF)

        # translate buttons
        self.button_guess.setLabel(getString(self.SID_GUESS))
        self.button_random.setLabel(getString(self.SID_RANDOM))
        self.button_exit.setLabel(getString(self.SID_EXIT))

        # start the api
        self.login()
        self.getRandomShot()

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
        self.Quiz.getRandomShot()
        local_image_path = self.downloadPic(self.Quiz.shot['image_url'],
                                            self.Quiz.shot['shot_id'])
        self.image_main.setImage(local_image_path)
        self.image_gif.setVisible(False)

    def guessTitle(self):
        heading = getString(self.SID_KEYBOARD_HEADING)
        keyboard = xbmc.Keyboard(default='', heading=heading)
        keyboard.doModal()
        if keyboard.isConfirmed():
            guess = keyboard.getText()
        else:
            return
        answer_is_right = self.Quiz.guessShot(guess)
        if answer_is_right == True:
            self.answerRight()
        else:
            self.answerWrong()

    def answerRight(self):
        message = getString(self.SID_ANSWER_RIGHT)
        self.getRandomShot()
        self.score += 1
        self.updateScore()
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
        if not os.path.isdir(xbmc.translatePath(cache_dir)):
            os.makedirs(xbmc.translatePath(cache_dir))
        image_path = xbmc.translatePath('%s/%s.jpg' % (cache_dir, shot_id))
        dl = urllib.urlretrieve(image_url, image_path, )
        return image_path

    def updateScore(self):
        score_string = getString(self.SID_YOUR_SCORE) % str(self.score)
        self.label_score.setLabel(score_string)
