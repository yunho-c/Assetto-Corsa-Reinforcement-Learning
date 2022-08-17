##############################################################
# In-game 3D Map Apps
# ver. 1.1.2 / 21.Nov.2020
# Innovare Studio Inc. / D.Tsukamoto
#############################################################

import struct
import threading
import time
from operator import itemgetter

import ac

import acsys
from isUtils import *

rootPath = "apps/python/IS_3DMap"
configFile = rootPath + "/config.ini"
CONFIG = None

UI_FONT = "Segoe UI"
UI_COLOR_PICK = [1, 0, 0]
UI_COLOR_PICK_SELF = [0, 0, 0]
UI_COLOR_TEXT = [1, 1, 1]
UI_COLOR_BGR = [0.2, 0.2, 0.2]

CARS = []
CAR_FOCUSED = 0

TRACK_NAME = ""
TRACK_CONFIG = ""
TRACK_LENGTH = 0
TRACK_DIRECTORY = ""

TRACK_DETAILS = None

THREAD_WORKER = None
RENDERER = None
INITIALIZED = False


def acMain(version):
	global CONFIG
	CONFIG = Config(configFile)
	
	global CARS
	CARS = [carState(i) for i in range(ac.getCarsCount())]
	
	global TRACK_NAME, TRACK_CONFIG, TRACK_LENGTH, TRACK_DIRECTORY
	TRACK_NAME = ac.getTrackName(0)
	TRACK_CONFIG = ac.getTrackConfiguration(0)
	TRACK_LENGTH = ac.getTrackLength(0)
	TRACK_DIRECTORY = "content/tracks/%s" % (TRACK_NAME)
	if not TRACK_CONFIG == "" and os.path.isdir("content/tracks/%s/%s" % (TRACK_NAME, TRACK_CONFIG)):
		TRACK_DIRECTORY = "content/tracks/%s/%s" % (TRACK_NAME, TRACK_CONFIG)
	
	global TRACK_DETAILS
	TRACK_DETAILS = trackDetails()
	
	global THREAD_WORKER
	THREAD_WORKER = backgroundWorker()
	
	global RENDERER
	RENDERER = renderer()
	
	global INITIALIZED
	INITIALIZED = True


def acUpdate(delta):
	if not INITIALIZED and len(CARS) == 0: return
	global CAR_FOCUSED
	CAR_FOCUSED = ac.getFocusedCar()
	for index, CAR in enumerate(CARS):
		CAR.alive = ac.isConnected(index) == 1
		CAR.position = vec2(*itemgetter(0, 2)(ac.getCarState(index, acsys.CS.WorldPosition)))
		v1 = ac.getCarState(index, acsys.CS.TyreContactPoint, acsys.WHEELS.FR)
		v2 = ac.getCarState(index, acsys.CS.TyreContactPoint, acsys.WHEELS.RR)
		CAR.heading = math.degrees(math.atan2(v2[2] - v1[2], v2[0] - v1[0])) * -1
		CAR.name = str(ac.getDriverName(index))
		CAR.rank = ac.getCarRealTimeLeaderboardPosition(index) + 1
		CAR.speed = ac.getCarState(index, acsys.CS.SpeedKMH)
		CAR.node = ac.getCarState(index, acsys.CS.NormalizedSplinePosition)
		CAR.distance = distanceVertex(CAR.position, CARS[CAR_FOCUSED].position)


def acShutdown():
	THREAD_WORKER.stop()
	CONFIG.save()


def appRender(delta):
	RENDERER.render(delta)


def appActivate(val):
	THREAD_WORKER.run()


def appDismissed(val):
	THREAD_WORKER.stop()


