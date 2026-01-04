setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
SetTitleMatchMode 2

CoordMode, Tooltip, Screen
CoordMode, Pixel, Screen
CoordMode, Mouse, Screen

Loop, 0xFF
{
	Key := Format("VK{:02X}",A_Index)
	IF GetKeyState(Key)
		Send, {%Key% Up}
}

sleep 100
GoSub, ActivateRoblox
if !WinActive("Roblox")
	{
	msgbox, 0, No Roblox Instance Detected, Open Roblox First`n`nExiting Macro
	exitapp
	}

WinGetActiveStats, Title, WindowWidth, WindowHeight, WindowLeft, WindowTop
RobloxCenterX := WindowLeft+(WindowWidth/2)
RobloxCenterY := WindowTop+(WindowHeight/2)
PercentageScaling := Floor(100 * (A_ScreenDPI / 96))
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
;Tooltip, hello test, %TooltipX%, %Tooltip1%, 1

Gui, +toolwindow +resize -caption +alwaysontop -border
Gui, color, FFFFFF
Gui, Hide

filePath := "GeneralSettings.txt"
filePath2 := "MinigameSettings.txt"
if !FileExist("GeneralSettings.txt")
{
	GoSub, AutoSubscribe
	GoSub, DiscordWebhook
	GoSub, EquipRod
	GoSub, AutoLookDown
	GoSub, AutoZoomIn	
	GoSub, CompassDirection
	GoSub, AutoCameraMode
	GoSub, ChooseShakeMode
	GoSub, CastRod
	GoSub, Shake
	GoSub, MinigameBar
	GoSub, MinigameBarTolerance
	GoSub, CreateGeneralSettingsFile
}
if !FileExist("MinigameSettings.txt")
{
	GoSub, CreateThatDamnFile
}
GoSub, ExtractGeneralSettings
GoSub, ExtractMinigameSettings

PixelScaling := 1036/(BarRight-BarLeft)

MsgBox, 0, Fisch IRUS v3, Made By AsphaltCake, 1

GoSub, ActivateRoblox

tooltip, Runtime: 0h 0m 0s, TooltipX, Tooltip1, 1
tooltip, Made By AsphaltCake, TooltipX, Tooltip2, 2
tooltip, Press P to start, TooltipX, Tooltip4, 4
tooltip, Press O to reload, TooltipX, Tooltip5, 5
tooltip, Press M to exit, TooltipX, Tooltip6, 6

$m:: exitapp
$o:: reload

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

ActivateRoblox:
WinActivate, Roblox
DllCall("SetForegroundWindow", "uInt", mhwnd)
return

AutoSubscribe:
MsgBox, 1, First Time Setup, No configuration has been found`n`nOK = agree to auto subscribe`nCancel = exit
ifMsgBox Cancel
exitapp
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
GoSub, ActivateRoblox
return

DiscordWebhook:
InputBox, Webhook, Discord Webhook, % "Enter your discord webhook`n`nleave blank to disable", , , , RobloxCenterX, RobloxCenterY
if (Webhook != "")
{
	MsgBox, 4, Discord Webhook, Yes = Image Mode`nNo = Text Mode
	ifMsgBox No
	{
		WebhookMode := "Text"
	}
	else
	{
		WebhookMode := "Image"
	}
}
GoSub, ActivateRoblox
return

EquipRod:
GoSub, ActivateRoblox
send 2
sleep 250
send 1
sleep 500
return

AutoLookDown:
Gosub, ActivateRoblox
mousemove, RobloxCenterX, RobloxCenterY, 100
sleep 100
send {rbutton down}
sleep 750
mousemove, 0, 1000, 100, R
sleep 100
send {rbutton up}
sleep 100
mousemove, RobloxCenterX, RobloxCenterY, 100
MsgBox, 4, Auto Look Down, Did your camera look down?
ifMsgBox No
{
	AutoLookDown := 0
}
else
{
	AutoLookDown := 1
}
Gosub, ActivateRoblox
return

