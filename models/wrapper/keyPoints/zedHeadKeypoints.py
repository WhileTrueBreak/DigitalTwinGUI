from asset import *

from connections.opcua import *
from connections.opcuaReceiver import OpcuaReceiver
from connections.opcuaTransmitter import OpcuaTransmitter
from constants import Constants

from models.interfaces.model import Updatable, Serializable

from utils.interfaces.pollController import PollController
from utils.debug import *

class ZedHeadKeypoints(Updatable, PollController, Serializable):
    def __init__(self, modelRenderer):
        self.modelRenderer = modelRenderer

        self.attach = None

        self.headPoseChanged = True
        self.headPoses = []
        self.headModelIds = []

        self.headPoses = []
        self.__setupConnections()

    def __setupConnections(self):
        self.opcuaReceiverContainer = OpcuaContainer()
        self.headlistReceiver = OpcuaReceiver(['ns=54;s=ZED_Headlist'], self.opcuaReceiverContainer, Constants.OPCUA_LOCATION)
        
    @funcProfiler(ftype='zedupdate')
    def update(self, delta):
        self.__updateHeadPose()
        self.__updateHeadModels()

    def __updateHeadPose(self):
        if not self.opcuaReceiverContainer.hasUpdated('ns=54;s=ZED_Headlist'): return
        headlist = self.opcuaReceiverContainer.getValue('ns=54;s=ZED_Headlist', default=[])[0]
        ZEDHeadPoses = [headlist[i:i+3] for i in range(0, len(headlist), 3)]

        self.headPoses = []
        for pose in ZEDHeadPoses:
            self.headPoses.append([-pose[0], pose[2], pose[1]])
        self.headPoseChanged = True
    
    def __updateHeadModels(self, force_update=False):
        if not self.headPoseChanged and not force_update: return
        attachFrame = self.attach.getFrame() if self.attach else np.identity(4)
        currentHeadNum = len(self.headModelIds)
        if currentHeadNum > len(self.headPoses):
            for id in self.headModelIds[len(self.headPoses):]:
                self.modelRenderer.setViewFlag(id, False)
                self.modelRenderer.setColor(id, (1,1,1,0))
        for i,e in enumerate(self.headPoses):
            headTransform = np.matmul(createTransformationMatrix(e[0], e[1], e[2], 0, 0, 0), createScaleMatrix(3, 3, 3))
            headTransform = np.matmul(attachFrame, headTransform)
            if i < currentHeadNum:
                self.modelRenderer.setViewFlag(self.headModelIds[i], True)
                self.modelRenderer.setColor(self.headModelIds[i], (0,1,0,0.8))
                self.modelRenderer.setTransformMatrix(self.headModelIds[i], headTransform)
            else:
                self.headModelIds.append(self.modelRenderer.addModel(Assets.SPHERE, headTransform))
                self.modelRenderer.setColor(self.headModelIds[-1], (0,1,0,0.8))
        self.headPoseChanged = False

    def setAttach(self, iModel):
        self.attach = iModel
        self.__updateHeadModels(force_update=True)
        return
    
    def isModel(self, modelId):
        return modelId in self.headModelIds

    @timing
    def start(self):
        self.headlistReceiver.start()

    @timing
    def stop(self):
        self.headlistReceiver.stop()

    @timing
    def serialize(self, loc):
        pass

    @timing
    @classmethod
    def deserialize(cls, path, file, renderer):
        pass