class Config:
	def __init__(self, file):
		self.file = file
		self.renderWidth = 300
		self.renderHeight = 400
		self.renderFOV = 160
		self.performanceFPS = 30
		self.performanceNodeStep = 4
		self.viewTransparent = 90
		self.viewZoom = 14
		self.viewAutoZoom = True
		self.viewAutoZoomGain = 85
		self.viewOffset = -10
		self.viewForward = 220
		self.viewBackward = 70
		self.nameTagVisible = True
		self.nameTagOffset = 0
		self.nameTagWidth = 140
		self.nameTagSize = 14
		self.nameTagHeadType = "dist"
		self.nameTagViewSelf = True
		self.load()
		
		self.appId = 0
		self.gui_label_generic = 0
		self.gui_spinner_width = 0
		self.gui_spinner_height = 0
		self.gui_spinner_transparent = 0
		self.gui_label_view = 0
		self.gui_spinner_zoom = 0
		self.gui_spinner_fov = 0
		self.gui_spinner_offset = 0
		self.gui_checkbox_autozoom = 0
		self.gui_spinner_autozoom_gain = 0
		self.gui_label_nametag = 0
		self.gui_checkbox_nametag_visible = 0
		self.gui_label_nametag_enable = 0
		self.gui_label_nametag_header = 0
		self.gui_button_nametag_header_none = 0
		self.gui_button_nametag_header_rank = 0
		self.gui_button_nametag_header_dist = 0
		self.gui_spinner_nametag_offset = 0
		self.gui_spinner_nametag_width = 0
		self.gui_spinner_nametag_fontsize = 0
		self.gui_checkbox_nametag_view_self = 0
		self.gui_label_perf = 0
		self.gui_label_perf_preset = 0
		self.gui_button_perf_preset_low = 0
		self.gui_button_perf_preset_mid = 0
		self.gui_button_perf_preset_high = 0
		self.gui_button_perf_node_step = 0
		self.gui_button_perf_dist_forward = 0
		self.gui_button_perf_dist_backward = 0
		self.gui_button_perf_fps = 0
		self.initGUI()
	
	def load(self):
		parser = configparser.ConfigParser()
		try:
			parser.read(self.file)
			self.renderWidth = parser.getint("CONFIG", "WIDTH")
			self.renderHeight = parser.getint("CONFIG", "HEIGHT")
			self.renderFOV = parser.getint("CONFIG", "FOV")
			self.performanceFPS = parser.getint("CONFIG", "PREF_FPS")
			self.performanceNodeStep = parser.getint("CONFIG", "PREF_NODESTEP")
			self.viewTransparent = parser.getint("CONFIG", "TRANSPARENT")
			self.viewZoom = parser.getint("CONFIG", "ZOOM")
			self.viewAutoZoom = parser.getboolean("CONFIG", "AUTOZOOM")
			self.viewAutoZoomGain = parser.getint("CONFIG", "AUTOZOOM_GAIN")
			self.viewOffset = parser.getint("CONFIG", "OFFSET")
			self.viewForward = parser.getint("CONFIG", "VIEW_FORWARD")
			self.viewBackward = parser.getint("CONFIG", "VIEW_BACKWARD")
			self.nameTagVisible = parser.getboolean("CONFIG", "NAMETAG_VISIBLE")
			self.nameTagOffset = parser.getint("CONFIG", "NAMETAG_OFFSET")
			self.nameTagWidth = parser.getint("CONFIG", "NAMETAG_WIDTH")
			self.nameTagSize = parser.getint("CONFIG", "NAMETAG_FONTSIZE")
			self.nameTagHeadType = parser.get("CONFIG", "NAMETAG_HEAD_TYPE")
			self.nameTagViewSelf = parser.getboolean("CONFIG", "NAMETAG_VIEW_SELF")
		except:
			return
	
	def save(self):
		parser = configparser.ConfigParser()
		try:
			parser.add_section("CONFIG")
			parser.set("CONFIG", "WIDTH", str(self.renderWidth))
			parser.set("CONFIG", "HEIGHT", str(self.renderHeight))
			parser.set("CONFIG", "FOV", str(self.renderFOV))
			parser.set("CONFIG", "PREF_FPS", str(self.performanceFPS))
			parser.set("CONFIG", "PREF_NODESTEP", str(self.performanceNodeStep))
			parser.set("CONFIG", "TRANSPARENT", str(self.viewTransparent))
			parser.set("CONFIG", "ZOOM", str(self.viewZoom))
			parser.set("CONFIG", "AUTOZOOM", str(self.viewAutoZoom))
			parser.set("CONFIG", "AUTOZOOM_GAIN", str(self.viewAutoZoomGain))
			parser.set("CONFIG", "OFFSET", str(self.viewOffset))
			parser.set("CONFIG", "VIEW_FORWARD", str(self.viewForward))
			parser.set("CONFIG", "VIEW_BACKWARD", str(self.viewBackward))
			parser.set("CONFIG", "NAMETAG_VISIBLE", str(self.nameTagVisible))
			parser.set("CONFIG", "NAMETAG_OFFSET", str(self.nameTagOffset))
			parser.set("CONFIG", "NAMETAG_WIDTH", str(self.nameTagWidth))
			parser.set("CONFIG", "NAMETAG_FONTSIZE", str(self.nameTagSize))
			parser.set("CONFIG", "NAMETAG_HEAD_TYPE", str(self.nameTagHeadType))
			parser.set("CONFIG", "NAMETAG_VIEW_SELF", str(self.nameTagViewSelf))
			with open(self.file, "w") as data:
				parser.write(data)
		except:
			return
	
	def preset(self, mode):
		ac.setBackgroundColor(self.gui_button_perf_preset_low, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_button_perf_preset_low, 1)
		ac.setBackgroundColor(self.gui_button_perf_preset_mid, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_button_perf_preset_mid, 1)
		ac.setBackgroundColor(self.gui_button_perf_preset_high, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_button_perf_preset_high, 1)
		if mode == "low":
			self.performanceFPS = 30
			self.performanceNodeStep = 4
			self.viewForward = 220
			self.viewBackward = 70
			ac.setBackgroundColor(self.gui_button_perf_preset_low, 1, 0, 0)
		elif mode == "mid":
			self.performanceFPS = 60
			self.performanceNodeStep = 2
			self.viewForward = 230
			self.viewBackward = 80
			ac.setBackgroundColor(self.gui_button_perf_preset_mid, 1, 0, 0)
		elif mode == "high":
			self.performanceFPS = 60
			self.performanceNodeStep = 1
			self.viewForward = 240
			self.viewBackward = 90
			ac.setBackgroundColor(self.gui_button_perf_preset_high, 1, 0, 0)
		if THREAD_WORKER: THREAD_WORKER.setFPS()
		ac.setValue(self.gui_button_perf_fps, self.performanceFPS)
		ac.setValue(self.gui_button_perf_node_step, self.performanceNodeStep)
		ac.setValue(self.gui_button_perf_dist_forward, self.viewForward)
		ac.setValue(self.gui_button_perf_dist_backward, self.viewBackward)
		self.save()
	
	def changeNametagHeader(self, mode):
		ac.setBackgroundColor(self.gui_button_nametag_header_none, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_button_nametag_header_none, 1)
		ac.setBackgroundColor(self.gui_button_nametag_header_rank, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_button_nametag_header_rank, 1)
		ac.setBackgroundColor(self.gui_button_nametag_header_dist, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_button_nametag_header_dist, 1)
		self.nameTagHeadType = mode
		if mode == "rank":
			ac.setBackgroundColor(self.gui_button_nametag_header_rank, 1, 0, 0)
		elif mode == "dist":
			ac.setBackgroundColor(self.gui_button_nametag_header_dist, 1, 0, 0)
		else:
			ac.setBackgroundColor(self.gui_button_nametag_header_none, 1, 0, 0)
	
	def initGUI(self):
		self.appId = ac.newApp("3D Map Settings")
		ac.setSize(self.appId, 310, 580)
		ac.setTitle(self.appId, "3D Map Settings")
		
		self.gui_label_generic = ac.addLabel(self.appId, "  GENERIC")
		ac.setCustomFont(self.gui_label_generic, UI_FONT, 0, 1)
		ac.setFontSize(self.gui_label_generic, 14)
		ac.setPosition(self.gui_label_generic, 20, 35)
		ac.setFontColor(self.gui_label_generic, 0, 0, 0, 1)
		ac.setSize(self.gui_label_generic, 270, 20)
		ac.setBackgroundColor(self.gui_label_generic, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_label_generic, 1)
		
		self.gui_spinner_width = ac.addSpinner(self.appId, "Width")
		ac.setPosition(self.gui_spinner_width, 20, 80)
		ac.setSize(self.gui_spinner_width, 80, 20)
		ac.setStep(self.gui_spinner_width, 10)
		ac.setRange(self.gui_spinner_width, 10, 500)
		ac.setValue(self.gui_spinner_width, self.renderWidth)
		ac.addOnValueChangeListener(self.gui_spinner_width, onChangeRenderWidth)
		
		self.gui_spinner_height = ac.addSpinner(self.appId, "Height")
		ac.setPosition(self.gui_spinner_height, 115, 80)
		ac.setSize(self.gui_spinner_height, 80, 20)
		ac.setStep(self.gui_spinner_height, 10)
		ac.setRange(self.gui_spinner_height, 10, 500)
		ac.setValue(self.gui_spinner_height, self.renderHeight)
		ac.addOnValueChangeListener(self.gui_spinner_height, onChangeRenderHeight)
		
		self.gui_spinner_transparent = ac.addSpinner(self.appId, "Transparent")
		ac.setPosition(self.gui_spinner_transparent, 210, 80)
		ac.setSize(self.gui_spinner_transparent, 80, 20)
		ac.setStep(self.gui_spinner_transparent, 10)
		ac.setRange(self.gui_spinner_transparent, 0, 100)
		ac.setValue(self.gui_spinner_transparent, self.viewTransparent)
		ac.addOnValueChangeListener(self.gui_spinner_transparent, onChangeViewTransparent)
		
		self.gui_label_view = ac.addLabel(self.appId, "  VIEW")
		ac.setCustomFont(self.gui_label_view, UI_FONT, 0, 1)
		ac.setFontSize(self.gui_label_view, 14)
		ac.setPosition(self.gui_label_view, 20, 120)
		ac.setFontColor(self.gui_label_view, 0, 0, 0, 1)
		ac.setSize(self.gui_label_view, 270, 20)
		ac.setBackgroundColor(self.gui_label_view, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_label_view, 1)
		
		self.gui_spinner_zoom = ac.addSpinner(self.appId, "Zoom")
		ac.setPosition(self.gui_spinner_zoom, 20, 165)
		ac.setSize(self.gui_spinner_zoom, 80, 20)
		ac.setStep(self.gui_spinner_zoom, 1)
		ac.setRange(self.gui_spinner_zoom, 1, 30)
		ac.setValue(self.gui_spinner_zoom, self.viewZoom)
		ac.addOnValueChangeListener(self.gui_spinner_zoom, onChangeViewZoom)
		
		self.gui_spinner_fov = ac.addSpinner(self.appId, "FOV")
		ac.setPosition(self.gui_spinner_fov, 115, 165)
		ac.setSize(self.gui_spinner_fov, 80, 20)
		ac.setStep(self.gui_spinner_fov, 10)
		ac.setRange(self.gui_spinner_fov, 10, 800)
		ac.setValue(self.gui_spinner_fov, self.renderFOV)
		ac.addOnValueChangeListener(self.gui_spinner_fov, onChangeRenderFOV)
		
		self.gui_spinner_offset = ac.addSpinner(self.appId, "Offset")
		ac.setPosition(self.gui_spinner_offset, 210, 165)
		ac.setSize(self.gui_spinner_offset, 80, 20)
		ac.setStep(self.gui_spinner_offset, 1)
		ac.setRange(self.gui_spinner_offset, -30, 30)
		ac.setValue(self.gui_spinner_offset, self.viewOffset)
		ac.addOnValueChangeListener(self.gui_spinner_offset, onChangeViewOffset)
		
		self.gui_checkbox_autozoom = ac.addCheckBox(self.appId, "Auto zoom")
		ac.setCustomFont(self.gui_checkbox_autozoom, UI_FONT, 0, 0)
		ac.setPosition(self.gui_checkbox_autozoom, 20, 210)
		ac.setValue(self.gui_checkbox_autozoom, self.viewAutoZoom)
		ac.addOnCheckBoxChanged(self.gui_checkbox_autozoom, onChangeViewAutoZoom)
		
		self.gui_spinner_autozoom_gain = ac.addSpinner(self.appId, "Auto zoom Gain")
		ac.setPosition(self.gui_spinner_autozoom_gain, 210, 215)
		ac.setSize(self.gui_spinner_autozoom_gain, 80, 20)
		ac.setStep(self.gui_spinner_autozoom_gain, 5)
		ac.setRange(self.gui_spinner_autozoom_gain, 10, 100)
		ac.setValue(self.gui_spinner_autozoom_gain, self.viewAutoZoomGain)
		ac.addOnValueChangeListener(self.gui_spinner_autozoom_gain, onChangeViewAutoZoomGain)
		
		self.gui_label_nametag = ac.addLabel(self.appId, "  NAME TAG")
		ac.setCustomFont(self.gui_label_nametag, UI_FONT, 0, 1)
		ac.setFontSize(self.gui_label_nametag, 14)
		ac.setPosition(self.gui_label_nametag, 20, 255)
		ac.setFontColor(self.gui_label_nametag, 0, 0, 0, 1)
		ac.setSize(self.gui_label_nametag, 270, 20)
		ac.setBackgroundColor(self.gui_label_nametag, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_label_nametag, 1)
		
		self.gui_checkbox_nametag_visible = ac.addCheckBox(self.appId, "")
		ac.setPosition(self.gui_checkbox_nametag_visible, 260, 253)
		ac.setValue(self.gui_checkbox_nametag_visible, self.nameTagVisible)
		ac.addOnCheckBoxChanged(self.gui_checkbox_nametag_visible, onChangeNameTagVisible)
		
		self.gui_label_nametag_enable = ac.addLabel(self.appId, "ENABLE")
		ac.setFontSize(self.gui_label_nametag_enable, 12)
		ac.setFontAlignment(self.gui_label_nametag_enable, "right")
		ac.setPosition(self.gui_label_nametag_enable, 186, 257)
		ac.setFontColor(self.gui_label_nametag_enable, 0, 0, 0, 1)
		ac.setSize(self.gui_label_nametag_enable, 65, 16)
		
		self.gui_label_nametag_header = ac.addLabel(self.appId, "HEADER")
		ac.setFontSize(self.gui_label_nametag_header, 12)
		ac.setFontAlignment(self.gui_label_nametag_header, "left")
		ac.setPosition(self.gui_label_nametag_header, 30, 285)
		ac.setFontColor(self.gui_label_nametag_header, 1, 1, 1, 1)
		ac.setSize(self.gui_label_nametag_header, 65, 16)
		
		self.gui_button_nametag_header_none = ac.addLabel(self.appId, "NONE")
		ac.setCustomFont(self.gui_button_nametag_header_none, UI_FONT, 0, 1)
		ac.setFontSize(self.gui_button_nametag_header_none, 13)
		ac.setPosition(self.gui_button_nametag_header_none, 90, 285)
		ac.setSize(self.gui_button_nametag_header_none, 60, 20)
		ac.setFontColor(self.gui_button_nametag_header_none, 0, 0, 0, 1)
		ac.setBackgroundColor(self.gui_button_nametag_header_none, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_button_nametag_header_none, 1)
		ac.setFontAlignment(self.gui_button_nametag_header_none, "center")
		ac.addOnClickedListener(self.gui_button_nametag_header_none, onChangeNametagHeaderNone)
		
		self.gui_button_nametag_header_rank = ac.addLabel(self.appId, "RANK")
		ac.setCustomFont(self.gui_button_nametag_header_rank, UI_FONT, 0, 1)
		ac.setFontSize(self.gui_button_nametag_header_rank, 13)
		ac.setPosition(self.gui_button_nametag_header_rank, 160, 285)
		ac.setSize(self.gui_button_nametag_header_rank, 60, 20)
		ac.setFontColor(self.gui_button_nametag_header_rank, 0, 0, 0, 1)
		ac.setBackgroundColor(self.gui_button_nametag_header_rank, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_button_nametag_header_rank, 1)
		ac.setFontAlignment(self.gui_button_nametag_header_rank, "center")
		ac.addOnClickedListener(self.gui_button_nametag_header_rank, onChangeNametagHeaderRank)
		
		self.gui_button_nametag_header_dist = ac.addLabel(self.appId, "DIST")
		ac.setCustomFont(self.gui_button_nametag_header_dist, UI_FONT, 0, 1)
		ac.setFontSize(self.gui_button_nametag_header_dist, 13)
		ac.setPosition(self.gui_button_nametag_header_dist, 230, 285)
		ac.setSize(self.gui_button_nametag_header_dist, 60, 20)
		ac.setFontColor(self.gui_button_nametag_header_dist, 0, 0, 0, 1)
		ac.setBackgroundColor(self.gui_button_nametag_header_dist, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_button_nametag_header_dist, 1)
		ac.setFontAlignment(self.gui_button_nametag_header_dist, "center")
		ac.addOnClickedListener(self.gui_button_nametag_header_dist, onChangeNametagHeaderDist)
		
		self.changeNametagHeader(self.nameTagHeadType)
		
		self.gui_spinner_nametag_offset = ac.addSpinner(self.appId, "Offset")
		ac.setPosition(self.gui_spinner_nametag_offset, 20, 330)
		ac.setSize(self.gui_spinner_nametag_offset, 80, 20)
		ac.setStep(self.gui_spinner_nametag_offset, 1)
		ac.setRange(self.gui_spinner_nametag_offset, -100, 100)
		ac.setValue(self.gui_spinner_nametag_offset, self.nameTagOffset)
		ac.addOnValueChangeListener(self.gui_spinner_nametag_offset, onChangeNameTagOffset)
		
		self.gui_spinner_nametag_width = ac.addSpinner(self.appId, "Width")
		ac.setPosition(self.gui_spinner_nametag_width, 115, 330)
		ac.setSize(self.gui_spinner_nametag_width, 80, 20)
		ac.setStep(self.gui_spinner_nametag_width, 1)
		ac.setRange(self.gui_spinner_nametag_width, 10, 300)
		ac.setValue(self.gui_spinner_nametag_width, self.nameTagWidth)
		ac.addOnValueChangeListener(self.gui_spinner_nametag_width, onChangeNameTagWidth)
		
		self.gui_spinner_nametag_fontsize = ac.addSpinner(self.appId, "Font size")
		ac.setPosition(self.gui_spinner_nametag_fontsize, 210, 330)
		ac.setSize(self.gui_spinner_nametag_fontsize, 80, 20)
		ac.setStep(self.gui_spinner_nametag_fontsize, 1)
		ac.setRange(self.gui_spinner_nametag_fontsize, 5, 50)
		ac.setValue(self.gui_spinner_nametag_fontsize, self.nameTagSize)
		ac.addOnValueChangeListener(self.gui_spinner_nametag_fontsize, onChangeNameTagSize)
		
		self.gui_checkbox_nametag_view_self = ac.addCheckBox(self.appId, "Visible self")
		ac.setCustomFont(self.gui_checkbox_nametag_view_self, UI_FONT, 0, 0)
		ac.setPosition(self.gui_checkbox_nametag_view_self, 20, 370)
		ac.setValue(self.gui_checkbox_nametag_view_self, self.nameTagViewSelf)
		ac.addOnCheckBoxChanged(self.gui_checkbox_nametag_view_self, onChangeNameTagViewSelf)
		
		self.gui_label_perf = ac.addLabel(self.appId, "  PERFORMANCE")
		ac.setCustomFont(self.gui_label_perf, UI_FONT, 0, 1)
		ac.setFontSize(self.gui_label_perf, 14)
		ac.setPosition(self.gui_label_perf, 20, 410)
		ac.setFontColor(self.gui_label_perf, 0, 0, 0, 1)
		ac.setSize(self.gui_label_perf, 270, 20)
		ac.setBackgroundColor(self.gui_label_perf, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_label_perf, 1)
		
		self.gui_label_perf_preset = ac.addLabel(self.appId, "QUALITY")
		ac.setFontSize(self.gui_label_perf_preset, 12)
		ac.setFontAlignment(self.gui_label_perf_preset, "left")
		ac.setPosition(self.gui_label_perf_preset, 30, 440)
		ac.setFontColor(self.gui_label_perf_preset, 1, 1, 1, 1)
		ac.setSize(self.gui_label_perf_preset, 65, 16)
		
		self.gui_button_perf_preset_low = ac.addLabel(self.appId, "LOW")
		ac.setCustomFont(self.gui_button_perf_preset_low, UI_FONT, 0, 1)
		ac.setFontSize(self.gui_button_perf_preset_low, 13)
		ac.setPosition(self.gui_button_perf_preset_low, 90, 440)
		ac.setSize(self.gui_button_perf_preset_low, 60, 20)
		ac.setFontColor(self.gui_button_perf_preset_low, 0, 0, 0, 1)
		ac.setBackgroundColor(self.gui_button_perf_preset_low, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_button_perf_preset_low, 1)
		ac.setFontAlignment(self.gui_button_perf_preset_low, "center")
		ac.addOnClickedListener(self.gui_button_perf_preset_low, onChangePerformancePresetLOW)
		
		self.gui_button_perf_preset_mid = ac.addLabel(self.appId, "MIDDLE")
		ac.setCustomFont(self.gui_button_perf_preset_mid, UI_FONT, 0, 1)
		ac.setFontSize(self.gui_button_perf_preset_mid, 13)
		ac.setPosition(self.gui_button_perf_preset_mid, 160, 440)
		ac.setSize(self.gui_button_perf_preset_mid, 60, 20)
		ac.setFontColor(self.gui_button_perf_preset_mid, 0, 0, 0, 1)
		ac.setBackgroundColor(self.gui_button_perf_preset_mid, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_button_perf_preset_mid, 1)
		ac.setFontAlignment(self.gui_button_perf_preset_mid, "center")
		ac.addOnClickedListener(self.gui_button_perf_preset_mid, onChangePerformancePresetMID)
		
		self.gui_button_perf_preset_high = ac.addLabel(self.appId, "HIGH")
		ac.setCustomFont(self.gui_button_perf_preset_high, UI_FONT, 0, 1)
		ac.setFontSize(self.gui_button_perf_preset_high, 13)
		ac.setPosition(self.gui_button_perf_preset_high, 230, 440)
		ac.setSize(self.gui_button_perf_preset_high, 60, 20)
		ac.setFontColor(self.gui_button_perf_preset_high, 0, 0, 0, 1)
		ac.setBackgroundColor(self.gui_button_perf_preset_high, 1, 1, 1)
		ac.setBackgroundOpacity(self.gui_button_perf_preset_high, 1)
		ac.setFontAlignment(self.gui_button_perf_preset_high, "center")
		ac.addOnClickedListener(self.gui_button_perf_preset_high, onChangePerformancePresetHIGH)
		
		self.gui_button_perf_node_step = ac.addSpinner(self.appId, "node step")
		ac.setPosition(self.gui_button_perf_node_step, 20, 485)
		ac.setSize(self.gui_button_perf_node_step, 80, 20)
		ac.setStep(self.gui_button_perf_node_step, 1)
		ac.setRange(self.gui_button_perf_node_step, 1, 20)
		ac.setValue(self.gui_button_perf_node_step, self.performanceNodeStep)
		ac.addOnValueChangeListener(self.gui_button_perf_node_step, onChangePerformanceNodeStep)
		
		self.gui_button_perf_dist_forward = ac.addSpinner(self.appId, "dist Forward")
		ac.setPosition(self.gui_button_perf_dist_forward, 115, 485)
		ac.setSize(self.gui_button_perf_dist_forward, 80, 20)
		ac.setStep(self.gui_button_perf_dist_forward, 5)
		ac.setRange(self.gui_button_perf_dist_forward, 10, 300)
		ac.setValue(self.gui_button_perf_dist_forward, self.viewForward)
		ac.addOnValueChangeListener(self.gui_button_perf_dist_forward, onChangeViewForward)
		
		self.gui_button_perf_dist_backward = ac.addSpinner(self.appId, "dist Backward")
		ac.setPosition(self.gui_button_perf_dist_backward, 210, 485)
		ac.setSize(self.gui_button_perf_dist_backward, 80, 20)
		ac.setStep(self.gui_button_perf_dist_backward, 5)
		ac.setRange(self.gui_button_perf_dist_backward, 10, 300)
		ac.setValue(self.gui_button_perf_dist_backward, self.viewBackward)
		ac.addOnValueChangeListener(self.gui_button_perf_dist_backward, onChangeViewBackward)
		
		self.gui_button_perf_fps = ac.addSpinner(self.appId, "Calculate FPS")
		ac.setPosition(self.gui_button_perf_fps, 20, 535)
		ac.setSize(self.gui_button_perf_fps, 80, 20)
		ac.setStep(self.gui_button_perf_fps, 1)
		ac.setRange(self.gui_button_perf_fps, 1, 95)
		ac.setValue(self.gui_button_perf_fps, self.performanceFPS)
		ac.addOnValueChangeListener(self.gui_button_perf_fps, onChangePerformanceFPS)