AutoZoomIn:
Gosub, ActivateRoblox
mousemove, RobloxCenterX, RobloxCenterY, 100
loop 10
{
	send {wheelup}
	sleep 10
}
sleep 500
send {wheeldown}
MsgBox, 4, Auto Zoom In, Did your camera zoomed in to max,`nThen zoomed out by 1 scroll?
ifMsgBox No
{
	AutoZoomIn := 0
}
else
{
	AutoZoomIn := 1
}
Gosub, ActivateRoblox
return

CompassDirection:
Gosub, ActivateRoblox
ResizeOrangeScanArea:
Gui, Show
TemporaryLeft := WindowLeft+(WindowWidth/2.15)
TemporaryTop := WindowTop+(WindowHeight/70)
TemporaryLength := (WindowLeft+(WindowWidth/1.8686))-TemporaryLeft
TemporaryWidth := (WindowTop+(WindowHeight/20))-TemporaryTop
WinMove, ahk_class AutoHotkeyGUI, , TemporaryLeft, TemporaryTop, TemporaryLength, TemporaryWidth
Gui, +LastFound
WinSet, Transparent, 100
SetTimer, UpdateTooltips, 10
OnMessage(0x201, "WM_LBUTTONDOWN")
MsgBox, 0, Compass Scan Area, Set the white square to cover the compass at the top
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
GoSub, ActivateRoblox
AllowedLeftCompass := (WindowLeft+(WindowWidth/2))-(WindowWidth/250)
AllowedRightCompass := (WindowLeft+(WindowWidth/2))+(WindowWidth/250)
send {left up}
send {right up}
mynukercounter := 0
RealignNorth:
PixelSearch, OrangeX, , OrangeLeft, OrangeTop, OrangeRight, OrangeBottom, 0x76B8E7, 10, Fast
if (ErrorLevel == 0)
{
	if (OrangeX < AllowedLeftCompass)
	{
		send {right up}
		getkeystate, state, left
		if (state = "U")
		{
			send {left down}
		}
		goto RealignNorth
	}
	else if (OrangeX > AllowedRightCompass)
	{
		send {left up}
		getkeystate, state, right
		if (state = "U")
		{
			send {right down}
		}
		goto RealignNorth
	}
	else
	{
		send {left up}
		send {right up}
	}
}
else
{
	mynukercounter++
	if (mynukercounter < 1000)
	{
		getkeystate, state, right
		if (state = "U")
		{
			send {right down}
		}
		goto RealignNorth
		sleep 10	
	}
	else
	{
		msgbox, can u like.. disable ur camera mode
		send {left up}		
		send {right up}
		GoSub, ActivateRoblox
		mynukercounter := 0
		goto RealignNorth
	}
}

MsgBox, 4, Anti Nuke, Did you face north?
ifMsgBox No
{
	AntiNuke := 0
}
else
{
	AntiNuke := 1
}
mousemove, RobloxCenterX, RobloxCenterY, 100
sleep 250
send {wheelup}
sleep 250
send {wheeldown}
sleep 500
return

AutoCameraMode:
Gui, Show
TemporaryLeft := WindowLeft+(WindowWidth/2.15)
TemporaryTop := WindowTop+(WindowHeight/1.1)
TemporaryLength := (WindowLeft+(WindowWidth/1.85))-TemporaryLeft
TemporaryWidth := (WindowTop+(WindowHeight/1.05))-TemporaryTop
WinMove, ahk_class AutoHotkeyGUI, , TemporaryLeft, TemporaryTop, TemporaryLength, TemporaryWidth
Gui, +LastFound
WinSet, Transparent, 100
SetTimer, UpdateTooltips, 10
OnMessage(0x201, "WM_LBUTTONDOWN")
MsgBox, 0, Auto Camera Mode, Drag the box over the "open backpack" text at the bottom
GoSub, ActivateRoblox
SetTimer, UpdateTooltips, off
BackpackLeft := Left
BackpackRight := Right
BackpackTop := Top
BackpackBottom := Bottom
ToolTip, , , , 17
ToolTip, , , , 18
ToolTip, , , , 19
ToolTip, , , , 20
Gui, Hide

BackpackTolerance := 0
GoSub, ActivateRoblox
RedoBlablablapoint:
PixelSearch, , , BackpackLeft, BackpackTop, BackpackRight, BackpackBottom, 0xFFFFFF, %BackpackTolerance%, Fast
if (ErrorLevel == 1)
{
	BackpackTolerance++
	if (BackpackTolerance > 20)
	{
		msgbox, MAKE SURE UR CAMERA MODE IS DISABLED`n(u need to see the text "open backpack")
		goto AutoCameraMode
	}
	goto RedoBlablablapoint
}

Tooltip, Right Click The Camera Icon`nRight Click The Camera Icon`nRight Click The Camera Icon`nRight Click The Camera Icon`nRight Click The Camera Icon`nRight Click The Camera Icon`nRight Click The Camera Icon`nRight Click The Camera Icon`nRight Click The Camera Icon`nRight Click The Camera Icon`n, RobloxCenterX, RobloxCenterY
keywait, rbutton, D
mousegetpos, CameraX, CameraY
tooltip
GoSub, ActivateRoblox
click %CameraX% %CameraY%
MsgBox, 4, Auto Camera Mode, Did your camera mode turn on?
ifMsgBox No
{
	AutoCameraMode := 0
}
else
{
	AutoCameraMode := 1
}

PixelSearch, , , BackpackLeft, BackpackTop, BackpackRight, BackpackBottom, 0xFFFFFF, %BackpackTolerance%, Fast
if (ErrorLevel == 0)
{
	GoSub, ActivateRoblox
	click %CameraX% %CameraY%
}
return

ChooseShakeMode:
MsgBox, 4, Shake Mode, Yes = Click Shake Mode`nNo = Navigation Shake Mode
ifMsgBox No
{
	ShakeMode := "Navigation"
	GoSub, NavigationStuff
}
else
{
	ShakeMode := "Click"
	GoSub, ClickStuff
}
return

NavigationStuff:
GoSub, ActivateRoblox
InputBox, NavigationKey, Navigation Key, % "Input your navigation key`nIf its #, type in ~ into the box instead", , , , RobloxCenterX, RobloxCenterY
GoSub, ActivateRoblox
loop, 4
{
send %NavigationKey%
sleep 100
}
MsgBox, 4, Navigation Mode, Did your navigation mode enable?
ifMsgBox No
{
	goto NavigationStuff
}
return

