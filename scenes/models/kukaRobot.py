class KukaRobot:

    def __init__(self, pos, nid, rid, modelRenderer, hasGripper=True, hasForceVector=False):
        self.joints = [0,0,0,pi/2,0,0,0]
        self.forceVector = np.array([0,0,0], dtype='float32')
        self.pos = pos
        self.nodeId = nid
        self.robotId = rid
        self.modelRenderer = modelRenderer
        self.hasGripper = hasGripper
        self.hasForceVector = hasForceVector
        self.colors = np.zero((8,4), dtype='float32')
        self.isLinkedOpcua = True
        self.__loadModel()
        self.__setupConnections()
    
    def __loadModel(self):
        self.modelKukaIds = []
        x, y, z = self.pos
        for i in range(0,8):
            mat = Robot1_T_0_[i].copy()
            self.modelKukaIds.append(self.modelRenderer.addModel(Assets.KUKA_IIWA14_MODEL[i], mat))
            self.modelRenderer.setColor(self.modelKukaIds[-1], self.colors[i])
        if self.hasGripper:
            self.modelKukaIds.append(self.modelRenderer.addModel(Assets.GRIPPER, Robot1_T_0_[7].copy()))
            self.modelRenderer.setColor(self.modelKukaIds[-1], self.colors[-1])
        self.forceVectorId = None
        if self.hasForceVector:
            self.forceVectorId = self.modelRenderer.addModel(Assets.POLE, np.identity(4))
            self.modelRenderer.setColor(self.forceVectorId, (0,0,0,0.7))
    
    def __getNodeName(self, name):
        return f'ns={self.nodeId};s={self.robotId}{name}'

    def __setupConnections(self):
        self.opcuaReceiverContainer = OpcuaContainer()
        self.jointReceiver = OpcuaReceiver([
                    self.__getNodeName('d_Joi1'),
                    self.__getNodeName('d_Joi2'),
                    self.__getNodeName('d_Joi3'),
                    self.__getNodeName('d_Joi4'),
                    self.__getNodeName('d_Joi5'),
                    self.__getNodeName('d_Joi6'),
                    self.__getNodeName('d_Joi7'),
                ], self.opcuaReceiverContainer, 'oct.tpc://172.31.1.236:4840/server/')
        self.forceReceiver = OpcuaReceiver([
                    self.__getNodeName('d_ForX'),
                    self.__getNodeName('d_ForY'),
                    self.__getNodeName('d_ForZ'),
                ], self.opcuaReceiverContainer, 'oct.tpc://172.31.1.236:4840/server/')

    def update(self):
        self.__updateFromOpcua()
        self.__updateJoints()
    
    def __updateFromOpcua(self):
        if not self.isLinkedOpcua: return
        for i in range(7):
            if not self.opcuaReceiverContainer.hasUpdated(self.__getNodeName(f'd_Joi{i+1}')): continue
            self.jointsRad[i] = radians(self.opcuaReceiverContainer.getValue(self.__getNodeName(f'd_Joi{i+1}'), default=0)[0])
        if self.opcuaReceiverContainer.hasUpdated(self.__getNodeName(f'd_ForX')):
            self.forceVector[0] = self.opcuaReceiverContainer.getValue(self.__getNodeName(f'd_ForX'), default=0)[0]
        if self.opcuaReceiverContainer.hasUpdated(self.__getNodeName(f'd_ForY')):
            self.forceVector[1] = self.opcuaReceiverContainer.getValue(self.__getNodeName(f'd_ForY'), default=0)[0]
        if self.opcuaReceiverContainer.hasUpdated(self.__getNodeName(f'd_ForZ')):
            self.forceVector[2] = self.opcuaReceiverContainer.getValue(self.__getNodeName(f'd_ForZ'), default=0)[0]

    def __updateJoints(self):
        Robot1_T_0_ , Robot1_T_i_ = self.__T_KUKAiiwa14(self.jointsRad)
        for i,id in enumerate(self.modelKukaIds):
            mat = Robot1_T_0_[max(i, len(Robot1_T_0_)-1)].copy()
            mat[0][3] += self.pos[0]*2/2
            mat[1][3] += self.pos[1]*2/2
            mat[2][3] += self.pos[2]*2/2
            self.modelRenderer.setTransformMatrix(id, mat)
        self.__updateForceVector(Robot1_T_0_[-1])
    
    def __updateForceVector(self, mat):
        if not self.hasForceVector or self.forceVectorId == None: return
        if not self.isLinkedOpcua:
            self.modelRenderer.setColor(self.forceVectorId, (0,0,0,0))
            return
        forceMag = np.linalg.norm(self.forceVector)
        if forceMag < 3.5:
            self.modelRenderer.setColor(self.forceVectorId, (0,0,0,0))
            return
        forceTransform = vectorTransform(transform[:3,3], transform[:3,3]+2*self.forceVector, 1, upperLimit=100)
        self.modelRenderer.setColor(self.forceVectorId, (0,0,0,0.7))
        self.modelRenderer.setTransformMatrix(self.forceVectorId, forceTransform)

    def start(self):
        if not self.isLinkedOpcua:return
        self.jointReceiver.start()
        self.forceReceiver.start()
        self.progControlReceiver.start()
        self.transmitter.start()

    def stop(self):
        self.jointReceiver.stop()
        self.forceReceiver.stop()
        self.progControlReceiver.stop()
        self.transmitter.stop()

    def __DH(self, DH_table):
        T_0_ = np.ndarray(shape=(len(DH_table)+1,4,4))
        T_0_[:][:][0] = np.eye(4)
        T_i_ = np.ndarray(shape=(len(DH_table),4,4))
        for i in range(len(DH_table)):
            alp = DH_table[i][0]
            a = DH_table[i][1]
            d = DH_table[i][2]
            the = DH_table[i][3]

            T = np.array([[np.cos(the),-np.sin(the),0,a],
                [np.sin(the)*np.cos(alp),np.cos(the)*np.cos(alp),-np.sin(alp),-np.sin(alp)*d],
                [np.sin(the)*np.sin(alp),np.cos(the)*np.sin(alp),np.cos(alp),np.cos(alp)*d],
                [0,0,0,1]])

            T_0_[:][:][i+1] = np.matmul(T_0_[:][:][i],T)
            T_i_[:][:][i] = T
        return T_0_ ,T_i_

    def __T_KUKAiiwa14(self, q):
        DH_Robot1 = np.array([[0, 0, 0.36, q[0]], 
            [-np.pi/2, 0, 0 , q[1]],
            [np.pi/2, 0, 0.42 , q[2]],
            [np.pi/2, 0, 0, q[3]],
            [-np.pi/2, 0, 0.4, q[4]],
            [-np.pi/2, 0, 0, q[5]],
            [np.pi/2, 0, 0.15194, q[6]]])

        Robot1_T_0_ , Robot1_T_i_ = self.__DH(DH_Robot1)
        return Robot1_T_0_ , Robot1_T_i_

    def setColors(self, colors):
        self.colors = colors
        for i,id in enumerate(self.modelKukaIds):
            self.modelRenderer.setColor(id, self.colors[i])

    def disconnectOpcua(self):
        self.isLinkedOpcua = False
        self.stop()

    def connectOpcua(self):
        self.isLinkedOpcua = True
        self.start()

    def setJoints(self, angles):
        self.joints = angles

    def getJoints(self):
        return self.joints

