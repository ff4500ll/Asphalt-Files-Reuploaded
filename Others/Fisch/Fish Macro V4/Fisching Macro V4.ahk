#ifWinActive, Roblox
setkeydelay, 0
setmousedelay, 0

;===============    Settings    ====================;

; how long to hold for when casting rod
HoldCastDuration := 500

; how long to wait after fish is caught or lost
RecastDelay := 2000

; increase for lower control rods (increments of 0.1 btw)
Strength := 1

; maximum difference allowed
DifferenceMax := 300

;===================================================;

; dont touch these
FishPixelRange := 0
ArrowPixelRange := 0
ScanDelay := 100
ArrowDelay := 20
RightBias := 100

; dont touch these
PositiveMovementMultiplier := 1.7
PositiveCounterMultiplier := 1
NegativeMovementMultiplier := 1.1
NegativeCounterMultiplier := 1

;===================================================;

EndShakeScanLeft := A_ScreenWidth/2.0078
EndShakeScanRight := A_ScreenWidth/1.9922
EndShakeScanTop := A_ScreenHeight/1.1842
EndShakeScanBottom := A_ScreenHeight/1.1501

FishScanLeft := A_ScreenWidth/3.3464
FishScanRight := A_ScreenWidth-FishScanLeft
FishScanTop := EndShakeScanTop
FishScanBottom := EndShakeScanBottom

Started = false
ImmediateStop = false
NavigationStatus = false
FishTrackHeight := A_ScreenHeight/1.0397
ResolutionScaling := 2560/A_ScreenWidth
InversedResolutionScaling := A_ScreenWidth/2560
DifferenceMax := DifferenceMax*InversedResolutionScaling
RightBias := RightBias*A_ScreenWidth/2560

tooltipMain := A_ScreenWidth/20
tooltip10 := A_ScreenHeight/2-(A_ScreenHeight/72*2)
tooltip1 := A_ScreenHeight/2
tooltip2 := A_ScreenHeight/2+(A_ScreenHeight/72)
tooltip3 := A_ScreenHeight/2+(A_ScreenHeight/72*2)
tooltip4 := A_ScreenHeight/2+(A_ScreenHeight/72*3)
tooltip5 := A_ScreenHeight/2+(A_ScreenHeight/72*4)
tooltip6 := A_ScreenHeight/2+(A_ScreenHeight/72*5)
tooltip7 := A_ScreenHeight/2+(A_ScreenHeight/72*6)
tooltip8 := A_ScreenHeight/2+(A_ScreenHeight/72*7)
tooltip9 := A_ScreenHeight/2+(A_ScreenHeight/72*8)

send {lbutton up}
send {\ up}
send {s up}
send {enter up}

tooltip, Made By AsphaltCake, tooltipMain, tooltip10, 10
tooltip, Press P to begin, tooltipMain, tooltip1, 1
tooltip, Turn off Navigation Mode, tooltipMain, tooltip3, 3
tooltip, Turn off Camera Mode, tooltipMain, tooltip4, 4
tooltip, Turn off "brightness" and "saturation" (in menu), tooltipMain, tooltip6, 6
tooltip, Turn off "see own nametag" (in menu), tooltipMain, tooltip7, 7
tooltip, Play in FULLSCREEN, tooltipMain, tooltip8, 8

send {lbutton up}

settimer, activescan, 100
activescan:
PixelSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, 0x5B4B43, %FishPixelRange%, Fast
if (ErrorLevel = 0)
	{
	tooltip, Illegal Pixel, %xxx%, %yyy%, 11
	}
else
	{
	tooltip, , , , 11
	}
return

$o::
if Started = false
reload
tooltip, RELOADING DONT PRESS ANYTHING, tooltipMain, tooltip1, 1
tooltip, RELOADING DONT PRESS ANYTHING, tooltipMain, tooltip2, 2
tooltip, RELOADING DONT PRESS ANYTHING, tooltipMain, tooltip3, 3
tooltip, RELOADING DONT PRESS ANYTHING, tooltipMain, tooltip4, 4
tooltip, RELOADING DONT PRESS ANYTHING, tooltipMain, tooltip5, 5
tooltip, RELOADING DONT PRESS ANYTHING, tooltipMain, tooltip6, 6
tooltip, RELOADING DONT PRESS ANYTHING, tooltipMain, tooltip7, 7
tooltip, RELOADING DONT PRESS ANYTHING, tooltipMain, tooltip8, 8
tooltip, RELOADING DONT PRESS ANYTHING, tooltipMain, tooltip9, 9
tooltip, Made By AsphaltCake, tooltipMain, tooltip10, 10
tooltip, , , , 19
tooltip, , , , 20
ImmediateStop = true
sleep 1
send {lbutton up}
sleep 1
send {left up}
sleep 1
send {right up}
sleep 1
send {\ up}
sleep 1
send {s up}
sleep 1
send {enter up}
sleep 1
if NavigationStatus = true
	{
	loop, 2
		{
		send {\ down}
		sleep 10
		send {\ up}
		sleep 100
		}
	loop 2,
		{
		send {right down}
		sleep 10
		send {right up}
		sleep 200
		}
	send {enter down}
	sleep 10
	send {enter up}
	sleep 500
	send {\ down}
	sleep 10
	send {\ up}
	sleep 100
	send {2 down}
	sleep 10
	send {2 up}
	sleep 100
	send {1 down}
	sleep 10
	send {1 up}
	}