ClickStuff:
GoSub, ActivateRoblox
Gui, Show
TemporaryLeft := WindowLeft+(WindowWidth/4.65)
TemporaryTop := WindowTop+(WindowHeight/17.6)
TemporaryLength := (WindowLeft+(WindowWidth/1.27))-TemporaryLeft
TemporaryWidth := (WindowTop+(WindowHeight/1.15))-TemporaryTop
WinMove, ahk_class AutoHotkeyGUI, , TemporaryLeft, TemporaryTop, TemporaryLength, TemporaryWidth
Gui, +LastFound
WinSet, Transparent, 100
SetTimer, UpdateTooltips, 10
OnMessage(0x201, "WM_LBUTTONDOWN")
MsgBox, 4096, Click Shake Setup, Drag the box to cover WHEREVER the "shake" button could appear
GoSub, ActivateRoblox
SetTimer, UpdateTooltips, off
ClickShakeLeft := Left
ClickShakeRight := Right
ClickShakeTop := Top
ClickShakeBottom := Bottom
ToolTip, , , , 17
ToolTip, , , , 18
ToolTip, , , , 19
ToolTip, , , , 20
Gui, Hide
return

CastRod:
mousemove, RobloxCenterX, RobloxCenterY, 100
send {lbutton down}
sleep 1000
send {lbutton up}
sleep 1000
return