class KukaRobotTwin:

    FREE_MOVE_PROG = 2

    def __init__(self, window, pos, nid, rid, modelRenderer, hasGripper=True, hasForceVector=False):
        self.liveRobot = KukaRobot(pos, nid, rid, modelRenderer, hasGripper, hasForceVector)
        self.twinRobot = KukaRobot(pos, nid, rid, modelRenderer, hasGripper, False)

        self.window = window

        self.twinJoints = self.twinRobot.getJoints().copy()

        self.twinRobot.disconnectOpcua()

        self.matchLive = True

        self.progStartFlag = False
        self.executingFlag = False
        self.doneFlag = False

        self.__createUi()
        self.__setupConnections()
    
    def __getNodeName(self, name):
        return f'ns={self.nodeId};s={self.robotId}{name}'

    def __setupConnections(self):
        self.opcuaReceiverContainer = OpcuaContainer()
        self.opcuaTransmitterContainer = OpcuaContainer()
        self.progControlReceiver = OpcuaReceiver([
                    self.__getNodeName('c_ProgID'),
                    self.__getNodeName('c_Start'),
                    self.__getNodeName('f_Ready'),
                    self.__getNodeName('f_End'),
                ], self.opcuaReceiverContainer, 'oct.tpc://172.31.1.236:4840/server/')
        self.transmitter = OpcuaTransmitter(self.opcuaTransmitterContainer, 'oct.tpc://172.31.1.236:4840/server/')

    def __createUi(self):
        self.pages = Pages(self.window, Constraints.ALIGN_PERCENTAGE(0, 0, 1, 1))
        self.pages.addPage()
        self.pages.addPage()
        self.pages.addPage()
        self.page0 = self.pages.getPage(0)

        self.selecterWrappers = [None]*7
        padding = 5
        for i in range(len(self.selecterWrappers)):
            constraints = [
                ABSOLUTE(T_X, padding),
                COMPOUND(RELATIVE(T_Y, 0.1*i, P_H), ABSOLUTE(T_Y, padding)),
                COMPOUND(RELATIVE(T_W, 1, P_W), ABSOLUTE(T_W, -2*padding)),
                COMPOUND(RELATIVE(T_H, 0.1, P_H), ABSOLUTE(T_H, -2*padding)),
            ]
            self.selecterWrappers[i] = UiWrapper(self.window, constraints)
        self.page0.addChildren(*self.selecterWrappers)

        self.liveTextWrapper = [None]*len(self.selecterWrappers)
        self.liveAngleText = [None]*len(self.selecterWrappers)
        self.twinTextWrapper = [None]*len(self.selecterWrappers)
        self.twinAngleText = [None]*len(self.selecterWrappers)

        self.angleSlider = [None]*len(self.selecterWrappers)
        for i in range(len(self.selecterWrappers)):
            self.liveTextWrapper[i] = UiWrapper(self.window, Constraints.ALIGN_PERCENTAGE(0, 0, 0.5, 0.5))
            self.twinTextWrapper[i] = UiWrapper(self.window, Constraints.ALIGN_PERCENTAGE(0.5, 0, 0.5, 0.5))
            self.selecterWrappers[i].addChild(self.liveTextWrapper[i])
            self.selecterWrappers[i].addChild(self.twinTextWrapper[i])
            self.liveAngleText[i] = UiText(self.window, Constraints.ALIGN_TEXT_PERCENTAGE(0, 0.5))
            self.liveAngleText[i].setFontSize(18)
            self.liveAngleText[i].setTextSpacing(7)
            self.twinAngleText[i] = UiText(self.window, Constraints.ALIGN_TEXT_PERCENTAGE(0, 0.5))
            self.twinAngleText[i].setFontSize(18)
            self.twinAngleText[i].setTextSpacing(7)
            self.liveTextWrapper[i].addChild(self.liveAngleText[i])
            self.twinTextWrapper[i].addChild(self.twinAngleText[i])
            self.angleSlider[i] = UiSlider(self.window, Constraints.ALIGN_PERCENTAGE(0, 0.5, 1, 0.5))
            self.angleSlider[i].setRange(-pi, pi)
            self.angleSlider[i].setBaseColor((0,0,0))
            self.angleSlider[i].setSliderColor((0.8,0.8,0.8))
            self.angleSlider[i].setSliderPercentage(0.05)
            self.selecterWrappers[i].addChild(self.angleSlider[i])
        
        constraints = [
            COMPOUND(RELATIVE(T_X, 0.5, P_W), ABSOLUTE(T_X, padding)),
            COMPOUND(RELATIVE(T_Y, 0.8, P_H), ABSOLUTE(T_Y, padding)),
            COMPOUND(RELATIVE(T_W, 0.5, P_W), ABSOLUTE(T_W, -2*padding)),
            COMPOUND(RELATIVE(T_H, 0.1, P_H), ABSOLUTE(T_H, -2*padding)),
        ]
        self.sendBtn, self.sendBtnText = centeredTextButton(self.window, constraints)
        self.sendBtnText.setText('Execute')
        self.sendBtnText.setFontSize(20)
        self.sendBtnText.setTextSpacing(8)
        self.sendBtn.setDefaultColor((0,109/255,174/255))
        self.sendBtn.setHoverColor((0,159/255,218/255))
        self.sendBtn.setPressColor((0,172/255,62/255))
        self.sendBtn.setLockColor((0.6, 0.6, 0.6))
        self.page0.addChild(self.sendBtn)
        
        constraints = [
            COMPOUND(RELATIVE(T_X, 0, P_W), ABSOLUTE(T_X, padding)),
            COMPOUND(RELATIVE(T_Y, 0.8, P_H), ABSOLUTE(T_Y, padding)),
            COMPOUND(RELATIVE(T_W, 0.5, P_W), ABSOLUTE(T_W, -2*padding)),
            COMPOUND(RELATIVE(T_H, 0.1, P_H), ABSOLUTE(T_H, -2*padding)),
        ]
        self.unlinkBtn, self.unlinkBtnText = centeredTextButton(self.window, constraints)
        self.unlinkBtnText.setText('Unlink')
        self.unlinkBtnText.setFontSize(20)
        self.unlinkBtnText.setTextSpacing(8)
        self.unlinkBtn.setDefaultColor((0,109/255,174/255))
        self.unlinkBtn.setHoverColor((0,159/255,218/255))
        self.unlinkBtn.setPressColor((0,172/255,62/255))
        self.unlinkBtn.setLockColor((0.6, 0.6, 0.6))
        self.page0.addChild(self.unlinkBtn)

    def update(self):
        self.liveRobot.update()
        self.twinRobot.update()
        self.__updateJoints()
        self.__updateProgram()
        self.__updateGui()

    def __updateJoints(self):
        if self.matchLive:
            self.twinJoints = self.liveRobot.getJoints().copy()

    def __updateProgram(self):
        if not self.opcuaReceiverContainer.getValue(self.__getNodeName('f_Ready'), default=False)[0]:
            self.sendBtn.lock()
        if self.progStartFlag:
            self.sendBtn.lock()
            self.unlinkBtn.lock()
            self.sendBtnText.setText('Waiting')
            if self.__isTransmitClear():
                self.executingFlag = True
                self.progStartFlag = False
                self.opcuaTransmitterContainer.setValue(self.__getNodeName('c_Start'), True, ua.VariantType.Boolean)
        elif self.executingFlag:
            self.sendBtn.lock()
            self.unlinkBtn.lock()
            self.sendBtnText.setText('Executing')
            if self.opcuaReceiverContainer.getValue(self.__getNodeName('c_ProgID'), default=self.progid)[0] == 0:
                self.doneFlag = True
                self.executingFlag = False
        elif self.doneFlag:
            self.doneFlag = False
            self.sendBtn.unlock()
            self.unlinkBtn.unlock()
            self.matchLive = True
            self.unlinkBtnText.setText('Unlink')
            self.sendBtnText.setText('Execute')
            self.__updateTwinColor()
        elif self.opcuaReceiverContainer.getValue(self.__getNodeName('f_Ready'), default=False)[0]:
            self.sendBtn.unlock()

    def __updateGui(self):
        for i in range(len(self.selecterWrappers)):
            self.liveAngleText[i].setText(f'Live: {int(self.jointsRad[i]*180/pi)}')
            if not self.matchLive:
                twinText = self.angleSlider[i].getValue()
                self.twinJoints[i] = float(twinText)
            else:
                self.angleSlider[i].setValue(self.twinJoints[i])
            self.twinAngleText[i].setText(f'Twin: {int(self.twinJoints[i]*180/pi)}')

    def handleEvents(self, event):
        self.pages.handleEvents(event)
        if event['action'] == 'release':
            if event['obj'] == self.sendBtn:
                self.sendBtn.lock()
                for i in range(len(self.twinJoints)):
                    self.opcuaTransmitterContainer.setValue(self.__getNodeName(f'c_Joi{i+1}'), self.twinJoints[i]*180/pi, ua.VariantType.Double)
                self.opcuaTransmitterContainer.setValue(self.__getNodeName(f'c_ProgID'), KukaRobotTwin.FREE_MOVE_PROG, ua.VariantType.Int32)
                self.progStartFlag = True
            if event['obj'] == self.unlinkBtn:
                self.matchLive = not self.matchLive
                self.unlinkBtnText.setText('Unlink' if self.matchLive else 'Link')
                self.__updateTwinColor()

    def setLiveColors(self, colors):
        self.liveRobot.setColors(colors)

    def setTwinColors(self, colors):
        self.twinRobot.setColors(colors)

    def start(self):
        self.liveRobot.start()
        self.twinRobot.start()

    def stop(self):
        self.liveRobot.stop()
        self.twinRobot.stop()

    def getControlPanel(self):
        return self.pages.getPageWrapper()

    def __isTransmitClear(self):
        for i in range(len(self.twinJoints)):
            if self.opcuaTransmitterContainer.hasUpdated(self.__getNodeName(f'c_Joi{i+1}')):
                return False
        if self.opcuaTransmitterContainer.hasUpdated(self.__getNodeName('c_ProgID')):
            return False
        if self.opcuaReceiverContainer.getValue(self.__getNodeName('c_ProgID'), default=0)[0] != KukaRobotTwin.FREE_MOVE_PROG:
            return False
        if not self.opcuaReceiverContainer.getValue(self.__getNodeName('f_Ready'), default=False)[0]:
            return False
        return True

    def __updateTwinColor(self):
        for id in self.twinKukaIds:
            color = self.modelRenderer.getData(id)['color']
            self.modelRenderer.setColor(id, (*color[0:3], 0 if self.matchLive else 0.7))
        color = self.modelRenderer.getData(self.TgripperId)['color']
        self.modelRenderer.setColor(self.TgripperId, (*color[0:3], 0 if self.matchLive else 0.7))


