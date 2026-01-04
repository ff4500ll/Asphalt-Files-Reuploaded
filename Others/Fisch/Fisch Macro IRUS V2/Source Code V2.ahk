setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
SetTitleMatchMode 2

CoordMode, Tooltip, Screen
CoordMode, Pixel, Screen
CoordMode, Mouse, Screen

PercentageScaling := Floor(100 * (A_ScreenDPI / 96))

sleep 100
WinActivate, Roblox
if !WinActive("Roblox")
	{
	msgbox, 0, No Roblox Instance Detected, Open Roblox First`n`nExiting Macro
	exitapp
	}

filePath := "GeneralSettings.txt"
filePath2 := "MinigameSettings.txt"
if !FileExist("GeneralSettings.txt")
{
	MsgBox, 1, First Time Setup, No configuration has been found`n`nOK = agree to auto subscribe`nCancel = exit
	ifMsgBox Cancel
	exitapp
	AutoLowerGraphics := 1
	AutoZoomIn := 1
	AutoLookDown := 1
	AutoCameraMode := 1
	AutoBlur := 1
	run https://www.youtube.com/@AsphaltCake/community/?sub_confirmation=1
	sleep 3000
	WinGetActiveStats, Title, WindowWidth, WindowHeight, WindowLeft, WindowTop
	SubscribeX := WindowLeft+(WindowWidth/2)
	SubscribeY := WindowTop+(WindowHeight/2)
	click, %SubscribeX%, %SubscribeY%
	send {tab}
	sleep 100
	send {tab}
	sleep 300
	send {enter}
	sleep 500
	send {enter}
	sleep 300
	send {ctrl down}
	sleep 100
	send w
	sleep 100
	send {ctrl up}
	WinActivate, Roblox
	
	MsgBox, 4, Lazy To Configure, % "Do you want to manually configure?`nNo = auto configure (not 100% accurate%)"
	ifMsgBox NO
	{
	goto V11AutoConfig
	}
	
	RedoConfigureNavigationKey:
	WinActivate, Roblox
	WinGetActiveStats, Title, WindowWidth, WindowHeight, WindowLeft, WindowTop
	send {esc}
	sleep 250
	send {tab}
	sleep 250
	MiddleX := WindowLeft+WindowWidth/2
	MiddleY := WindowTop+WindowHeight/2
	mousemove, %MiddleX%, %MiddleY%
	sleep 100
	loop 10,
	{
		send {wheeldown}
		sleep 10
	}
	InputBox, NavigationKey, Navigation Key, Enter the key used for navigation`n`nUI Navigation Toggle`nUse the _ key to enter and exit UI navigation mode, , , , 100, 100
	WinActivate, Roblox
	send {esc}
	sleep 250
	loop, 3
	{
		send %NavigationKey%
		sleep 250
		send %NavigationKey%
		sleep 250
	}
	MsgBox, 4, Navigation Key, Did the navigation mode activate?
	ifMsgBox No
	goto RedoConfigureNavigationKey
	
	mousemove, %MiddleX%, %MiddleY%
	sleep 200
	send {click}
	sleep 200
	Gui, +toolwindow +resize -caption +alwaysontop -border
	Gui, color, FFFFFF
	ResizeOrangeScanArea:
	Gui, Show
	WinMove, ahk_class AutoHotkeyGUI, , 200, 200, 400, 400
	Gui, +LastFound
	WinSet, Transparent, 100
	SetTimer, UpdateTooltips, 10
	OnMessage(0x201, "WM_LBUTTONDOWN")
	MsgBox, 0, Compass Scan Area, Set the white square to cover the compass at the top`nMake sure the orange "North" is visible
	SetTimer, UpdateTooltips, off
	OrangeLeft := Left
	OrangeRight := Right
	OrangeTop := Top
	OrangeBottom := Bottom
	ToolTip, , , , 17
	ToolTip, , , , 18
	ToolTip, , , , 19
	ToolTip, , , , 20
	Gui, Hide
	sleep 500

	OrangeColorTolerance := 10
	RedoConfigureOrangeTolerance:
	PixelSearch, , , OrangeLeft, OrangeTop, OrangeRight, OrangeBottom, 0x76B8E7, %OrangeColorTolerance%, Fast
	if (ErrorLevel == 0)
	{
		MsgBox, 4, Tolerance Wizard, Automated Tolerance Value: %OrangeColorTolerance%`n`nYes = Accept`nNo = Redo
		ifMsgBox NO
		{
			OrangeColorTolerance := 10
			goto ResizeOrangeScanArea
		}
	}
	else
	{
		OrangeColorTolerance := OrangeColorTolerance+1
		if (OrangeColorTolerance >= 50)
		{
			MsgBox, 4, Tolerance Wizard, FAILED TO DETECT (Current Tolerance: 50)`nDisabling Nuke Reset`n`nYes = Accept`nNo = Redo
			ifMsgBox NO
			{
				OrangeColorTolerance := 10
				goto ResizeOrangeScanArea 
			}
			else
			{
				AutoResetTimer := 0
			}
		}
		else
		{
			goto RedoConfigureOrangeTolerance
		}
	}

	InputBox, AutoResetTimer, Reset Timer, Delay per reset (in minutes)`n0 = disable, , , , 100, 100
	
	if (AutoResetTimer > 0)
	{
		AllowedLeft := WindowLeft+WindowWidth/2.04
		AllowedRight := WindowLeft+WindowWidth/1.96
		click, %MiddleX%, %MiddleY%
		sleep 100
		send {right down}
		sleep 2000
		ihatenamingtheseredothings:
		PixelSearch, OrangeX, , OrangeLeft, OrangeTop, OrangeRight, OrangeBottom, 0x76B8E7, %OrangeColorTolerance%, Fast
		if (ErrorLevel == 0)
		{
			if (OrangeX < AllowedLeft)
			{
			sleep 50
			send {right up}
			sleep 50
			send {left down}
			sleep 50
			goto ihatenamingtheseredothings
			}
			else if (OrangeX > AllowedRight)
			{
			sleep 50
			send {left up}
			sleep 50
			send {right down}
			sleep 50
			goto ihatenamingtheseredothings
			}
			send {right up}
			sleep 50
			send {left up}
			sleep 50
		}
		else
		{
			sleep 50
			goto ihatenamingtheseredothings
		}
	}
	
	WinActivate, Roblox
	send {shift up}
	sleep 250
	send {shift}
	sleep 250
	loop 10
	{
		send {f10}
		sleep 10
	}
	sleep 250
	send {shift down}
	sleep 250
	loop 10
	{
		send {f10}
		sleep 50
	}
	sleep 250
	send {shift up}
	MsgBox, 4, Auto Lower Graphics, Did your graphics get set to 1?
	ifMsgBox No
	{
	MsgBox, 1, Auto Lower Graphics, AutoLowerGraphics = false`n`nOK = continue`nCancel = Override to true
	ifMsgBox OK
		{
		AutoLowerGraphics := false
		}
	}

	WinActivate, Roblox
	loop 10
	{
		send {wheelup}
		sleep 10
	}
	sleep 250
	send {wheeldown}
	sleep 250
	MsgBox, 4, Auto Zoom In, Did your camera zoomed in to max,`nThen zoomed out by 1 scroll?
	ifMsgBox No
	{
	MsgBox, 1, Auto Zoom In, AutoZoomIn = false`n`nOK = continue`nCancel = Override to true
	ifMsgBox OK
		{
		AutoZoomIn := false
		}
	}
	
	WinActivate, Roblox
	mousemove, %MiddleX%, %MiddleY%
	sleep 500
	send {rbutton}
	sleep 500
	send {rbutton down}
	sleep 500
	DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 10000)
	sleep 250
	send {rbutton up}
	sleep 250
	mousemove, %MiddleX%, %MiddleY%
	sleep 250
	MsgBox, 4, Auto Look Down, Did your camera look down?
	ifMsgBox No
	{
	MsgBox, 1, Auto Look Down, AutoLookDown = false`n`nOK = continue`nCancel = Override to true
	ifMsgBox OK
		{
		AutoLookDown := false
		}
	}
	
	ResizeCameraWhiteScanArea:
	Gui, Show
	WinMove, ahk_class AutoHotkeyGUI, , 200, 200, 400, 400
	Gui, +LastFound
	WinSet, Transparent, 100
	SetTimer, UpdateTooltips, 10
	OnMessage(0x201, "WM_LBUTTONDOWN")
	MsgBox, 0, Camera Mode Scan Area, Set the white square to cover the scan area for "Open Backpack" located above the hotbar`n`nClick "Ok" once done
	WinActivate, Roblox
	sleep 500
	SetTimer, UpdateTooltips, off
	CameraLeft := Left
	CameraRight := Right
	CameraTop := Top
	CameraBottom := Bottom
	ToolTip, , , , 17
	ToolTip, , , , 18
	ToolTip, , , , 19
	ToolTip, , , , 20
	Gui, Hide
	sleep 500
	
	CameraWhiteTolerance := 0
	RedoConfigureCameraWhiteTolerance:
	PixelSearch, , , CameraLeft, CameraTop, CameraRight, CameraBottom, 0xFFFFFF, %CameraWhiteTolerance%, Fast
	if (ErrorLevel == 0)
	{
		MsgBox, 4, Tolerance Wizard, Automated Tolerance Value: %CameraWhiteTolerance%`n`nYes = Accept`nNo = Redo
		ifMsgBox NO
		{
			CameraWhiteTolerance := 0
			goto ResizeCameraWhiteScanArea
		}
		else
		{
			WinActivate, Roblox
			send 2
			sleep 500
			send 1
			sleep 500
			send %NavigationKey%
			sleep 250
			loop, 10
			{
				send {right}
				sleep 100
			}
			sleep 150
			send {enter}
			sleep 250
			MsgBox, 4, Auto Camera Mode, Was your camera mode automatically enabled?
			ifMsgBox NO
			{
			MsgBox, 1, Auto Camera Mode, AutoCameraMode = false`n`nOK = continue`nCancel = Override to true
			ifMsgBox OK
				{
				AutoCameraMode := 0
				}
			}
		}
	}
	else
	{
		CameraWhiteTolerance := CameraWhiteTolerance+1
		if (CameraWhiteTolerance >= 50)
		{
			MsgBox, 4, Tolerance Wizard, FAILED TO DETECT (Current Tolerance: 50)`nAutoCameraMode set to false`n`nYes = Accept`nNo = Redo
			ifMsgBox NO
			{
				CameraWhiteTolerance := 0
				goto ResizeCameraWhiteScanArea
			}
			else
			{
				AutoCameraMode := 0
			}
		}
		else
		{
			goto RedoConfigureCameraWhiteTolerance
		}
	}
	
	if (AutoCameraMode == 0)
	MsgBox, 0, Camera Mode, ENABLE CAMERA MODE MANUALLY BEFORE CLICKING OK`n`ntop right icon is camera mode
	
	WinActivate, Roblox
	sleep 250
	send {m}
	sleep 250
	MsgBox, 4, Auto Blur, Did your screen become blurred?
	ifMsgBox No
	{
	MsgBox, 1, Auto Blur, AutoBlur = false`n`nOK = continue`nCancel = Override to true
	ifMsgBox OK
		{
		AutoBlur := false
		}
	}
	
	WinActivate, Roblox
	mousemove, %MiddleX%, %MiddleY%
	send {lbutton up}
	sleep 250
	send {lbutton down}
	sleep 1000
	send {lbutton up}
	sleep 250
	
	ResizeShakeWhiteScanArea:
	Gui, Show
	WinMove, ahk_class AutoHotkeyGUI, , 200, 200, 400, 400
	Gui, +LastFound
	WinSet, Transparent, 100
	SetTimer, UpdateTooltips, 10
	OnMessage(0x201, "WM_LBUTTONDOWN")
	MsgBox, 0, Shake Scan Area, Set the white square to cover the scan area for WHEREVER shake could show up`n`nDO NOT INCLUDE CHAT OR LEADERBOARD`n`nClick "Ok" once done
	WinActivate, Roblox
	sleep 500
	SetTimer, UpdateTooltips, off
	ShakeLeft := Left
	ShakeRight := Right
	ShakeTop := Top
	ShakeBottom := Bottom
	ToolTip, , , , 17
	ToolTip, , , , 18
	ToolTip, , , , 19
	ToolTip, , , , 20
	Gui, Hide
	sleep 500
	
	ShakeWhiteTolerance := 0
	RedoConfigureShakeWhiteTolerance:
	PixelSearch, , , ShakeLeft, ShakeTop, ShakeRight, ShakeBottom, 0xFFFFFF, %ShakeWhiteTolerance%, Fast
	if (ErrorLevel == 0)
	{
		MsgBox, 4, Tolerance Wizard, Automated Tolerance Value: %ShakeWhiteTolerance%`n`nYes = Accept`nNo = Redo
		ifMsgBox NO
		{
			ShakeWhiteTolerance := 0
			goto ResizeShakeWhiteScanArea
		}
		else
		{
			ShakeMode := "Click"
		}
	}
	else
	{
		ShakeWhiteTolerance := ShakeWhiteTolerance+1
		if (ShakeWhiteTolerance >= 50)
		{
			MsgBox, 4, Tolerance Wizard, FAILED TO DETECT (Current Tolerance: 50)`nShake Mode set to Navigation`n`nYes = Accept`nNo = Redo
			ifMsgBox NO
			{
				ShakeWhiteTolerance := 0
				goto ResizeShakeWhiteScanArea 
			}
			else
			{
				ShakeMode := "Navigation"
			}
		}
		else
		{
			goto RedoConfigureShakeWhiteTolerance
		}
	}
	
	if (ShakeMode == "Click")
	{
		WinActivate, Roblox
		sleep 250
		ConfigureClickCounter := 0
		FailedConfigureClickCounter := 0
		ConfigureClickShakeRedo:
		PixelSearch, xxx, yyy, ShakeLeft, ShakeTop, ShakeRight, ShakeBottom, 0xFFFFFF, %ShakeWhiteTolerance%, Fast
		if (ErrorLevel == 0)
		{
			FailedConfigureClickCounter := 0
			ConfigureClickCounter++
			if (ConfigureClickCounter < 6)
			{
				click, %xxx%, %yyy%
				sleep 500
				goto ConfigureClickShakeRedo
			}
		}
		else
		{
			FailedConfigureClickCounter++
			if (FailedConfigureClickCounter < 25)
			{
			sleep 200
			goto ConfigureClickShakeRedo
			}
		}

		MsgBox, 4, Click Shake, Did the shake circles get clicked?`n`nYes = Use Click Mode`nNo = Switch to Navigation Mode
		ifMsgBox NO
		{
			ShakeMode := "Navigation"
		}
	}
	
	if (ShakeMode == "Navigation")
	{
		WinActivate, Roblox
		send %NavigationKey%
		sleep 250
		loop 5
		{
		send {s}
		sleep 250
		send {enter}
		sleep 250
		}
		MsgBox, 4, Navigation Shake, Did the shake circles get clicked?`n`nYes = Use Navigation Mode`nNo = U literally cannot shake
		ifMsgBox No
		{
			exitapp
		}
	}
	
	Gui, Show
	WinMove, ahk_class AutoHotkeyGUI, , 200, 200, 400, 400
	Gui, +LastFound
	WinSet, Transparent, 100
	SetTimer, UpdateTooltips, 10
	OnMessage(0x201, "WM_LBUTTONDOWN")
	MsgBox, 0, Minigame Bar, Drag the box over the minigame bar, allign the TOP LEFT of the TOOLTIPS (check youtube tutorial), not the actual box itself`n`nClick OK once alligned
	WinActivate, Roblox
	sleep 500
	SetTimer, UpdateTooltips, off
	BarLeft := Left
	BarRight := Right
	BarTop := Top
	BarBottom := Bottom
	ToolTip, , , , 17
	ToolTip, , , , 18
	ToolTip, , , , 19
	ToolTip, , , , 20
	Gui, Hide
	sleep 500
	
	ConfigureBarMinigameRedo3:
	FishBlueTolerance := 0
	ArrowTolerance := 0
	MsgBox, 0, Minigame Bar, Click Ok once u have RESET the minigame (check youtube tutorial)
	
	WinActivate, Roblox
	sleep 100
	ConfigureBarMinigameRedo:
	PixelSearch, , , BarLeft, BarTop, BarRight, BarBottom, 0x5B4B43, %FishBlueTolerance%, Fast
	if (ErrorLevel == 0)
	{
		ConfigureBarMinigameRedo2:
		PixelSearch, , , BarLeft, BarTop, BarRight, BarBottom, 0x878584, %ArrowTolerance%, Fast
		if (ErrorLevel == 0)
		{
			MsgBox, 4, Minigame Bar, Fish Bar Tolerance: %FishBlueTolerance%`nArrow Tolerance: %ArrowTolerance%`n`nYes = Accept`nNo = Redo
			ifMsgBox NO
			{
				goto ConfigureBarMinigameRedo3
			}			
		}
		else
		{
			ArrowTolerance := ArrowTolerance+1
			if (ArrowTolerance > 30)
			{
				goto ConfigureBarMinigameRedo3
			}
			sleep 50
			goto ConfigureBarMinigameRedo2
		}
	}
	else
	{
		FishBlueTolerance := FishBlueTolerance+1
		if (FishBlueTolerance > 30)
		{
			goto ConfigureBarMinigameRedo3
		}
		sleep 50
		goto ConfigureBarMinigameRedo
	}
	
	goto SkipAutoConfig
	V11AutoConfig:
	WinGetActiveStats, Title, AutoWidth, AutoHeight, AutoScreenLeft, AutoScreenTop
	NavigationKey := "\"
	AutoLowerGraphics := 1
	AutoZoomIn := 1
	AutoLookDown := 1
	AutoCameraMode := 1
	AutoBlur := 1
	CameraWhiteTolerance := 0
	CameraLeft := AutoScreenLeft+(AutoWidth/2.1694)
	CameraRight := AutoScreenLeft+(AutoWidth/1.8550)
	CameraTop := AutoScreenTop+(AutoHeight/1.1612)
	CameraBottom := AutoScreenTop+AutoHeight
	ShakeMode := "Click"
	ShakeWhiteTolerance := 0
	ShakeLeft := AutoScreenLeft+(AutoWidth/4.1967)
	ShakeRight := AutoScreenLeft+(AutoWidth/1.3128)
	ShakeTop := AutoScreenTop+(AutoHeight/4.4307)
	ShakeBottom := AutoScreenTop+(AutoHeight/1.0635)
	FishBlueTolerance := 0
	FishBarWhiteColorTolerance := 0
	ArrowTolerance := 0
	BarLeft := AutoScreenLeft+(AutoWidth/3.3464)
	BarRight := (AutoScreenLeft+AutoWidth)-(AutoWidth/3.3464)
	BarTop := AutoScreenTop+(AutoHeight/1.1842)
	BarBottom := AutoScreenTop+(AutoHeight/1.1501)
	HoldRodCastDuration := 1000
	WaitForBobberDelay := 1000
	EndMinigameDelay := 1500
	AutoResetTimer := 0
	OrangeColorTolerance := 0
	OrangeLeft := 0
	OrangeRight := 0
	OrangeTop := 0
	OrangeBottom := 0
	TurnRight := 0
	TurnLeft := 0
	SkipAutoConfig:
	
	FileAppend, NavigationKey=%NavigationKey%`n, %filePath%
	FileAppend, AutoLowerGraphics=%AutoLowerGraphics%`n, %filePath%
	FileAppend, AutoZoomIn=%AutoZoomIn%`n, %filePath%
	FileAppend, AutoLookDown=%AutoLookDown%`n, %filePath%
	FileAppend, AutoCameraMode=%AutoCameraMode%`n, %filePath%
	FileAppend, AutoBlur=%AutoBlur%`n`n, %filePath%
	
	FileAppend, CameraWhiteTolerance=%CameraWhiteTolerance%`n, %filePath%
	FileAppend, CameraLeft=%CameraLeft%`n, %filePath%
	FileAppend, CameraRight=%CameraRight%`n, %filePath%
	FileAppend, CameraTop=%CameraTop%`n, %filePath%
	FileAppend, CameraBottom=%CameraBottom%`n`n, %filePath%
	
	FileAppend, ShakeMode=%ShakeMode%`n, %filePath%
	FileAppend, ShakeWhiteTolerance=%ShakeWhiteTolerance%`n, %filePath%
	FileAppend, ShakeLeft=%ShakeLeft%`n, %filePath%
	FileAppend, ShakeRight=%ShakeRight%`n, %filePath%
	FileAppend, ShakeTop=%ShakeTop%`n, %filePath%
	FileAppend, ShakeBottom=%ShakeBottom%`n`n, %filePath%
	
	FileAppend, FishBlueTolerance=%FishBlueTolerance%`n, %filePath%
	FileAppend, FishBarWhiteColorTolerance=15`n, %filePath%
	FileAppend, ArrowTolerance=%ArrowTolerance%`n, %filePath%
	FileAppend, BarLeft=%BarLeft%`n, %filePath%
	FileAppend, BarRight=%BarRight%`n, %filePath%
	FileAppend, BarTop=%BarTop%`n, %filePath%
	FileAppend, BarBottom=%BarBottom%`n`n, %filePath%
	
	FileAppend, HoldRodCastDuration=1000`n, %filePath%
	FileAppend, WaitForBobberDelay=1000`n, %filePath%
	FileAppend, EndMinigameDelay=1500`n`n, %filePath%
	
	FileAppend, AutoResetTimer=%AutoResetTimer%`n, %filePath%
	FileAppend, OrangeColorTolerance=%OrangeColorTolerance%`n, %filePath%
	FileAppend, OrangeLeft=%OrangeLeft%`n, %filePath%
	FileAppend, OrangeRight=%OrangeRight%`n, %filePath%
	FileAppend, OrangeTop=%OrangeTop%`n, %filePath%
	FileAppend, OrangeBottom=%OrangeBottom%`n, %filePath%
	FileAppend, TurnRight=0`n, %filePath%
	FileAppend, TurnLeft=0`n, %filePath%
}
FileReadLine, NavigationKey, %filePath%, 1
StringSplit, arr, NavigationKey, =
NavigationKey := arr2
FileReadLine, AutoLowerGraphics, %filePath%, 2
StringSplit, arr, AutoLowerGraphics, =
AutoLowerGraphics := arr2
FileReadLine, AutoZoomIn, %filePath%, 3
StringSplit, arr, AutoZoomIn, =
AutoZoomIn := arr2
FileReadLine, AutoLookDown, %filePath%, 4
StringSplit, arr, AutoLookDown, =
AutoLookDown := arr2
FileReadLine, AutoCameraMode, %filePath%, 5
StringSplit, arr, AutoCameraMode, =
AutoCameraMode := arr2
FileReadLine, AutoBlur, %filePath%, 6
StringSplit, arr, AutoBlur, =
AutoBlur := arr2
FileReadLine, CameraWhiteTolerance, %filePath%, 8
StringSplit, arr, CameraWhiteTolerance, =
CameraWhiteTolerance := arr2
FileReadLine, CameraLeft, %filePath%, 9
StringSplit, arr, CameraLeft, =
CameraLeft := arr2
FileReadLine, CameraRight, %filePath%, 10
StringSplit, arr, CameraRight, =
CameraRight := arr2
FileReadLine, CameraTop, %filePath%, 11
StringSplit, arr, CameraTop, =
CameraTop := arr2
FileReadLine, CameraBottom, %filePath%, 12
StringSplit, arr, CameraBottom, =
CameraBottom := arr2
FileReadLine, ShakeMode, %filePath%, 14
StringSplit, arr, ShakeMode, =
ShakeMode := arr2
FileReadLine, ShakeWhiteTolerance, %filePath%, 15
StringSplit, arr, ShakeWhiteTolerance, =
ShakeWhiteTolerance := arr2
FileReadLine, ShakeLeft, %filePath%, 16
StringSplit, arr, ShakeLeft, =
ShakeLeft := arr2
FileReadLine, ShakeRight, %filePath%, 17
StringSplit, arr, ShakeRight, =
ShakeRight := arr2
FileReadLine, ShakeTop, %filePath%, 18
StringSplit, arr, ShakeTop, =
ShakeTop := arr2
FileReadLine, ShakeBottom, %filePath%, 19
StringSplit, arr, ShakeBottom, =
ShakeBottom := arr2
FileReadLine, FishBlueTolerance, %filePath%, 21
StringSplit, arr, FishBlueTolerance, =
FishBlueTolerance := arr2
FileReadLine, FishBarWhiteColorTolerance, %filePath%, 22
StringSplit, arr, FishBarWhiteColorTolerance, =
FishBarWhiteColorTolerance := arr2
FileReadLine, ArrowTolerance, %filePath%, 23
StringSplit, arr, ArrowTolerance, =
ArrowTolerance := arr2
FileReadLine, BarLeft, %filePath%, 24
StringSplit, arr, BarLeft, =
BarLeft := arr2
FileReadLine, BarRight, %filePath%, 25
StringSplit, arr, BarRight, =
BarRight := arr2
FileReadLine, BarTop, %filePath%, 26
StringSplit, arr, BarTop, =
BarTop := arr2
FileReadLine, BarBottom, %filePath%, 27
StringSplit, arr, BarBottom, =
BarBottom := arr2
FileReadLine, HoldRodCastDuration, %filePath%, 29
StringSplit, arr, HoldRodCastDuration, =
HoldRodCastDuration := arr2
FileReadLine, WaitForBobberDelay, %filePath%, 30
StringSplit, arr, WaitForBobberDelay, =
WaitForBobberDelay := arr2
FileReadLine, EndMinigameDelay, %filePath%, 31
StringSplit, arr, EndMinigameDelay, =
EndMinigameDelay := arr2
FileReadLine, AutoResetTimer, %filePath%, 33
StringSplit, arr, AutoResetTimer, =
AutoResetTimer := arr2
FileReadLine, OrangeColorTolerance, %filePath%, 34
StringSplit, arr, OrangeColorTolerance, =
OrangeColorTolerance := arr2
FileReadLine, OrangeLeft, %filePath%, 35
StringSplit, arr, OrangeLeft, =
OrangeLeft := arr2
FileReadLine, OrangeRight, %filePath%, 36
StringSplit, arr, OrangeRight, =
OrangeRight := arr2
FileReadLine, OrangeTop, %filePath%, 37
StringSplit, arr, OrangeTop, =
OrangeTop := arr2
FileReadLine, OrangeBottom, %filePath%, 38
StringSplit, arr, OrangeBottom, =
OrangeBottom := arr2
FileReadLine, TurnRight, %filePath%, 39
StringSplit, arr, TurnRight, =
TurnRight := arr2
FileReadLine, TurnLeft, %filePath%, 40
StringSplit, arr, TurnLeft, =
TurnLeft := arr2