else
	{
	send {\ down}
	sleep 10
	send {\ up}
	sleep 100
	loop 2,
		{
		send {right down}
		sleep 10
		send {right up}
		sleep 200
		}
	send {enter down}
	sleep 10
	send {enter up}
	sleep 500
	send {\ down}
	sleep 10
	send {\ up}
	sleep 100
	send {2 down}
	sleep 10
	send {2 up}
	sleep 100
	send {1 down}
	sleep 10
	send {1 up}
	}
reload
return

$p::

settimer, activescan, off
tooltip, Made By AsphaltCake, tooltipMain, tooltip10, 10
tooltip, Press O to reload, tooltipMain, tooltip1, 1
tooltip, Current Task: Idle, tooltipMain, tooltip3, 3
tooltip, Immediate Task: Idle, tooltipMain, tooltip4, 4
tooltip, , , , 5
tooltip, , , , 6
tooltip, , , , 7
tooltip, , , , 8
tooltip, , , , 9
tooltip, , , , 11

tooltip, Current Task: Setting Up Camera Mode, tooltipMain, tooltip3, 3
tooltip, Immediate Task: Selecting Bag, tooltipMain, tooltip4, 4
send {2 down}
sleep 10
send {2 up}
sleep 100
tooltip, Immediate Task: Selecting Rod, tooltipMain, tooltip4, 4
send {1 down}
sleep 10
send {1 up}
sleep 100
tooltip, Immediate Task: Enabling Nagivation Mode, tooltipMain, tooltip4, 4
send {\ down}
NavigationStatus = true
sleep 10
send {\ up}
sleep 100
tooltip, Immediate Task: Going To Camera, tooltipMain, tooltip4, 4
loop 3,
	{
	send {right down}
	sleep 10
	send {right up}
	sleep 200
	}
tooltip, Immediate Task: Enabling Camera Mode, tooltipMain, tooltip4, 4
send {enter down}
Started = true
sleep 10
send {enter up}
sleep 500
tooltip, Immediate Task: Going To Quest, tooltipMain, tooltip4, 4
loop 2,
	{
	send {left down}
	sleep 10
	send {left up}
	sleep 200
	}

Reset:
tooltip, Made By AsphaltCake, tooltipMain, tooltip10, 10
tooltip, Press O to reload, tooltipMain, tooltip1, 1
tooltip, Current Task: Idle, tooltipMain, tooltip3, 3
tooltip, Immediate Task: Idle, tooltipMain, tooltip4, 4
tooltip, , , , 5
tooltip, , , , 6
tooltip, , , , 7
tooltip, , , , 8
tooltip, , , , 9
if ImmediateStop = true
return

tooltip, Current Task: Casting Rod, tooltipMain, tooltip3, 3
tooltip, Immediate Task: Waiting For %HoldCastDuration%ms, tooltipMain, tooltip4, 4
send {lbutton down}
NavigationStatus = false
sleep %HoldCastDuration%
send {lbutton up}
sleep 10

tooltip, Immediate Task: Enabling Navigation Mode, tooltipMain, tooltip4, 4
send {\ down}
NavigationStatus = true
sleep 10
send {\ up}
sleep 100

count = 0
FishFound = false
tooltip, Current Task: Auto Shake, tooltipMain, tooltip3, 3
ShakeStart:
if ImmediateStop = true
return
count++
tooltip, Scanning: Times Scanned For Fish Bar: %count%, tooltipMain, tooltip6, 6
PixelSearch, xxx, yyy, EndShakeScanLeft, EndShakeScanTop, EndShakeScanRight, EndShakeScanBottom, 0x5B4B43, %FishPixelRange%, Fast
if (ErrorLevel = 0)
	{
	PixelSearch, xx, yy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %FishPixelRange%, Fast
		if (ErrorLevel = 0)
		{
		tooltip, Immediate Task: Calculating Offset, tooltipMain, tooltip4, 4
		Offset := xxx-xx
		tooltip, Scan Completed, tooltipMain, tooltip5, 5
		goto ShakeEnd
		}
		else
		{
		tooltip, Scanning: Waiting For Arrow To Render, tooltipMain, tooltip5, 5
		goto ShakeStart
		}
	}