def onChangeNametagHeaderNone(x, y):
	CONFIG.changeNametagHeader("none")
	if RENDERER: RENDERER.resizeNameTag()


def onChangeNametagHeaderRank(x, y):
	CONFIG.changeNametagHeader("rank")
	if RENDERER: RENDERER.resizeNameTag()


def onChangeNametagHeaderDist(x, y):
	CONFIG.changeNametagHeader("dist")
	if RENDERER: RENDERER.resizeNameTag()


def onChangePerformancePresetLOW(x, y):
	CONFIG.preset("low")


def onChangePerformancePresetMID(x, y):
	CONFIG.preset("mid")


def onChangePerformancePresetHIGH(x, y):
	CONFIG.preset("high")


def onChangeRenderWidth(value):
	CONFIG.renderWidth = value
	ac.setSize(RENDERER.appId, CONFIG.renderWidth, CONFIG.renderHeight)


def onChangeRenderHeight(value):
	CONFIG.renderHeight = value
	ac.setSize(RENDERER.appId, CONFIG.renderWidth, CONFIG.renderHeight)


def onChangeRenderFOV(value):
	CONFIG.renderFOV = value


def onChangePerformanceFPS(value):
	CONFIG.performanceFPS = value
	if THREAD_WORKER: THREAD_WORKER.setFPS()


