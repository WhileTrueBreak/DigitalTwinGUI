from ui.uiHelper import *
from ui.elements.uiWrapper import UiWrapper
from ui.elements.uiBlock import UiBlock
from ui.constraintManager import *

class Pages:

    def __init__(self, window, constraints):
        self.window = window
        self.pageWrapper = UiBlock(window, constraints)
        self.pageWrapper.setColor((0,0,0,0.7))
        self.pages = []
        self.currentPage = None
        self.buttonMap = {}
        self.pageButtons = {}
        self.pageContentWrapper = {}
    
    def handleEvents(self, event):
        if event['action'] != 'release': return
        if event['obj'] in self.buttonMap:
            self.switchPage(self.buttonMap[event['obj']])
    
    def refreshPage(self):
        if self.currentPage == None: return
        self.pageWrapper.removeAllChildren()
        self.pageWrapper.addChild(self.currentPage)

    def switchPage(self, page):
        self.currentPage = page
        self.pageWrapper.removeAllChildren()
        self.pageWrapper.addChild(page)
    
    def addPage(self):
        page = UiWrapper(self.window, Constraints.ALIGN_PERCENTAGE(0,0,1,1))
        wrapper = UiWrapper(self.window, Constraints.ALIGN_PERCENTAGE(0, 0, 1, 0.9))
        page.addChild(wrapper)
        self.pages.append(page)
        self.pageButtons[page] = {'prev':None, 'next':None}
        self.pageContentWrapper[page] = wrapper
        self.addNext(page)
        self.addPrev(page)
        if (prevbutton:=self.pageButtons[page]['prev']) != None:
            self.addNext(self.buttonMap[prevbutton])
        if len(self.pages) == 1:
            self.switchPage(page)
    
    def removePage(self, pageNum):
        if pageNum < 0 or pageNum >= len(self.pages): return
        self.pageContentWrapper.pop(self.pages[pageNum])
        prevButton = self.pageButtons[self.pages[pageNum]]['prev']
        prevPage = None
        if prevButton != None:
            prevPage = self.buttonMap[prevButton]
            self.buttonMap[prevPage]['next'] = None
            prevPage.removeChild(self.pageButtons[prevPage]['next'])
        nextButton = self.pageButtons[self.pages[pageNum]]['next']
        nextPage = None
        if nextButton != None:
            nextPage = self.buttonMap[nextButton]
            self.buttonMap[nextPage]['prev'] = None
            nextPage.removeChild(self.pageButtons[nextPage]['prev'])
        self.buttonMap.pop(self.pages[pageNum])
        if currentPage == self.pages[pageNum]:
            self.pageWrapper.removeChild(currentPage)
            if len(self.pages) == 1:
                self.switchPage(self.pages[0])
        del self.pages[pageNum]
        if prevPage != None: self.addNext(prevPage)
        if nextPage != None: self.addPrev(nextPage)
    
    def getPage(self, pageNum):
        if pageNum < 0 or pageNum >= len(self.pages): return None
        return self.pageContentWrapper[self.pages[pageNum]]
    
    def addNext(self, page):
        if self.pages.index(page) >= len(self.pages)-1: return
        padding = 5
        constraints = [
            COMPOUND(RELATIVE(T_X, 0.5, P_W), ABSOLUTE(T_X, padding)),
            COMPOUND(RELATIVE(T_Y, 0.9, P_H), ABSOLUTE(T_Y, padding)),
            COMPOUND(RELATIVE(T_W, 0.5, P_W), ABSOLUTE(T_W, -2*padding)),
            COMPOUND(RELATIVE(T_H, 0.1, P_H), ABSOLUTE(T_H, -2*padding)),
        ]
        button,text = centeredTextButton(self.window, constraints)
        text.setText('Next Page')
        text.setFontSize(20)
        text.setTextSpacing(7)
        button.setDefaultColor((0,109/255,174/255))
        button.setHoverColor((0,159/255,218/255))
        button.setPressColor((0,172/255,62/255))
        button.setLockColor((0.6, 0.6, 0.6))
        page.addChild(button)
        self.pageButtons[page]['next'] = button
        self.buttonMap[button] = self.pages[self.pages.index(page)+1]
    
    def addPrev(self, page):
        if self.pages.index(page) <= 0: return
        padding = 5
        constraints = [
            COMPOUND(RELATIVE(T_X, 0, P_W), ABSOLUTE(T_X, padding)),
            COMPOUND(RELATIVE(T_Y, 0.9, P_H), ABSOLUTE(T_Y, padding)),
            COMPOUND(RELATIVE(T_W, 0.5, P_W), ABSOLUTE(T_W, -2*padding)),
            COMPOUND(RELATIVE(T_H, 0.1, P_H), ABSOLUTE(T_H, -2*padding)),
        ]
        button,text = centeredTextButton(self.window, constraints)
        text.setText('Prev Page')
        text.setFontSize(20)
        text.setTextSpacing(7)
        button.setDefaultColor((0,109/255,174/255))
        button.setHoverColor((0,159/255,218/255))
        button.setPressColor((0,172/255,62/255))
        button.setLockColor((0.6, 0.6, 0.6))
        page.addChild(button)
        self.pageButtons[page]['prev'] = button
        self.buttonMap[button] = self.pages[self.pages.index(page)-1]

    def getPageWrapper(self):
        return self.pageWrapper
