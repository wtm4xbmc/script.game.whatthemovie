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
    CID_IMAGE_SOLUTION = 1006
    CID_LABEL_LOGINSTATE = 1001
    CID_LABEL_SCORE = 1003
    CID_LABEL_POSTED_BY = 1004
    CID_LABEL_SOLVED = 1005
    CID_LABEL_SOLUTION = 1007
    CID_LABEL_SHOT_ID = 1008
    CID_LABEL_SHOT_DATE = 1011
    CID_IMAGE_CORRECT = 1009
    CID_IMAGE_WRONG = 1010

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
    SID_CHECKING = 3111
    SID_POSTED_BY = 3203
    SID_SOLVED = 3204
    SID_UNSOLVED = 3205
    SID_SHOT_ID = 3207
    SID_SHOT_DATE = 3213

    # ACTION_IDs
    AID_EXIT_BACK = [10, 13]

    def __init__(self, *args, **kwargs):
        # __init__ will be called when python creates object from this class
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)

    def onInit(self):
        # onInit will be called from xbmc (after __init__)
        # store xbmc keycodes for exit and backspace

        # get controls
        self.button_guess = self.getControl(self.CID_BUTTON_GUESS)
        self.button_random = self.getControl(self.CID_BUTTON_RANDOM)
        self.button_exit = self.getControl(self.CID_BUTTON_EXIT)
        self.label_loginstate = self.getControl(self.CID_LABEL_LOGINSTATE)
        self.label_score = self.getControl(self.CID_LABEL_SCORE)
        self.label_posted_by = self.getControl(self.CID_LABEL_POSTED_BY)
        self.label_solved = self.getControl(self.CID_LABEL_SOLVED)
        self.label_solution = self.getControl(self.CID_LABEL_SOLUTION)
        self.label_shot_id = self.getControl(self.CID_LABEL_SHOT_ID)
        self.label_shot_date = self.getControl(self.CID_LABEL_SHOT_DATE)
        self.image_main = self.getControl(self.CID_IMAGE_MAIN)
        self.image_gif = self.getControl(self.CID_IMAGE_GIF)
        self.image_solution = self.getControl(self.CID_IMAGE_SOLUTION)
        self.image_correct = self.getControl(self.CID_IMAGE_CORRECT)
        self.image_wrong = self.getControl(self.CID_IMAGE_WRONG)

        # translate buttons
        self.button_guess.setLabel(getString(self.SID_GUESS))
        self.button_random.setLabel(getString(self.SID_RANDOM))
        self.button_exit.setLabel(getString(self.SID_EXIT))

        # set control visibility
        self.setVisibleState((self.label_solution,
                              self.image_solution,
                              self.image_correct,
                              self.image_wrong), False)
        self.hideLabels()

        # start the api
        self.Quiz = whatthemovie.WhatTheMovie()
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
        self.setVisibleState((self.image_gif, ), True)
        shot = self.Quiz.getRandomShot()
        local_image_path = self.downloadPic(shot['image_url'],
                                            shot['shot_id'])
        self.setVisibleState((self.label_solution,
                              self.image_solution,
                              self.image_correct,
                              self.image_wrong), False)
        self.image_main.setImage(local_image_path)
        self.label_posted_by.setLabel(getString(self.SID_POSTED_BY)
                                      % shot['posted_by'])
        if shot['solved']['status']:
            self.label_solved.setLabel(getString(self.SID_SOLVED)
                                       % (shot['solved']['count'],
                                          shot['solved']['first_by']))
        else:
            self.label_solved.setLabel(getString(self.SID_UNSOLVED))
        self.label_shot_id.setLabel(getString(self.SID_SHOT_ID)
                                    % shot['shot_id'])
        self.label_shot_date.setLabel(getString(self.SID_SHOT_DATE)
                                      % (shot['date']['year'] + ' ' +
                                         shot['date']['month'] + ' ' +
                                         shot['date']['day']))
        self.setVisibleState((self.image_gif, ), False)

    def guessTitle(self):
        self.setVisibleState((self.label_solution,
                              self.image_solution,
                              self.image_wrong,
                              self.image_correct), False)
        heading = getString(self.SID_KEYBOARD_HEADING)
        keyboard = xbmc.Keyboard(default='', heading=heading)
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText() is not '':
            guess = keyboard.getText()
            self.image_solution.setColorDiffuse('FFFFFF00')
            self.setVisibleState((self.label_solution,
                                  self.image_solution), True)
            message = getString(self.SID_CHECKING)
            self.label_solution.setLabel(message)
            answer = self.Quiz.guessShot(guess)
            self.setVisibleState((self.label_solution,
                                  self.image_solution), False)
            if answer['is_right'] == True:
                self.answerRight(answer['title_year'])
            else:
                self.answerWrong()

    def answerRight(self, title_year):
        message = getString(self.SID_ANSWER_RIGHT)
        self.image_solution.setColorDiffuse('FF00FF00')
        self.setVisibleState((self.label_solution,
                              self.image_solution,
                              self.image_correct), True)
        self.label_solution.setLabel(message % title_year)
        self.getRandomShot()
        self.score += 1
        self.updateScore()
        self.setVisibleState((self.label_solution,
                              self.image_solution,
                              self.image_correct), False)

    def answerWrong(self):
        self.image_solution.setColorDiffuse('FFFF0000')
        self.setVisibleState((self.label_solution,
                              self.image_solution,
                              self.image_wrong), True)
        message = getString(self.SID_ANSWER_WRONG)
        self.label_solution.setLabel(message)

    def login(self):
        self.score = 0
        if getSetting('login') == 'false':
            self.label_loginstate.setLabel(getString(self.SID_NOT_LOGGED_IN))
        else:
            script_id = sys.modules['__main__'].__id__
            cookie_dir = 'special://profile/addon_data/%s' % script_id
            self.checkCreatePath(cookie_dir)
            cookie_file = xbmc.translatePath('%s/cookie.txt' % cookie_dir)
            user = getSetting('username')
            password = getSetting('password')
            success = self.Quiz.login(user, password, cookie_file)
            if success == False:
                dialog = xbmcgui.Dialog()
                dialog.ok(getString(self.SID_LOGIN_FAILED_HEADING),
                          getString(self.SID_LOGIN_FAILED) % user)
                label = getString(self.SID_NOT_LOGGED_IN)
            else:
                label = getString(self.SID_LOGGED_IN_AS) % user
                self.score = int(self.Quiz.getScore(user))
            self.label_loginstate.setLabel(label)
        self.updateScore()

    def downloadPic(self, image_url, shot_id):
        script_id = sys.modules['__main__'].__id__
        cache_dir = 'special://profile/addon_data/%s/cache' % script_id
        self.checkCreatePath(cache_dir)
        image_path = xbmc.translatePath('%s/%s.jpg' % (cache_dir, shot_id))
        dl = urllib.urlretrieve(image_url, image_path, )
        return image_path

    def updateScore(self):
        score_string = getString(self.SID_YOUR_SCORE) % str(self.score)
        self.label_score.setLabel(score_string)

    def checkCreatePath(self, path):
        result = False
        if os.path.isdir(xbmc.translatePath(path)):
            result = True
        else:
            result = os.makedirs(xbmc.translatePath(path))
        return result

    def setVisibleState(self, control_list, visible):
        for control in control_list:
            control.setVisible(visible)

    def hideLabels(self):
        if getSetting('visible_posted_by') == 'false':
            self.setVisibleState((self.label_posted_by, ), False)
        if getSetting('visible_solved') == 'false':
            self.setVisibleState((self.label_solved, ), False)
        if getSetting('visible_shot_id') == 'false':
            self.setVisibleState((self.label_shot_id, ), False)