def onChangePerformanceNodeStep(value):
	CONFIG.performanceNodeStep = value


def onChangeViewTransparent(value):
	CONFIG.viewTransparent = value


def onChangeViewZoom(value):
	CONFIG.viewZoom = value


def onChangeViewAutoZoom(name, value):
	CONFIG.viewAutoZoom = bool(value)


def onChangeViewAutoZoomGain(value):
	CONFIG.viewAutoZoomGain = value


def onChangeViewOffset(value):
	CONFIG.viewOffset = value


def onChangeViewForward(value):
	CONFIG.viewForward = value


def onChangeViewBackward(value):
	CONFIG.viewBackward = value


def onChangeNameTagVisible(name, value):
	CONFIG.nameTagVisible = bool(value)


def onChangeNameTagOffset(value):
	CONFIG.nameTagOffset = value


def onChangeNameTagWidth(value):
	CONFIG.nameTagWidth = value
	RENDERER.resizeNameTag()


def onChangeNameTagSize(value):
	CONFIG.nameTagSize = value
	RENDERER.resizeNameTag()


def onChangeNameTagViewSelf(name, value):
	CONFIG.nameTagViewSelf = bool(value)


class carState:
	def __init__(self, index=0, alive=False, name="", rank=0, position=vec2(), heading=0, speed=0, node=0):
		self.id = index
		self.alive = alive
		self.name = name
		self.rank = rank
		self.position = position
		self.heading = heading
		self.speed = speed
		self.node = node
		self.mesh = []
		self.distance = 0
		self.tagOffset = 0