filePath2 := "MinigameSettings.txt"
if !FileExist("MinigameSettings.txt")
{
	FileAppend, Author=AsphaltCake`n`n, %filePath2%
	
	FileAppend, BarSideRatio=0.75`n, %filePath2%
	FileAppend, DeadZoneRatio=0.1`n, %filePath2%
	FileAppend, MinLeftSideWait=700`n, %filePath2%
	FileAppend, MinRightSideWait=700`n`n, %filePath2%
	
	FileAppend, RightMultiplier=2.7`n, %filePath2%
	FileAppend, RightDivision=1.2`n, %filePath2%
	FileAppend, LeftMultiplier=2.7`n, %filePath2%
	FileAppend, LeftDivision=1.2`n`n, %filePath2%
	
	FileAppend, RightAnkleBreakMultiplier=1.25`n, %filePath2%
	FileAppend, LeftAnkleBreakMultiplier=0.75`n`n, %filePath2%
	
	FileAppend, ScanDelay=10, %filePath2%
}
FileReadLine, Author, %filePath2%, 1
StringSplit, arr, Author, =
Author := arr2
FileReadLine, BarSideRatio, %filePath2%, 3
StringSplit, arr, BarSideRatio, =
BarSideRatio := arr2
FileReadLine, DeadZoneRatio, %filePath2%, 4
StringSplit, arr, DeadZoneRatio, =
DeadZoneRatio := arr2
FileReadLine, MinLeftSideWait, %filePath2%, 5
StringSplit, arr, MinLeftSideWait, =
MinLeftSideWait := arr2
FileReadLine, MinRightSideWait, %filePath2%, 6
StringSplit, arr, MinRightSideWait, =
MinRightSideWait := arr2
FileReadLine, RightMultiplier, %filePath2%, 8
StringSplit, arr, RightMultiplier, =
RightMultiplier := arr2
FileReadLine, RightDivision, %filePath2%, 9
StringSplit, arr, RightDivision, =
RightDivision := arr2
FileReadLine, LeftMultiplier, %filePath2%, 10
StringSplit, arr, LeftMultiplier, =
LeftMultiplier := arr2
FileReadLine, LeftDivision, %filePath2%, 11
StringSplit, arr, LeftDivision, =
LeftDivision := arr2
FileReadLine, RightAnkleBreakMultiplier, %filePath2%, 13
StringSplit, arr, RightAnkleBreakMultiplier, =
RightAnkleBreakMultiplier := arr2
FileReadLine, LeftAnkleBreakMultiplier, %filePath2%, 13
StringSplit, arr, LeftAnkleBreakMultiplier, =
LeftAnkleBreakMultiplier := arr2
FileReadLine, ScanDelay, %filePath2%, 13
StringSplit, arr, ScanDelay, =
ScanDelay := arr2

WinActivate, Roblox
sleep 250
WinGetActiveStats, Title, WindowWidth, WindowHeight, WindowLeft, WindowTop
DynamicTooltip := 20/100*PercentageScaling
TooltipX := WindowWidth/DynamicTooltip
Tooltip1 := (WindowHeight/2)-(DynamicTooltip*9)
Tooltip2 := (WindowHeight/2)-(DynamicTooltip*8)
Tooltip3 := (WindowHeight/2)-(DynamicTooltip*7)
Tooltip4 := (WindowHeight/2)-(DynamicTooltip*6)
Tooltip5 := (WindowHeight/2)-(DynamicTooltip*5)
Tooltip6 := (WindowHeight/2)-(DynamicTooltip*4)
Tooltip7 := (WindowHeight/2)-(DynamicTooltip*3)
Tooltip8 := (WindowHeight/2)-(DynamicTooltip*2)
Tooltip9 := (WindowHeight/2)-(DynamicTooltip*1)
Tooltip10 := (WindowHeight/2)-(DynamicTooltip)
MsgBox, 0, Fisch v.IRUS, Made By AsphaltCake, 1

tooltip, Made By AsphaltCake (YT), %TooltipX%, %Tooltip1%, 1
tooltip, Settings By %Author%, %TooltipX%, %Tooltip2%, 2
tooltip, P = Start | M = Exit, %TooltipX%, %Tooltip3%, 3
tooltip, O = Reload, %TooltipX%, %Tooltip4%, 4
return

WM_LBUTTONDOWN(wParam, lParam, msg, hwnd)
{
    PostMessage, 0xA1, 2
}

UpdateTooltips:
    WinGetPos, X, Y, Width, Height, ahk_class AutoHotkeyGUI
    Left := X
    Right := X + Width
    Top := Y
    Bottom := Y + Height
	XHalf := Left+Width/2
	YHalf := Top+Height/2
    ToolTip, Left: %Left%, %Left%, %YHalf%, 17
    ToolTip, Right: %Right%, %Right%, %YHalf%, 18
    ToolTip, Top: %Top%, %XHalf%, %Top%, 19
    ToolTip, Bottom: %Bottom%, %XHalf%, %Bottom%, 20
return

$m:: exitapp
$o:: reload
$p::

WinActivate, Roblox
sleep 250
WinGetActiveStats, Title, WindowWidth, WindowHeight, WindowLeft, WindowTop
sleep 250
MiddleX := WindowLeft+WindowWidth/2
MiddleY := WindowTop+WindowHeight/2
ShakeDelay := 100

FishBarTooltipHeight := BarBottom+30

DynamicTooltip := 20/100*PercentageScaling
TooltipX := WindowWidth/DynamicTooltip
Tooltip1 := (WindowHeight/2)-(DynamicTooltip*9)
Tooltip2 := (WindowHeight/2)-(DynamicTooltip*8)
Tooltip3 := (WindowHeight/2)-(DynamicTooltip*7)
Tooltip4 := (WindowHeight/2)-(DynamicTooltip*6)
Tooltip5 := (WindowHeight/2)-(DynamicTooltip*5)
Tooltip6 := (WindowHeight/2)-(DynamicTooltip*4)
Tooltip7 := (WindowHeight/2)-(DynamicTooltip*3)
Tooltip8 := (WindowHeight/2)-(DynamicTooltip*2)
Tooltip9 := (WindowHeight/2)-(DynamicTooltip*1)
Tooltip10 := (WindowHeight/2)-(DynamicTooltip)

PixelScaling := 1034/(BarRight-BarLeft)

tooltip, Made By AsphaltCake (YT), %TooltipX%, %Tooltip1%, 1
tooltip, Settings By %Author%, %TooltipX%, %Tooltip2%, 2
tooltip, P = Start | M = Exit, %TooltipX%, %Tooltip3%, 3
tooltip, O = Reload, %TooltipX%, %Tooltip4%, 4

IHateCountersCounterSECOND := 0
IHateCountersCounterMINUTE := 0
IHateCountersCounterHOUR := 0
ForTheEverLovingCOUNTERGOD := 0
settimer, InfiniteDomainExpansion, 1000

if (AutoLowerGraphics == 1)
{
	send {shift up}
	sleep 250
	send {shift}
	sleep 250
	send {shift down}
	sleep 250
	loop 10
	{
		send {f10}
		sleep 50
	}
	sleep 250
	send {shift up}
	sleep 250
}

if (AutoZoomIn == 1)
{
	loop 10
	{
		send {wheelup}
		sleep 10
	}
	sleep 250
	send {wheeldown}
	sleep 250
}

ItsTimeToDOIT := true
Restart:
if (AutoCameraMode == 1 and ItsTimeToDOIT == true and AutoResetTimer > 0)
{
	ItsTimeToDOIT := false
	blablabla:
	PixelSearch, , , CameraLeft, CameraTop, CameraRight, CameraBottom, 0xFFFFFF, %CameraWhiteTolerance%, Fast
	if (ErrorLevel == 0)
	{
		AllowedLeft := WindowLeft+WindowWidth/2.04
		AllowedRight := WindowLeft+WindowWidth/1.96
		click, %MiddleX%, %MiddleY%
		sleep 100
		send {right down}
		sleep 2000
		ihatenamingtheseredothingswasd:
		PixelSearch, OrangeX, , OrangeLeft, OrangeTop, OrangeRight, OrangeBottom, 0x76B8E7, %OrangeColorTolerance%, Fast
		if (ErrorLevel == 0)
		{
			if (OrangeX > AllowedLeft and OrangeX < AllowedRight)
			{
				send {right up}
				send {left up}
				sleep 100
				if (TurnLeft != 0 or TurnRight != 0)
				{
					if (TurnLeft > TurnRight)
					{
						send {left down}
						sleep %TurnLeft%
						send {left up}
						sleep 250
					}
					else
					{
						send {right down}
						sleep %TurnRight%
						send {right up}
						sleep 250
					}
				}
				if (AutoZoomIn == 1)
				{
					loop 10
					{
						send {wheelup}
						sleep 10
					}
					sleep 250
					send {wheeldown}
					sleep 250
				}
			}
			else
			{
				sleep 50
				goto ihatenamingtheseredothingswasd
			}
		}
		else
		{
			sleep 10
			goto ihatenamingtheseredothingswasd
		}	
	}
	else
	{
		send 2
		sleep 500
		send 1
		sleep 500
		send %NavigationKey%
		sleep 250
		loop, 10
		{
			send {right}
			sleep 100
		}
		sleep 150
		send {enter}
		sleep 250
		goto blablabla
	}
}

if (AutoLookDown == 1)
{
	sleep 250
	mousemove, %MiddleX%, %MiddleY%
	sleep 500
	send {rbutton}
	sleep 500
	send {rbutton down}
	sleep 500
	DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 10000)
	sleep 250
	send {rbutton up}
	sleep 250
	mousemove, %MiddleX%, %MiddleY%
	sleep 250
}

if (AutoCameraMode == 1)
{
	PixelSearch, , , CameraLeft, CameraTop, CameraRight, CameraBottom, 0xFFFFFF, %CameraWhiteTolerance%, Fast
	if (ErrorLevel == 0)
	{
		send 2
		sleep 500
		send 1
		sleep 500
		send %NavigationKey%
		sleep 250
		loop, 10
		{
			send {right}
			sleep 100
		}
		sleep 150
		send {enter}
		sleep 250		
	}
}

if (AutoBlur == 1)
{
	send {m}
	sleep 250
}

send {lbutton up}
sleep 500
send {lbutton down}
sleep %HoldRodCastDuration%
send {lbutton up}
sleep %WaitForBobberDelay%

if (ShakeMode == "Click")
{
	FailsafeTriggered := false
	FailsafeCount := 0
	FailsafeLimit := 20
	settimer, FailsafeCounter, 1000
	MemoryX := 0
	MemoryY := 0
	DoubleCounter := 0
	ClickShakeRedo:
	if (FailsafeTriggered == true)
	goto Restart
	sleep %ShakeDelay%
	PixelSearch, , , BarLeft, BarTop, BarRight, BarBottom, 0x5B4B43, %FishBlueTolerance%, Fast
	if (ErrorLevel == 0)
	{
		tooltip, , , , 7
		settimer, FailsafeCounter, off
		goto BarMinigameStart
	}
	else
	{
		PixelSearch, ClickX, ClickY, ShakeLeft, ShakeTop, ShakeRight, ShakeBottom, 0xFFFFFF, %ShakeWhiteTolerance%, Fast
		if (ErrorLevel == 0)
		{
			if (ClickX != MemoryX and ClickY != MemoryY)
			{
				DoubleCounter := 0
				FailCounter := 0
				click, %ClickX%, %ClickY%
				MemoryX := ClickX
				MemoryY := ClickY
			}
			else
			{
				DoubleCounter++
				if (DoubleCounter >= 3)
				{
					ShakeDelay := ShakeDelay-30
					MemoryX := 0
					MemoryY := 0
				}
				else
				{
					ShakeDelay := ShakeDelay+10
				}
			}
		}
		goto ClickShakeRedo
	}
}
else if (ShakeMode == "Navigation")
{
	FailsafeTriggered := false
	FailsafeCount := 0
	FailsafeLimit := 30
	settimer, FailsafeCounter, 1000
	send %NavigationKey%
	sleep 500
	NavigationShakeRedo:
	if (FailsafeTriggered == true)
	goto Restart	
	PixelSearch, , , BarLeft, BarTop, BarRight, BarBottom, 0x5B4B43, %FishBlueTolerance%, Fast
	if (ErrorLevel == 0)
	{
		tooltip, , , , 7
		settimer, FailsafeCounter, off
		goto BarMinigameStart
	}
	else
	{
		send {s}
		sleep 50
		send {enter}
		sleep 50
		goto NavigationShakeRedo
	}
}
else
{
	msgbox, UNKNOWN SHAKE MODE (exiting)
	exitapp
}

BarMinigameStart:

EndFishMinigame := false
sleep 100
PixelSearch, BarX, , BarLeft, BarTop, BarRight, BarBottom, 0xFFFFFF, %FishBarWhiteColorTolerance%, Fast
FullBar := (BarRight-(BarX-BarLeft))-BarX
HalfBar := FullBar/2
Deadzone := FullBar*0.1
LeftMax := BarLeft+(FullBar*BarSideRatio)
RightMax := BarRight-(FullBar*BarSideRatio)

settimer, PerfectTrackingBar, %ScanDelay%

BarMinigameRedo:
if (EndFishMinigame == true)
{
	sleep %EndMinigameDelay%
	goto Restart
}
if (Action == 0)
{
	; nothing
	SideToggle := false
	send {lbutton down}
	sleep 10
	send {lbutton up}
	sleep 10
}
else if (Action == 1)
{
	; <<<
	SideToggle := false
	send {lbutton up}
	if (AnkleBreak == false)
	{
		sleep %AnkleBreakDuration%
		AnkleBreakDuration := 0
	}
	Duration := Abs(Direction)*LeftMultiplier*PixelScaling
	sleep %Duration%
	send {lbutton down}
	CounterStrafe := Duration/LeftDivision
	sleep %CounterStrafe%
	AnkleBreak := true
	AnkleBreakDuration := AnkleBreakDuration+(Duration-CounterStrafe)
}
else if (Action == 2)
{
	; >>>
	SideToggle := false
	send {lbutton down}
	if (AnkleBreak == true)
	{
		sleep %AnkleBreakDuration%
		AnkleBreakDuration := 0
	}
	Duration := Abs(Direction)*RightMultiplier*PixelScaling
	sleep %Duration%
	send {lbutton up}
	CounterStrafe := Duration/RightDivision
	sleep %CounterStrafe%
	AnkleBreak := false
	AnkleBreakDuration := AnkleBreakDuration+(Duration-CounterStrafe)
}
else if (Action == 3)
{
	; max <
	if (SideToggle == false)
	{
		AnkleBreak := none
		AnkleBreakDuration := 0
		SideToggle := true
		send {lbutton up}
		sleep %MinLeftSideWait%	
	}
	sleep %ScanDelay%
}
else if (Action == 4)
{
	; max >
	if (SideToggle == false)
	{
		AnkleBreak := none
		AnkleBreakDuration := 0
		SideToggle := true
		send {lbutton down}
		sleep %MinRightSideWait%	
	}
	sleep %ScanDelay%
}
else
{
	sleep %ScanDelay%
}
goto BarMinigameRedo

PerfectTrackingBar:
PixelSearch, FishX, , BarLeft, BarTop, BarRight, BarBottom, 0x5B4B43, %FishBlueTolerance%, Fast
if (ErrorLevel == 0)
{
	tooltip, |, %FishX%, %FishBarTooltipHeight%, 20
	if (FishX < LeftMax)
		{
			Action := 3
			tooltip, |, %LeftMax%, %FishBarTooltipHeight%, 19
			return
		}
	else if (FishX > RightMax)
		{
			Action := 4
			tooltip, |, %RightMax%, %FishBarTooltipHeight%, 19
			return
		}
	PixelSearch, BarX, , BarLeft, BarTop, BarRight, BarBottom, 0xFFFFFF, %FishBarWhiteColorTolerance%, Fast
	if (ErrorLevel == 0)
	{
		BarX := BarX+HalfBar
		Direction := BarX-FishX
		if (Direction > Deadzone)
		{
			Action := 1
			tooltip, <, %BarX%, %FishBarTooltipHeight%, 19
		}
		else if (Direction < -Deadzone)
		{
			Action := 2
			tooltip, >, %BarX%, %FishBarTooltipHeight%, 19
		}
		else
		{
			Action := 0
			tooltip, ., %BarX%, %FishBarTooltipHeight%, 19	
		}	
	}
	else
	{
		Direction := HalfBar
		PixelGetColor, color, 746, 1207
		PixelSearch, ArrowX, , BarLeft, BarTop, BarRight, BarBottom, 0x878584, %ArrowTolerance%, Fast
		ArrowX := ArrowX-FishX
		if (ArrowX > 0)
		{
			Action := 1
			BarX := FishX+HalfBar
			tooltip, <, %BarX%, %FishBarTooltipHeight%, 19	
		}
		else
		{
			Action := 2
			BarX := FishX-HalfBar
			tooltip, >, %BarX%, %FishBarTooltipHeight%, 19	
		}
	}
}
else
{
	tooltip, , , , 19
	tooltip, , , , 20
	EndFishMinigame := true
	settimer, PerfectTrackingBar, off
}
return

FailsafeCounter:
FailsafeCount++
tooltip, Failsafe: %FailsafeCount%/%FailsafeLimit%, %TooltipX%, %Tooltip7%, 7
if (FailsafeCount > FailsafeLimit)
{
	tooltip, , , , 7
	FailsafeTriggered := true
	settimer, FailsafeCounter, off
}
return

InfiniteDomainExpansion:
IHateCountersCounterSECOND++
if (IHateCountersCounterSECOND >= 60)
{
	IHateCountersCounterSECOND := 0
	IHateCountersCounterMINUTE++
}
if (IHateCountersCounterMINUTE >= 60)
{
	IHateCountersCounterMINUTE := 0
	IHateCountersCounterHOUR++
}
if (AutoResetTimer > 0)
{
	if (IHateCountersCounterMINUTE >= ForTheEverLovingCOUNTERGOD)
	{
		ItsTimeToDOIT := true
		ForTheEverLovingCOUNTERGOD := ForTheEverLovingCOUNTERGOD + AutoResetTimer
	}
}
tooltip, Runtime: %IHateCountersCounterHOUR%h %IHateCountersCounterMINUTE%m %IHateCountersCounterSECOND%s, %TooltipX%, %Tooltip6%, 6
return