Shake:
GoSub, ActivateRoblox
msgbox, Click Ok once "Shake" appears on the screen
GoSub, ActivateRoblox
sleep 500
if (ShakeMode == "Navigation")
{
	send %NavigationKey%
	settimer, SpamNavigationShake, 1000
}
else
{
	ShakeWhiteTolerance := 0
	PixelSearch, , , ClickShakeLeft, ClickShakeTop, ClickShakeRight, ClickShakeBottom, 0xFFFFFF, %ShakeWhiteTolerance%, Fast
	if (ErrorLevel == 1)
	{
		ShakeWhiteTolerance++
		if (ShakeWhiteTolerance > 10)
		{
			goto Shake
		}
	}
	settimer, SpamClickShake, 1000
}
Tooltip, Right Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`n, TooltipX, Tooltip1
keywait, rbutton, D
tooltip
settimer, SpamNavigationShake, off
settimer, SpamClickShake, off
return

SpamNavigationShake:
send s
sleep 500
send {enter}
return

SpamClickShake:
PixelSearch, ShakeX, ShakeY, ClickShakeLeft, ClickShakeTop, ClickShakeRight, ClickShakeBottom, 0xFFFFFF, %ShakeWhiteTolerance%, Fast
click %ShakeX% %ShakeY%
return

MinigameBar:
GoSub, ActivateRoblox
Gui, Show
TemporaryLeft := WindowLeft+(WindowWidth/3.3464)
TemporaryTop := WindowTop+(WindowHeight/1.1942)
TemporaryLength := (WindowLeft+(WindowWidth/1.4261))-TemporaryLeft
TemporaryWidth := (WindowTop+(WindowHeight/1.14))-TemporaryTop
WinMove, ahk_class AutoHotkeyGUI, , TemporaryLeft, TemporaryTop, TemporaryLength, TemporaryWidth
Gui, +LastFound
WinSet, Transparent, 100
SetTimer, UpdateTooltips, 10
OnMessage(0x201, "WM_LBUTTONDOWN")
afadadsasd:
MsgBox, 4, Bar Minigame, Drag the box over the bar minigame like in the youtube tutorial`n`nYes = continue`nNo = the minigame bar went away
GoSub, ActivateRoblox
ifMsgBox No
{
	GoSub, CastRod
	if (ShakeMode == "Navigation")
	{
		send %NavigationKey%
		settimer, SpamNavigationShake, 1000
	}
	else
	{
		settimer, SpamClickShake, 1000
	}
	Tooltip, Right Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`n, TooltipX, Tooltip1
	keywait, rbutton, D
	tooltip
	settimer, SpamNavigationShake, off
	settimer, SpamClickShake, off
	goto afadadsasd
}
GoSub, ActivateRoblox
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
return

MinigameBarTolerance:
msgbox, Click Ok once the minigame ends
sleep 1000
GoSub, ActivateRoblox
GoSub, CastRod
if (ShakeMode == "Navigation")
{
	send %NavigationKey%
	settimer, SpamNavigationShake, 1000
}
else
{
	settimer, SpamClickShake, 1000
}
Tooltip, Right Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`nRight Click When Minigame Starts`n, TooltipX, Tooltip1
keywait, rbutton, D
tooltip
settimer, SpamNavigationShake, off
settimer, SpamClickShake, off
FishBlueTolerance := 0
adwdawdawvxzxz:
PixelSearch, , , BarLeft, BarTop, BarRight, BarBottom, 0x5B4B43, %FishBlueTolerance%, Fast
if (ErrorLevel == 1)
{
	FishBlueTolerance++
	goto adwdawdawvxzxz
}
ArrowTolerance := 0
awddawasdasd:
PixelSearch, , , BarLeft, BarTop, BarRight, BarBottom, 0x878584, %ArrowTolerance%, Fast
if (ErrorLevel == 1)
{
	ArrowTolerance++
	goto adwdawdawvxzxz
}
return

CreateGeneralSettingsFile:
FileAppend,
(
Webhook=%Webhook%
WebhookMode=%WebhookMode%
EveryHowManyReelsForImage=10

ConsecutiveFAILUREStoshutdown=5
FailProcedure=Shutdown

AutoLookDown=%AutoLookDown%
AutoZoomIn=%AutoZoomIn%
AutoCameraMode=%AutoCameraMode%

BackpackTolerance=%BackpackTolerance%
ShakeWhiteTolerance=%ShakeWhiteTolerance%
BarWhiteTolerance=15
FishBlueTolerance=%FishBlueTolerance%
ArrowTolerance=%ArrowTolerance%

ShakeMode=%ShakeMode%
MinimumClickDelay=150
NavigationDelay=25
NavigationKey=%NavigationKey%
ShakeFailsafeSeconds=20

AntiNuke=%AntiNuke%
TurnLeft=0
TurnRight=0

HoldRodCastDelay=1000
WaitForBobberDelay=1000
EndMinigameDelay=1500

OrangeLeft=%OrangeLeft%
OrangeRight=%OrangeRight%
OrangeTop=%OrangeTop%
OrangeBottom=%OrangeBottom%
BackpackLeft=%BackpackLeft%
BackpackRight=%BackpackRight%
BackpackTop=%BackpackTop%
BackpackBottom=%BackpackBottom%
ClickShakeLeft=%ClickShakeLeft%
ClickShakeRight=%ClickShakeRight%
ClickShakeTop=%ClickShakeTop%
ClickShakeBottom=%ClickShakeBottom%
BarLeft=%BarLeft%
BarRight=%BarRight%
BarTop=%BarTop%
BarBottom=%BarBottom%
CameraX=%CameraX%
CameraY=%CameraY%
), % filePath
return

CreateThatDamnFile:
FileAppend,
(
ScanDelay=100
TriggerSideBarRatio=0.6
ReleaseSideBarRatio=0.9

LeftStrength=2.7
LeftDivision=1
LeftStabilizerLoops=10

RightStrength=2.7
RightDivision=1.1
RightStabilizerLoops=0
), % filePath2
return

ExtractGeneralSettings:
FileRead, ConfigData, %filePath%
Loop, parse, ConfigData, `n, `r
{
    if (A_LoopField = "")
        continue
    StringSplit, Parts, A_LoopField, =
    if (Parts0 >= 2)
    {
        varName := Parts1
        varValue := Parts2
        %varName% := varValue
    }
}
return

ExtractMinigameSettings:
FileRead, ConfigData2, %filePath2%
Loop, parse, ConfigData2, `n, `r
{
    if (A_LoopField = "")
        continue
    StringSplit, Parts, A_LoopField, =
    if (Parts0 >= 2)
    {
        varName := Parts1
        varValue := Parts2
        %varName% := varValue
    }
}
return

$p::
onetimeonlytrigger := 1
tooltip, Press O to reload, TooltipX, Tooltip4, 4
tooltip, Press M to exit, TooltipX, Tooltip5, 5
tooltip, , , , 6
if (Webhook != "")
{
	FormatTime, CurrentTime, %A_Now%, dddd hh:mm tt
	message := CurrentTime "   Starting Macro"
	HTTP := ComObjCreate("WinHttp.WinHttpRequest.5.1")
	HTTP.Open("POST", Webhook, false)
	HTTP.SetRequestHeader("Content-Type", "application/json")
	HTTP.Send("{""content"": """ message """}")		
}
AntiNukeReset := 1
GoSub, ActivateRoblox
RuntimeS := 0
RuntimeM := 0
RuntimeH := 0
settimer, Runtime, 1000
herawdawdadawdwa:
if (AutoLookDown == 1)
{
	GoSub, LegitAutoLookDown
}
if (AutoZoomIn == 1)
{
	GoSub, LegitAutoZoomIn
}
if (AntiNuke == 1)
{
	GoSub, LegitAntiNuke
}
if (AutoCameraMode == 1)
{
	GoSub, LegitAutoCameraMode
}
haharedoLOSER:
if (ultimatefailshutdown >= ConsecutiveFAILUREStoshutdown)
{
	if (AntiNuke == 1 and onetimeonlytrigger == 1)
	{
		onetimeonlytrigger := 0
		ultimatefailshutdown := 0
		GoSub, LegitAntiNuke
		if (Webhook != "")
		{
			FormatTime, CurrentTime, %A_Now%, dddd hh:mm tt
			message := CurrentTime "   " ConsecutiveFAILUREStoshutdown " Consecutive Failures, Attempting Anti Nuke"
			HTTP := ComObjCreate("WinHttp.WinHttpRequest.5.1")
			HTTP.Open("POST", Webhook, false)
			HTTP.SetRequestHeader("Content-Type", "application/json")
			HTTP.Send("{""content"": """ message """}")
		}
		goto herawdawdadawdwa
	}
	if (Webhook != "")
	{
		FormatTime, CurrentTime, %A_Now%, dddd hh:mm tt
		message := CurrentTime "   " ConsecutiveFAILUREStoshutdown " Consecutive Failures, Shutting Down"
		HTTP := ComObjCreate("WinHttp.WinHttpRequest.5.1")
		HTTP.Open("POST", Webhook, false)
		HTTP.SetRequestHeader("Content-Type", "application/json")
		HTTP.Send("{""content"": """ message """}")
	}
	if (FailProcedure == "Shutdown")
	{
		shutdown, 8
	}
	else
	{
		exitapp
	}
}
GoSub, LegitCastRod
if (ShakeMode == "Click")
{
	GoSub, LegitClickShake
}
else
{
	GoSub, LegitNavigationShake
}
tooltip, , , , 6
if (uFIALEDDD == true)
{
	if (Webhook != "")
	{
		FormatTime, CurrentTime, %A_Now%, dddd hh:mm tt
		message := CurrentTime "   Failsafe Triggered (" ShakeMode ")"
		HTTP := ComObjCreate("WinHttp.WinHttpRequest.5.1")
		HTTP.Open("POST", Webhook, false)
		HTTP.SetRequestHeader("Content-Type", "application/json")
		HTTP.Send("{""content"": """ message """}")		
	}
	ultimatefailshutdown++
	if (AutoLookDown == 1)
	{
		GoSub, LegitAutoLookDown
	}
	goto haharedoLOSER
}
GoSub, TimeTODUDUDUDUDUDUELLLLLLLLLLLL
if (AutoLookDown == 1)
{
	GoSub, LegitAutoLookDown
}
if (Webhook != "")
{
	if (WebhookMode == "Image")
	{
		GoSub, DiscordImageShit
	}
	else if (WebhookMode == "Text")
	{
		GoSub, DiscordTextShit
	}
}
ultimatefailshutdown := 0
onetimeonlytrigger := 1
goto haharedoLOSER
return

Runtime:
RuntimeS++
if (RuntimeS >= 60)
{
	RuntimeS := 0
	RuntimeM++
}
if (RuntimeM >= 60)
{
	RuntimeM := 0
	RuntimeH++
}
tooltip, Runtime: %RuntimeH%h %RuntimeM%m %RuntimeS%s, %TooltipX%, %Tooltip1%, 1
return

LegitAutoLookDown:
Gosub, ActivateRoblox
mousemove, RobloxCenterX, RobloxCenterY, 100
sleep 100
send {rbutton down}
sleep 750
mousemove, 0, 1000, 100, R
sleep 100
send {rbutton up}
sleep 100
return

LegitAutoZoomIn:
Gosub, ActivateRoblox
mousemove, RobloxCenterX, RobloxCenterY, 100
loop 10
{
	send {wheelup}
	sleep 10
}
sleep 500
send {wheeldown}
sleep 500
return

LegitAntiNuke:
Gosub, ActivateRoblox
if (AutoCameraMode == 1)
{
	PixelSearch, , , BackpackLeft, BackpackTop, BackpackRight, BackpackBottom, 0xFFFFFF, %BackpackTolerance%, Fast
	if (ErrorLevel == 1)
	{
		sleep 250
		click %CameraX% %CameraY%
		sleep 250
	}
}
mynukercounter := 0
AllowedLeftCompass := (WindowLeft+(WindowWidth/2))-(WindowWidth/250)
AllowedRightCompass := (WindowLeft+(WindowWidth/2))+(WindowWidth/250)
send {left up}
send {right up}
RealignNorth123:
PixelSearch, OrangeX, , OrangeLeft, OrangeTop, OrangeRight, OrangeBottom, 0x76B8E7, 10, Fast
if (ErrorLevel == 0)
{
	if (OrangeX < AllowedLeftCompass)
	{
		send {right up}
		getkeystate, state, left
		if (state = "U")
		{
			send {left down}
		}
		goto RealignNorth123
	}
	else if (OrangeX > AllowedRightCompass)
	{
		send {left up}
		getkeystate, state, right
		if (state = "U")
		{
			send {right down}
		}
		goto RealignNorth123
	}
	else
	{
		send {left up}
		send {right up}
	}
}
else
{
	mynukercounter++
	if (mynukercounter < 1000)
	{
	getkeystate, state, right
	if (state = "U")
	{
		send {right down}
	}
	goto RealignNorth123
	sleep 10	
	}
	else
	{
		if (Webhook != "")
		{
			FormatTime, CurrentTime, %A_Now%, dddd hh:mm tt
			message := CurrentTime "   Failed To AntiNuke, Shutting Down"
			HTTP := ComObjCreate("WinHttp.WinHttpRequest.5.1")
			HTTP.Open("POST", Webhook, false)
			HTTP.SetRequestHeader("Content-Type", "application/json")
			HTTP.Send("{""content"": """ message """}")
		}
		if (FailProcedure == "Shutdown")
		{
			shutdown, 8
		}
		else
		{
			exitapp
		}
	}
}
mousemove, RobloxCenterX, RobloxCenterY, 100
if (TurnLeft != 0 or TurnRight != 0)
{
	if (TurnLeft > TurnRight)
	{
		send {left down}
		sleep %TurnLeft%
		send {left up}
	}
	else
	{
		send {right down}
		sleep %TurnRight%
		send {right up}
	}
}
send 2
sleep 250
send 1
sleep 250
send {wheelup}
sleep 250
send {wheeldown}
sleep 500
return

LegitAutoCameraMode:
Gosub, ActivateRoblox
PixelSearch, , , BackpackLeft, BackpackTop, BackpackRight, BackpackBottom, 0xFFFFFF, %BackpackTolerance%, Fast
if (ErrorLevel == 0)
{
	sleep 250
	click %CameraX% %CameraY%
	sleep 250
}
return

LegitReverseAutoCameraMode:
Gosub, ActivateRoblox
PixelSearch, , , BackpackLeft, BackpackTop, BackpackRight, BackpackBottom, 0xFFFFFF, %BackpackTolerance%, Fast
if (ErrorLevel == 1)
{
	sleep 250
	click %CameraX% %CameraY%
	sleep 250
}
return

LegitCastRod:
mousemove, RobloxCenterX, RobloxCenterY, 100
send {lbutton down}
sleep %HoldRodCastDelay%
send {lbutton up}
sleep %WaitForBobberDelay%
return

LegitClickShake:
wowowowo := 0
uFIALEDDD := false
settimer, MyAlluhakbar, 1000
DynamicShakeDelay := MinimumClickDelay
ClickCountThingy := 0
awddwaghfd:
if (uFIALEDDD == true)
return
PixelSearch, , , BarLeft, BarTop, BarRight, BarBottom, 0x5B4B43, %FishBlueTolerance%, Fast
if (ErrorLevel == 1)
{
	PixelSearch, ClickShakeX, ClickShakeY, ClickShakeLeft, ClickShakeTop, ClickShakeRight, ClickShakeBottom, 0xFFFFFF, %ShakeWhiteTolerance%, Fast
	if (ErrorLevel == 0)
	{
		if (ClickShakeX != MemoryX and ClickShakeY != MemoryY)
		{
			ClickCountThingy := 0
			click %ClickShakeX% %ClickShakeY%
			MemoryX := ClickShakeX
			MemoryY := ClickShakeY
			sleep %DynamicShakeDelay%
			goto awddwaghfd
		}
		else
		{
			ClickCountThingy++
			if (ClickCountThingy >= 3)
			{
				ClickCountThingy := 0
				DynamicShakeDelay := MinimumClickDelay
				MemoryX := 0
				MemoryY := 0
				goto awddwaghfd
			}
			sleep %DynamicShakeDelay%
			DynamicShakeDelay := DynamicShakeDelay + 10
			goto awddwaghfd
		}
	}
	else
	{
		sleep %DynamicShakeDelay%
		goto awddwaghfd
	}
}
settimer, MyAlluhakbar, off
return

LegitNavigationShake:
wowowowo := 0
uFIALEDDD := false
settimer, MyAlluhakbar, 1000
send %NavigationKey%
sleep 500
ahahwdawd:
if (uFIALEDDD == true)
return
PixelSearch, , , BarLeft, BarTop, BarRight, BarBottom, 0x5B4B43, %FishBlueTolerance%, Fast
if (ErrorLevel == 1)
{
	send s
	sleep %NavigationDelay%
	send {enter}
	sleep %NavigationDelay%
	goto ahahwdawd
}
settimer, MyAlluhakbar, off
return

MyAlluhakbar:
wowowowo++
tooltip, Failsafe: %wowowowo%/%ShakeFailsafeSeconds%, TooltipX, Tooltip6, 6
if (wowowowo >= ShakeFailsafeSeconds)
{
	settimer, MyAlluhakbar, off
	uFIALEDDD := true
}
return

TimeTODUDUDUDUDUDUELLLLLLLLLLLL:
FishBarTooltipHeight := BarBottom+DynamicTooltip
sleep 100
PixelSearch, BarX1, , BarLeft, BarTop, BarRight, BarBottom, 0xFFFFFF, %BarWhiteTolerance%, Fast
PixelSearch, BarX2, , BarRight, BarTop, BarLeft, BarBottom, 0xFFFFFF, %BarWhiteTolerance%, Fast

FullBarSize := BarX2-BarX1
HalfBarSize := FullBarSize/2
TriggerMaxLeft := BarLeft+(FullBarSize*TriggerSideBarRatio)
TriggerMaxRight := BarRight-(FullBarSize*TriggerSideBarRatio)
ReleaseMaxLeft := BarLeft+(FullBarSize*ReleaseSideBarRatio)
ReleaseMaxRight := BarRight-(FullBarSize*ReleaseSideBarRatio)

goonnig123123 := false

settimer, daw8u9yudnawi, %ScanDelay%
dqweqweqwe:
if (Mode == 1)
{
	Temporary := PixelDifference*PixelScaling*RightStrength
	send {lbutton down}
	sleep %Temporary%
	Temporary2 := Temporary/RightDivision
	send {lbutton up}
	sleep %Temporary2%
	loop, %RightStabilizerLoops%
	{
	send {lbutton down}
	send {lbutton up}
	}
}
else if (Mode == 2)
{
	Temporary := PixelDifference*PixelScaling*LeftStrength
	send {lbutton up}
	sleep %Temporary%
	Temporary2 := Temporary/LeftDivision
	send {lbutton down}
	sleep %Temporary2%
	loop, %LeftStabilizerLoops%
	{
	send {lbutton down}
	send {lbutton up}
	}
}
else if (Mode == 3)
{
	getkeystate, state, lbutton
	if (state == "U")
	{
		sleep 100
		send {lbutton down}
	}
	sleep %ScanDelay%
}
else if (Mode == 4)
{
	getkeystate, state, lbutton
	if (state != "U")
	{
		sleep 100
		send {lbutton up}
	}
	sleep %ScanDelay%
}
if (goonnig123123 == false)
{
goto dqweqweqwe
}
sleep %EndMinigameDelay%
return

daw8u9yudnawi:
PixelSearch, FishX, , BarLeft, BarTop, BarRight, BarBottom, 0x5B4B43, %FishBlueTolerance%, Fast
if (ErrorLevel == 0)
{
	
	tooltip, |, %FishX%, %FishBarTooltipHeight%, 20
	if (TriggerPointHit == true)
	{
		if (FishX > ReleaseMaxLeft and FishX < ReleaseMaxRight)
		{
		TriggerPointHit := false
		}
	}
	else if (FishX > TriggerMaxRight)
	{
		tooltip, >, %ReleaseMaxRight%, %FishBarTooltipHeight%, 19
		Mode := 3
		PixelDifference := 0
		TriggerPointHit := true
	}
	else if (FishX < TriggerMaxLeft)
	{
		tooltip, <, %ReleaseMaxLeft%, %FishBarTooltipHeight%, 19
		Mode := 4
		PixelDifference := 0
		TriggerPointHit := true
	}
	else
	{
		PixelSearch, BarX, , BarLeft, BarTop, BarRight, BarBottom, 0xFFFFFF, %BarWhiteTolerance%, Fast
		if (ErrorLevel == 0)
		{
			BarX := BarX+HalfBarSize
			helladdaw := FishX-BarX
			if (helladdaw > 0)
			{
				PixelDifference := helladdaw
				tooltip, >, %BarX%, %FishBarTooltipHeight%, 19
				Mode := 1
			}
			else
			{
				PixelDifference := Abs(helladdaw)
				tooltip, <, %BarX%, %FishBarTooltipHeight%, 19
				Mode := 2
			}
		}
		else
		{
			PixelSearch, ArrowX, , BarLeft, BarTop, BarRight, BarBottom, 0x878584, %ArrowTolerance%, Fast
			if (ErrorLevel == 0)
			{
				if ((FishX-ArrowX) > 0)
				{
					BarX := FishX-HalfBarSize
					PixelDifference := HalfBarSize
					tooltip, >, %BarX%, %FishBarTooltipHeight%, 19
					Mode := 1
				}
				else
				{
					BarX := FishX+HalfBarSize
					PixelDifference := HalfBarSize
					tooltip, <, %BarX%, %FishBarTooltipHeight%, 19
					Mode := 2
				}
			}
			else
			{
				tooltip, , , , 19
			}
		}
	}
}
else
{
	tooltip, , , , 18
	tooltip, , , , 19
	tooltip, , , , 20
	goonnig123123 := true
	settimer, daw8u9yudnawi, off	
}
return

DiscordImageShit:
UniversalFishCountasdasdasd++
if (Mod(UniversalFishCountasdasdasd, EveryHowManyReelsForImage) != 0 and UniversalFishCountasdasdasd != 1)
{
FormatTime, CurrentTime, %A_Now%, dddd hh:mm tt
message := CurrentTime "   Fish Reeled: " UniversalFishCountasdasdasd
HTTP := ComObjCreate("WinHttp.WinHttpRequest.5.1")
HTTP.Open("POST", Webhook, false)
HTTP.SetRequestHeader("Content-Type", "application/json")
HTTP.Send("{""content"": """ message """}")
return
}
if (AutoCameraMode == 1)
{
	PixelSearch, , , BackpackLeft, BackpackTop, BackpackRight, BackpackBottom, 0xFFFFFF, %BackpackTolerance%, Fast
	if (ErrorLevel == 1)
	{
		sleep 100
		click %CameraX% %CameraY%
		sleep 100
	}
}
FormatTime, CurrentTime, %A_Now%, dddd hh:mm tt
MessageSent := CurrentTime "   Fish Reeled: " UniversalFishCountasdasdasd
EnvGet, username, USERNAME
PictureFileLoc2 := "C:\Users\" username "\Pictures\Roblox"
IfNotExist, %PictureFileLoc2%
{
    PictureFileLoc2 := "C:\Users\" username "\OneDrive\Pictures\Roblox"
}
send ^{Printscreen}
sleep 1500
   Loop %PictureFileLoc2%\*.*            
   If ( A_LoopFileTimeModified >= Time2 )
     Time2 := A_LoopFileTimeModified, File2 := A_LoopFileLongPath
	var203 := [ File2 ]
SendLatestScreenshotToWeb:
objParam := {file: var203, content: MessageSent}
CreateFormData(PostData, hdr_ContentType, objParam)
HTTP := ComObjCreate("WinHTTP.WinHTTPRequest.5.1")
HTTP.Open("POST", Webhook, true)
HTTP.SetRequestHeader("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
HTTP.SetRequestHeader("Content-Type", hdr_ContentType)
HTTP.SetRequestHeader("Pragma", "no-cache")
HTTP.SetRequestHeader("Cache-Control", "no-cache, no-store")
HTTP.SetRequestHeader("If-Modified-Since", "Sat, 1 Jan 2015 00:00:00 GMT")
HTTP.Send(PostData)
HTTP.WaitForResponse()
statuscode := HTTP.status
if (HTTP.status = 200)
{
filedelete, %File2%
}
if (HTTP.status = 404)
{
filedelete, %File2%
}
CreateFormData(ByRef retData, ByRef retHeader, objParam) {
	New CreateFormData(retData, retHeader, objParam)
}
Class CreateFormData {
	__New(ByRef retData, ByRef retHeader, objParam) {
		Local CRLF := "`r`n", i, k, v, str, pvData
		Local Boundary := this.RandomBoundary()
		Local BoundaryLine := "------------------------------" . Boundary
		this.Len := 0
		this.Ptr := DllCall( "GlobalAlloc", "UInt",0x40, "UInt",1, "Ptr" )
		For k, v in objParam
		{
			If IsObject(v) {
				For i, FileName in v
				{
					str := BoundaryLine . CRLF
					     . "Content-Disposition: form-data; name=""" . k . """; filename=""" . FileName . """" . CRLF
					     . "Content-Type: " . this.MimeType(FileName) . CRLF . CRLF
          this.StrPutUTF8( str )
          this.LoadFromFile( Filename )
          this.StrPutUTF8( CRLF )
				}
			} Else {
				str := BoundaryLine . CRLF
				     . "Content-Disposition: form-data; name=""" . k """" . CRLF . CRLF
				     . v . CRLF
        this.StrPutUTF8( str )
			}
		}
		this.StrPutUTF8( BoundaryLine . "--" . CRLF )
		retData := ComObjArray( 0x11, this.Len )
		pvData  := NumGet( ComObjValue( retData ) + 8 + A_PtrSize )
		DllCall( "RtlMoveMemory", "Ptr",pvData, "Ptr",this.Ptr, "Ptr",this.Len )
		this.Ptr := DllCall( "GlobalFree", "Ptr",this.Ptr, "Ptr" )
		retHeader := "multipart/form-data; boundary=----------------------------" . Boundary
	}
  StrPutUTF8( str ) {
    Local ReqSz := StrPut( str, "utf-8" ) - 1
    this.Len += ReqSz
    this.Ptr := DllCall( "GlobalReAlloc", "Ptr",this.Ptr, "UInt",this.len + 1, "UInt", 0x42 )   
    StrPut( str, this.Ptr + this.len - ReqSz, ReqSz, "utf-8" )
  }
  LoadFromFile( Filename ) {
    Local objFile := FileOpen( FileName, "r" )
    this.Len += objFile.Length
    this.Ptr := DllCall( "GlobalReAlloc", "Ptr",this.Ptr, "UInt",this.len, "UInt", 0x42 )
    objFile.RawRead( this.Ptr + this.Len - objFile.length, objFile.length )
    objFile.Close()       
  }
	RandomBoundary() {
		str := "0|1|2|3|4|5|6|7|8|9|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z"
		Sort, str, D| Random
		str := StrReplace(str, "|")
		Return SubStr(str, 1, 12)
	}
	MimeType(FileName) {
		n := FileOpen(FileName, "r").ReadUInt()
		Return (n = 0x474E5089) ? "image/png"
		     : (n = 0x38464947) ? "image/gif"
		     : (n&0xFFFF = 0x4D42    ) ? "image/bmp"
		     : (n&0xFFFF = 0xD8FF    ) ? "image/jpeg"
		     : (n&0xFFFF = 0x4949    ) ? "image/tiff"
		     : (n&0xFFFF = 0x4D4D    ) ? "image/tiff"
		     : "application/octet-stream"
	}
}
if (AutoCameraMode == 1)
{
	PixelSearch, , , BackpackLeft, BackpackTop, BackpackRight, BackpackBottom, 0xFFFFFF, %BackpackTolerance%, Fast
	if (ErrorLevel == 0)
	{
		sleep 100
		click %CameraX% %CameraY%
		sleep 100
	}
}
return

DiscordTextShit:
UniversalFishCountasdasdasd++
FormatTime, CurrentTime, %A_Now%, dddd hh:mm tt
message := CurrentTime "   Fish Reeled: " UniversalFishCountasdasdasd
HTTP := ComObjCreate("WinHttp.WinHttpRequest.5.1")
HTTP.Open("POST", Webhook, false)
HTTP.SetRequestHeader("Content-Type", "application/json")
HTTP.Send("{""content"": """ message """}")
return