class trackDetailNode:
	def __init__(self, rawIdeal, prevRawIdeal, rawDetail):
		self.id = rawIdeal[4]
		self.position = vec2(rawIdeal[0], rawIdeal[2])
		self.node = rawIdeal[3] / TRACK_LENGTH
		self.distance = rawIdeal[3]
		# self.direction = rawDetail[4]
		self.direction = -math.degrees(
			math.atan2(prevRawIdeal[2] - self.position.y,
			           self.position.x - prevRawIdeal[0]))
		
		_wallLeft = rawDetail[5]
		_wallRight = rawDetail[6]
		
		self.wallLeft = slideVec2(self.position, -self.direction + 90, _wallLeft)
		self.wallRight = slideVec2(self.position, -self.direction - 90, _wallRight)


class trackDetails:
	def __init__(self):
		self.available = False
		self.rawIdeal = []
		self.detail = []
		self.length = 0
		self.detailFile = "%s/ai/fast_lane.ai" % TRACK_DIRECTORY
		if os.path.isfile(self.detailFile):
			self.available = True
			self.readFastLane()
	
	def readFastLane(self):
		try:
			with open(self.detailFile, "rb") as buffer:
				header, self.length, lapTime, sampleCount = struct.unpack("4i", buffer.read(4 * 4))
				
				for i in range(self.length):
					self.rawIdeal.append(struct.unpack("4f i", buffer.read(4 * 5)))
				
				extraCount = struct.unpack("i", buffer.read(4))[0]
				for i in range(extraCount):
					prevRawIdeal = self.rawIdeal[i - 1] if i > 0 else self.rawIdeal[self.length - 1]
					self.detail.append(
						trackDetailNode(self.rawIdeal[i], prevRawIdeal, struct.unpack("18f", buffer.read(4 * 18))))
		except:
			self.available = False
	
	def getNearNodeIndex(self, nodePosition):
		nearNodeDiff = 1
		returnNodeIndex = 0
		for index, detail in enumerate(self.detail):
			nodeDiff = abs(nodePosition - detail.node)
			if nodeDiff < nearNodeDiff:
				nearNodeDiff = nodeDiff
				returnNodeIndex = index
			else:
				break
		return returnNodeIndex