tooltip, Immediate Task: Pressing S, tooltipMain, tooltip4, 4
send {s down}
sleep 10
send {s up}
sleep 10
tooltip, Immediate Task: Pressing Enter, tooltipMain, tooltip4, 4
send {enter down}
sleep 10
send {enter up}
sleep 10
goto ShakeStart
ShakeEnd:

tooltip, Immediate Task: Turning On Multi-Threaded Scanner, tooltipMain, tooltip4, 4
tooltip, , , , 5
tooltip, , , , 6
settimer, Scanner, %ScanDelay%

FishFound = false
toggle = false

count = 0
tooltip, Current Task: Auto Bar Balance, tooltipMain, tooltip3, 3
RightValue := (FishScanRight-Offset*2)
LeftValue := (FishScanLeft+Offset*2)
NavigationStatus = false

BarStart:
if ImmediateStop = true
return
if FishFound = true
goto BarEnd

sleep %ArrowDelay%
tooltip, Immediate Task: Searching For Bar Center, tooltipMain, tooltip4, 4
PixelSearch, xx, yy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %FishPixelRange%, Fast

Nigger := xx+Offset-RightBias
tooltip, White Bar: %Nigger%, tooltipMain, tooltip6, 6

tooltip, Immediate Task: Calculating Difference, tooltipMain, tooltip4, 4
Difference := xxx-Nigger
InversedDifference := Nigger-xxx

tooltip, Immediate Task: Check If Max Right, tooltipMain, tooltip4, 4
if (xxx > RightValue)
	{
	tooltip, >, %RightValue%, %FishTrackHeight%, 19
	tooltip, Immediate Task: Max Right, tooltipMain, tooltip4, 4
	if toggle = false
		{
		toggle = true
		send {lbutton down}
		sleep 10
		goto BarStart
		}
	goto BarStart
	}
toggle = false

tooltip, Immediate Task: Check If Max Left, tooltipMain, tooltip4, 4
if (xxx < LeftValue)
	{
	tooltip, <, %LeftValue%, %FishTrackHeight%, 19
	tooltip, Immediate Task: Max Left, tooltipMain, tooltip4, 4
	send {lbutton up}
	goto BarStart
	}

tooltip, Immediate Task: Checking Direction, tooltipMain, tooltip4, 4
if (Difference > 0)
	{
	if (Difference > DifferenceMax)
	Difference := DifferenceMax
	tooltip, Difference: %Difference%, tooltipMain, tooltip7, 7
	tooltip, >, %Nigger%, %FishTrackHeight%, 19
	send {lbutton down}
	Temporary := (Difference *PositiveMovementMultiplier *Strength *ResolutionScaling)
	tooltip, Immediate Task: Holding For %Temporary%ms, tooltipMain, tooltip4, 4
	sleep %Temporary%
	send {lbutton up}
	Temporary := (Difference *PositiveCounterMultiplier *Strength *ResolutionScaling)
	tooltip, Immediate Task: Releasing For %Temporary%ms, tooltipMain, tooltip4, 4
	sleep %Temporary%
	goto BarStart
	}
else
	{
	if (InversedDifference > DifferenceMax)
	InversedDifference := DifferenceMax
	tooltip, InversedDifference: %InversedDifference%, tooltipMain, tooltip7, 7
	tooltip, <, %Nigger%, %FishTrackHeight%, 19
	send {lbutton up}
	Temporary := (InversedDifference *NegativeMovementMultiplier *Strength *ResolutionScaling)
	tooltip, Immediate Task: Releasing For %Temporary%ms, tooltipMain, tooltip4, 4
	sleep %Temporary%
	send {lbutton down}
	Temporary := (InversedDifference *NegativeCounterMultiplier *Strength *ResolutionScaling)
	tooltip, Immediate Task: Holding For %Temporary%ms, tooltipMain, tooltip4, 4
	sleep %Temporary%
	send {lbutton up}
	goto BarStart
	}
goto BarStart
BarEnd:

tooltip, Current Task: Resetting, tooltipMain, tooltip3, 3
tooltip, Immediate Task: Waiting For %RecastDelay%ms, tooltipMain, tooltip4, 4
tooltip, , , , 5
tooltip, , , , 6
tooltip, , , , 7
tooltip, , , , 9
tooltip, , , , 19
tooltip, , , , 20
sleep %RecastDelay%
goto Reset
return

Scanner:
count++
tooltip, Times Scanned: %count%, tooltipMain, tooltip9, 9
PixelSearch, xxx, yyy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %FishPixelRange%, Fast
if (ErrorLevel = 0)
	{
	tooltip, Fish Bar: %xxx%, tooltipMain, tooltip5, 5
	tooltip, ., %xxx%, %FishTrackHeight%, 20
	}
else
	{
	FishFound = true
	settimer, Scanner, off
	return
	}
return