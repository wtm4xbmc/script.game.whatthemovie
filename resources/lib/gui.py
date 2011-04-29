import sys
import os
import urllib
import xbmcgui
import xbmc
import whatthemovie

getLocalizedString = sys.modules['__main__'].getLocalizedString
getSetting = sys.modules['__main__'].getSetting

# Buttons               3000-3009
# Textboxes             3010-3019
# Transl. for Controls  3100-3119
# Transl. for Usage     3200-3219


class GUI(xbmcgui.WindowXMLDialog):
    # get control ids
    CONTROL_ID_BUTTON_GUESS = 3000
    CONTROL_ID_BUTTON_NEXT = 3001
    CONTROL_ID_BUTTON_EXIT = 3002
    CONTROL_ID_IMAGE_MAIN = 1000
    CONTROL_ID_IMAGE_GIF = 1002
    CONTROL_ID_LABEL_STATE = 1001
    CONTROL_ID_LABEL_SCORE = 1003

    def __init__(self, *args, **kwargs):
        # __init__ will be called when python creates object from this class
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)

    def onInit(self):
        # onInit will be called from xbmc (after __init__)
        # store xbmc keycodes for exit and backspace
        self.Quiz = whatthemovie.WhatTheMovie()

        self.action_exitkeys_id = [10, 13]

        # get controls
        self.button_guess = self.getControl(self.CONTROL_ID_BUTTON_GUESS)
        self.button_next = self.getControl(self.CONTROL_ID_BUTTON_NEXT)
        self.button_exit = self.getControl(self.CONTROL_ID_BUTTON_EXIT)
        self.label_state = self.getControl(self.CONTROL_ID_LABEL_STATE)
        self.label_score = self.getControl(self.CONTROL_ID_LABEL_SCORE)
        self.image_main = self.getControl(self.CONTROL_ID_IMAGE_MAIN)
        self.image_gif = self.getControl(self.CONTROL_ID_IMAGE_GIF)
        
        # translate buttons
        self.button_guess.setLabel(getLocalizedString(3100))
        self.button_next.setLabel(getLocalizedString(3101))
        self.button_exit.setLabel(getLocalizedString(3102))

        self.login()
        self.getRandomShot()
        self.downloadPic()

    def onAction(self, action):
        # onAction will be called on keyboard or mouse action
        # action is the action which was triggered
        if action in self.action_exitkeys_id:
            self.closeDialog()
        #else:
        #    print action.getId()

    def onFocus(self, controlId):
        # onFocus will be called on any focus
        pass

    def onClick(self, controlId):
        # onClick will be called on any click
        # controlID is the ID of the item which is clicked
        if controlId == self.CONTROL_ID_BUTTON_GUESS:
            print 'guess'
            self.guessTitle()
        if controlId == self.CONTROL_ID_BUTTON_NEXT:
            print 'next'
            self.getRandomShot()
        elif controlId == self.CONTROL_ID_BUTTON_EXIT:
            print 'exit'
            self.closeDialog()

    def closeDialog(self):
        self.close()

    def getRandomShot(self):
        self.image_gif.setVisible(True)
        self.Quiz.getRandomShot()
        local_image_path = self.downloadPic(self.Quiz.shot['image_url'], self.Quiz.shot['shot_id'])
        self.image_main.setImage(local_image_path)
        self.image_gif.setVisible(False)

    def guessTitle(self):
        keyboard = xbmc.Keyboard(default='', title=getLocalizedString(3105))
        keyboard.doModal()
        if keyboard.isConfirmed():
            guess = keyboard.getText()
        answer = self.Quiz.guessShot(guess)
        if answer == 'right':
            message = getLocalizedString(3103)
            self.getRandomShot()
            self.score += 1
        else:
            message = getLocalizedString(3104)
        dialog = xbmcgui.Dialog()
        dialog.ok(answer, message)  # fixme

    def login(self):
        self.score = 0
        if getSetting('login') == 'false':
            self.label_state.setLabel(getLocalizedString(3106))
        else:
            user = getSetting('username')
            password = getSetting('password')
            success = self.Quiz.login(user, password)
            if success == False:
                dialog = xbmcgui.Dialog()
                dialog.ok(getLocalizedString(3108), getLocalizedString(3109) % user)  # fixme
                self.label_state.setLabel(getLocalizedString(3106))
            else:
                self.label_state.setLabel(getLocalizedString(3107) % user)
                self.score = int(self.Quiz.getScore())
        self.updateScore()

    def downloadPic(self, image_url, shot_id):
        cache_dir = 'special://profile/addon_data/%s/cache' % sys.modules['__main__'].__id__
        if not os.path.isdir(xbmc.translatePath(cache_dir)):
            os.makedirs(xbmc.translatePath(cache_dir))
        image_path = xbmc.translatePath('%s/%s.jpg' % (cache_dir, shot_id))
        dl = urllib.urlretrieve(image_url, image_path, )
        return image_path

    def updateScore(self):
        score_string = getLocalizedString(3110) % str(self.score)
        self.label_score.setLabel(score_string)