class renderer:
	def __init__(self):
		self.appId = ac.newApp("3D Map")
		ac.setSize(self.appId, CONFIG.renderWidth, CONFIG.renderHeight)
		ac.setTitle(self.appId, " ")
		ac.drawBorder(self.appId, 0)
		ac.setIconPosition(self.appId, 0, -9000)
		ac.setBackgroundOpacity(self.appId, 0)
		ac.drawBackground(self.appId, 0)
		ac.addRenderCallback(self.appId, appRender)
		ac.addOnAppActivatedListener(self.appId, appActivate)
		ac.addOnAppDismissedListener(self.appId, appDismissed)
		self.nameTagHead = []
		self.nameTag = []
		
		for i in range(len(CARS)):
			_nameTagHead = ac.addLabel(self.appId, "")
			ac.setCustomFont(_nameTagHead, UI_FONT, 0, 1)
			ac.setFontColor(_nameTagHead, 1, *UI_COLOR_TEXT)
			ac.setFontAlignment(_nameTagHead, "center")
			ac.setVisible(_nameTagHead, 0)
			self.nameTagHead.append(_nameTagHead)
			
			_nameTag = ac.addLabel(self.appId, "")
			ac.setCustomFont(_nameTag, UI_FONT, 0, 0)
			ac.setFontColor(_nameTag, 1, *UI_COLOR_TEXT)
			ac.setFontAlignment(_nameTag, "left")
			ac.setBackgroundColor(_nameTag, *UI_COLOR_BGR)
			ac.setVisible(_nameTag, 0)
			self.nameTag.append(_nameTag)
		self.resizeNameTag()
	
	def resizeNameTag(self):
		TAG_HEAD_SIZE = 0
		if CONFIG.nameTagHeadType == "dist":
			TAG_HEAD_SIZE = CONFIG.nameTagSize * 3
		elif CONFIG.nameTagHeadType == "rank":
			TAG_HEAD_SIZE = CONFIG.nameTagSize * 2
		else:
			TAG_HEAD_SIZE = CONFIG.nameTagSize * 0.5
		for i in range(len(CARS)):
			ac.setFontSize(self.nameTagHead[i], CONFIG.nameTagSize)
			ac.setSize(self.nameTagHead[i], TAG_HEAD_SIZE, CONFIG.nameTagSize * 1.5)
			ac.setFontSize(self.nameTag[i], CONFIG.nameTagSize)
			ac.setSize(self.nameTag[i], CONFIG.nameTagWidth, CONFIG.nameTagSize * 1.5)
	
	def render(self, delta):
		THREAD_WORKER.run()
		ac.setBackgroundOpacity(self.appId, 0)
		
		for quad in THREAD_WORKER.mesh_track:
			if not quad: continue
			ac.glBegin(acsys.GL.Quads)
			for point in quad:
				ac.glColor4f(1, 1, 1, point[2])
				ac.glVertex2f(point[0], point[1])
			ac.glEnd()
		
		NAMETAG_ANY_OFFSET = 0
		NAMETAG_HIGHER_CAR = CARS[THREAD_WORKER.nameTagHigherID]
		if NAMETAG_HIGHER_CAR.mesh and NAMETAG_HIGHER_CAR.tagOffset > NAMETAG_HIGHER_CAR.mesh[2][1]:
			NAMETAG_ANY_OFFSET = (CARS[THREAD_WORKER.nameTagHigherID].tagOffset - CARS[THREAD_WORKER.nameTagHigherID].mesh[2][1]) / 2
		
		for CAR in CARS:
			COLOR = list(map(lambda x: x * pow(1 - (min(30, max(0, CAR.distance - 10)) / 100), 2), UI_COLOR_PICK))
			if CAR.alive and CAR.mesh:
				if CAR.id == CAR_FOCUSED:
					BASE_MESH = vecTriangle(vec2(CAR.mesh[0][0], CAR.mesh[0][1]), vec2(CAR.mesh[1][0], CAR.mesh[1][1]), vec2(CAR.mesh[2][0], CAR.mesh[2][1]))
					BASE_MESH.scale(1.3)
					ac.glBegin(acsys.GL.Triangles)
					ac.glColor4f(0, 0, 0, CAR.mesh[0][2])
					for point in BASE_MESH.points:
						ac.glVertex2f(point.x, point.y)
					ac.glEnd()
				ac.glBegin(acsys.GL.Triangles)
				for point in CAR.mesh:
					if CAR.id == CAR_FOCUSED:
						ac.glColor4f(1, 1, 1, point[2])
					else:
						ac.glColor4f(COLOR[0], COLOR[1], COLOR[2], point[2])
					ac.glVertex2f(point[0], point[1])
				ac.glEnd()
			
			if CONFIG.nameTagVisible and CAR.alive and CAR.mesh and not (not CONFIG.nameTagViewSelf and CAR.id == CAR_FOCUSED):
				TAG_POS_X = CONFIG.renderWidth + CONFIG.nameTagOffset
				TAG_POS_Y = CAR.tagOffset - NAMETAG_ANY_OFFSET
				TAG_ALPHA = CAR.mesh[0][2]
				ac.glBegin(acsys.GL.Lines)
				if CAR.id == CAR_FOCUSED: COLOR = UI_COLOR_PICK_SELF
				ac.glColor4f(COLOR[0], COLOR[1], COLOR[2], TAG_ALPHA)
				ac.glVertex2f(CAR.mesh[2][0], CAR.mesh[2][1])
				ac.glVertex2f(TAG_POS_X, TAG_POS_Y)
				ac.glEnd()
				
				TAG_HEAD_SIZE = 0
				if CONFIG.nameTagHeadType == "dist":
					ac.setText(self.nameTagHead[CAR.id], "{:>3}m".format(int(CAR.distance)) if CAR.id != CAR_FOCUSED else "---")
					TAG_HEAD_SIZE = CONFIG.nameTagSize * 3
				elif CONFIG.nameTagHeadType == "rank":
					ac.setText(self.nameTagHead[CAR.id], "{:>2}".format(int(CAR.rank)))
					TAG_HEAD_SIZE = CONFIG.nameTagSize * 2
				else:
					ac.setText(self.nameTagHead[CAR.id], "")
					TAG_HEAD_SIZE = CONFIG.nameTagSize * 0.5
				ac.setPosition(self.nameTagHead[CAR.id], TAG_POS_X, TAG_POS_Y - ((CONFIG.nameTagSize * 1.5) / 2))
				ac.setFontColor(self.nameTagHead[CAR.id], UI_COLOR_TEXT[0], UI_COLOR_TEXT[1], UI_COLOR_TEXT[2], TAG_ALPHA)
				ac.setVisible(self.nameTagHead[CAR.id], 1)
				ac.setBackgroundColor(self.nameTagHead[CAR.id], *(UI_COLOR_PICK_SELF if CAR.id == CAR_FOCUSED else COLOR))
				ac.setBackgroundOpacity(self.nameTagHead[CAR.id], TAG_ALPHA)
				
				ac.setText(self.nameTag[CAR.id], "  %s" % CAR.name)
				ac.setPosition(self.nameTag[CAR.id], TAG_POS_X + TAG_HEAD_SIZE, TAG_POS_Y - ((CONFIG.nameTagSize * 1.5) / 2))
				ac.setFontColor(self.nameTag[CAR.id], UI_COLOR_TEXT[0], UI_COLOR_TEXT[1], UI_COLOR_TEXT[2], TAG_ALPHA)
				ac.setVisible(self.nameTag[CAR.id], 1)
				ac.setBackgroundOpacity(self.nameTag[CAR.id], TAG_ALPHA)
			else:
				ac.setVisible(self.nameTagHead[CAR.id], 0)
				ac.setVisible(self.nameTag[CAR.id], 0)


def convertToScreenPos(point):
	z = (CONFIG.renderFOV * 2) - (point.y * 0.3)
	point.x = (CONFIG.renderFOV * point.x / z) + (CONFIG.renderWidth / 2)
	point.y = (CONFIG.renderFOV * CONFIG.renderHeight / z)
	return point


def getAlphaByPoint(point, factor=vec2(3.5)):
	alpha_x = ((CONFIG.renderWidth / 2) - abs(point.x - (CONFIG.renderWidth / 2))) / (CONFIG.renderWidth / factor.x)
	alpha_y = ((CONFIG.renderHeight / 2) - abs(point.y - (CONFIG.renderHeight / 2))) / (CONFIG.renderHeight / factor.y)
	return min(CONFIG.viewTransparent / 100, min(alpha_x, alpha_y))


class backgroundWorker:
	def __init__(self):
		self.running = False
		self.interval = 1 / CONFIG.performanceFPS
		self.mesh_track = []
		self.mesh_track_raw = []
		self.renderZoom = 1
		self.renderCenter = vec2()
		self.nameTagHigherID = 0
		self.thread = None
	
	def run(self):
		if not self.running:
			self.running = True
			self.thread = threading.Thread(target=self.loop)
			self.thread.setDaemon(True)
			self.thread.start()
	
	def stop(self):
		if self.running:
			self.running = False
			self.thread.join()
	
	def setFPS(self, fps=0):
		if fps == 0: fps = CONFIG.performanceFPS
		self.interval = 1 / fps
	
	def loop(self):
		while self.running:
			self.calculateCenter()
			self.calculateCars()
			self.calculateMap()
			time.sleep(self.interval)
    
	def calculateCenter(self):
		SELF_CAR = CARS[CAR_FOCUSED]
		self.renderZoom = CONFIG.viewZoom
		if CONFIG.viewAutoZoom:
			self.renderZoom /= pow((SELF_CAR.speed - (SELF_CAR.speed * (CONFIG.viewAutoZoomGain / 100))) / 100 + 1, 2)
		self.renderCenter = slideVec2(SELF_CAR.position, SELF_CAR.heading, CONFIG.viewOffset)
		self.renderCenter.mult(-1)
	
	def calculateCars(self):
		SELF_CAR = CARS[CAR_FOCUSED]
		
		for CAR in CARS:
			CAR.mesh = False
			if CAR.alive and CAR.position.x != 0 and CAR.position.y != 0:
				P1 = slideVec2(CAR.position.clone(), CAR.heading, -3)
				P2 = slideVec2(CAR.position.clone(), CAR.heading - 30, 3)
				P3 = slideVec2(CAR.position.clone(), CAR.heading + 30, 3)
				DELTA_RAW = vecTriangle(P1, P2, P3)
				DELTA_RAW.add(self.renderCenter)
				DELTA_RAW.rotate(SELF_CAR.heading + 90)
				DELTA_RAW.mult(self.renderZoom)
				DELTA_RAW_IN_RANGE = False
				for point in DELTA_RAW.points:
					convertToScreenPos(point)
					if 0 <= point.x <= CONFIG.renderWidth and 0 <= point.y <= CONFIG.renderHeight:
						DELTA_RAW_IN_RANGE = True
				AREA = triangleArea(DELTA_RAW)
				if DELTA_RAW_IN_RANGE and AREA > 10:
					DELTA = [None] * 3
					for i, point in enumerate(DELTA_RAW.points):
						DISTANCE_GAIN = 1 - min(1, CAR.distance / 150)
						ALPHA = max(0, min(DISTANCE_GAIN, getAlphaByPoint(point)))
						DELTA[i] = [point.x, point.y, ALPHA]
					CAR.mesh = DELTA
		
		if CONFIG.nameTagVisible:
			def sort(car):
				if not car.mesh: return 0
				return car.mesh[2][1]
			
			CARS_SORTED = sorted(CARS, key=sort)
			HIGHER_NAMETAG_Y = 0
			
			for CAR in CARS_SORTED:
				if not CONFIG.nameTagViewSelf and CAR.id == CAR_FOCUSED: continue
				if not CAR.mesh: continue
				CAR.tagOffset = CAR.mesh[2][1]
				if HIGHER_NAMETAG_Y + (CONFIG.nameTagSize * 1.5) + 5 > CAR.tagOffset:
					CAR.tagOffset = HIGHER_NAMETAG_Y + (CONFIG.nameTagSize * 1.5) + 5
				if HIGHER_NAMETAG_Y < CAR.tagOffset:
					self.nameTagHigherID = CAR.id
					HIGHER_NAMETAG_Y = CAR.tagOffset
				list(filter(lambda car_raw: car_raw.id == CAR.id, CARS))[0].tagOffset = CAR.tagOffset
	
	def calculateMap(self):
		if not TRACK_DETAILS.available: return
		SELF_CAR = CARS[CAR_FOCUSED]
		NODE_STEP = CONFIG.performanceNodeStep
		
		NEAR_NODE = TRACK_DETAILS.getNearNodeIndex(SELF_CAR.node) + NODE_STEP
		NEAR_NODE -= NEAR_NODE % NODE_STEP - NODE_STEP
		if NEAR_NODE < 0: NEAR_NODE += TRACK_DETAILS.length - 1
		PER = TRACK_DETAILS.length / TRACK_LENGTH
		NEAR_NODE_FORWARD = round(CONFIG.viewForward * PER)
		NEAR_NODE_BACKWARD = round(CONFIG.viewBackward * PER)
		
		RANGE_FORWARD = NEAR_NODE + (NEAR_NODE_FORWARD - (NEAR_NODE_FORWARD % NODE_STEP))
		RANGE_BACKWARD = NEAR_NODE - (NEAR_NODE_BACKWARD - (NEAR_NODE_BACKWARD % NODE_STEP))
		
		RANGE = range(RANGE_BACKWARD, RANGE_FORWARD, NODE_STEP)
		self.mesh_track_raw = [None] * len(RANGE)
		for i, index in enumerate(RANGE):
			NODE = index
			if NODE < 0:
				NODE += TRACK_DETAILS.length - 1
			elif NODE >= TRACK_DETAILS.length - NODE_STEP:
				NODE -= TRACK_DETAILS.length - 1
			
			NODE_PREV = NODE - NODE_STEP
			if NODE_PREV < 0:
				NODE_PREV += TRACK_DETAILS.length - 1
			
			P1 = TRACK_DETAILS.detail[NODE].wallRight.clone()
			P2 = TRACK_DETAILS.detail[NODE].wallLeft.clone()
			P3 = TRACK_DETAILS.detail[NODE_PREV].wallLeft.clone()
			P4 = TRACK_DETAILS.detail[NODE_PREV].wallRight.clone()
			
			QUAD_RAW = vecQuad(P1, P2, P3, P4)
			QUAD_RAW.add(self.renderCenter)
			QUAD_RAW.rotate(SELF_CAR.heading + 90)
			QUAD_RAW.mult(self.renderZoom)
			QUAD_IN_RANGE = False
			for point in QUAD_RAW.points:
				convertToScreenPos(point)
				if 0 <= point.x <= CONFIG.renderWidth and 0 <= point.y <= CONFIG.renderHeight:
					QUAD_IN_RANGE = True
			if QUAD_IN_RANGE:
				QUAD = [None] * 4
				W = NEAR_NODE_FORWARD if index >= NEAR_NODE else NEAR_NODE_BACKWARD
				for j, point in enumerate(QUAD_RAW.points):
					rawIndex = index if j < 2 else index - NODE_STEP
					DISTANCE_NODE = rawIndex - NEAR_NODE
					if DISTANCE_NODE < 0: DISTANCE_NODE = 0  # round(DISTANCE_NODE * 0.3)
					DISTANCE_GAIN = 1 - min(1, abs(DISTANCE_NODE) / W)
					ALPHA = max(0, min(DISTANCE_GAIN, getAlphaByPoint(point)))
					QUAD[j] = [point.x, point.y, ALPHA]
				self.mesh_track_raw[i] = QUAD
		self.mesh_track = self.mesh_track_raw
