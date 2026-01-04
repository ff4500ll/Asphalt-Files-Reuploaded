setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
SetTitleMatchMode 2

WinActivate, Roblox
if !WinActive("Roblox")
	{
	msgbox, 0, No Roblox Instance Detected, Open Roblox First`n`nExiting Macro
	exitapp
	}
else
	{
	WinGet, winStyle, Style, Roblox
    if (winStyle & 0xC40000)
        {
            WinActivate
            Sleep, 500
            Send, {F11}
        }
	}
	
;===============================================

NavigationKey := "\"

CompassLeft := 1188
CompassRight := 1372
CompassBottom := 20
CompassColorTolerance := 10
CompassPixelTolerance := 10
CompassScanDelay := 10
CenterX := A_ScreenWidth/2
CompassMaxLeft := CenterX-CompassPixelTolerance
CompassMaxRight := CenterX+CompassPixelTolerance

BackpackLeft := 1210
BackpackTop := 1350
BackpackRight := 1350
BackpackBottom := 1360
BackpackColorTolerance := 10

HoldRodCastDuration := 500
WaitForBobberDelay := 2000
EndMinigameDelay := 1000

ShakeLeft := 490
ShakeRight := 2070
ShakeBottom := 1070
ShakeColorTolerance := 0
ClickShakeDelay := 200
ClickShakeResetMS := 200
ClickShakeMaxCount := ClickShakeResetMS/ClickShakeDelay

BarLeft := 765
BarTop := 1220
BarRight := 1795
BarBottom := 1255
BarBottomTooltip := 1380

FishBarTolerance := 0
WaitForBarDelay := 300
StaticWhiteBarTolerance := 0
DynamicWhiteBarTolerance := 0
ArrowTolerance := 0

BarMinigameScanDelay := 10

;===============================================

$l::
SetTimer, GetColor, 10
return
GetColor:
    MouseGetPos, MouseX, MouseY
    PixelGetColor, color, %MouseX%, %MouseY%
    ToolTip, %color% %MouseX% %MouseY%
return

$m:: exitapp
$o:: reload	
$p::

Start:
gosub TurnCameraModeOff

sleep 100
send 2
sleep 100
send 1

CompassDirectionLoop:
PixelSearch, CompassNorth, , CompassLeft, 0, CompassRight, CompassBottom, 0x74B7E8, %CompassColorTolerance%, Fast
if (ErrorLevel == 1)
	{
	send {left down}
	}
else
	{
	if (CompassNorth < CompassMaxLeft)
		{
		send {right up}
		send {left down}
		}
	else if (CompassNorth > CompassMaxRight)
		{
		send {left up}
		send {right down}
		}
	else
		{
		send {left up}
		send {right up}
		goto CompassDirectionFinish
		}
	}
sleep %CompassScanDelay%
goto CompassDirectionLoop
CompassDirectionFinish:

loop, 20
	{
	send {wheelup}
	sleep 10
	}
DllCall("mouse_event", "UInt", 0x0001, "UInt", 0, "UInt", 10000)
send {wheeldown}

sleep 100
gosub TurnCameraModeOn
sleep 100

send {lbutton down}
sleep %HoldRodCastDuration%
send {lbutton up}
sleep %WaitForBobberDelay%

ClickShakeLoop:
PixelSearch, ClickShakeX, ClickShakeY, ShakeLeft, 0, ShakeRight, ShakeBottom, 0xFFFFFF, %ShakeColorTolerance%, Fast
if (ErrorLevel == 0 && ClickShakeX <> MemoryX && ClickShakeY <> MemoryY)
	{
	mousemove, %ClickShakeX%, %ClickShakeY%
	click, %ClickShakeX%, %ClickShakeY%
	MemoryX := ClickShakeX
	MemoryY := ClickShakeY
	ClickShakeCounter := 0
	}
else
	{
	PixelSearch, , , BarLeft, BarTop, BarRight, BarBottom, 0x5B4B43, %FishBarTolerance%, Fast
	if (ErrorLevel == 0)
		{
		goto ClickShakeLoopFinish
		}
	else
		{
		ClickShakeCounter++
		if (ClickShakeCounter > ClickShakeMaxCount)
			{
			MemoryX := 0
			MemoryY := 0
			}		
		}
	}
sleep %ClickShakeDelay%
goto ClickShakeLoop
ClickShakeLoopFinish:

sleep %WaitForBarDelay%
PixelSearch, WhiteBarLeft, , BarLeft, BarTop, BarRight, BarBottom, 0xF1F1F1, %StaticWhiteBarTolerance%, Fast
PixelSearch, WhiteBarRight, , BarRight, BarTop, BarLeft, BarBottom, 0xF1F1F1, %StaticWhiteBarTolerance%, Fast
BarSize := WhiteBarRight-WhiteBarLeft
HalfBarSize := BarSize/2
QuarterBarSize := BarSize/4
SixthBarSize := BarSize/6

FishBarMaxLeft := BarLeft+HalfBarSize
FishBarMaxRight := BarRight-HalfBarSize

LeftDivision := 1.3
RightDivision := 1.6
LeftStrength := 2.5
RightStrength := 2.2
CounterMultiplier := 1.75

WaitForStart:
PixelSearch, WhiteBarLeft, , BarLeft, BarTop, BarRight, BarBottom, 0xF1F1F1, %StaticWhiteBarTolerance%, Fast
if (ErrorLevel == 0)
	{
	send {lbutton down}
	sleep 40
	send {lbutton up}
	sleep 10
	goto WaitForStart
	}

BarMinigameLoop:
PixelSearch, FishBarX, , BarLeft, BarTop, BarRight, BarBottom, 0x5B4B43, %FishBarTolerance%, Fast
if (ErrorLevel == 1)
	{
	goto BarMinigameFinish
	tooltip, , , , 1
	tooltip, , , , 2
	tooltip, , , , 3
	tooltip, , , , 4
	return
	}
tooltip, |, %FishBarX%, 1390, 1

if (FishBarX < FishBarMaxLeft)
	{
	if (OneTime == 0)
		{
		send {lbutton up}
		OneTime := 1
		tooltip, , , , 2
		tooltip, , , , 3
		tooltip, <, %FishBarMaxLeft%, 1390, 4
		Direction := 1
		sleep 500
		}
	}
else if (FishBarX > FishBarMaxRight)
	{
	if (OneTime == 0)
		{
		send {lbutton down}
		OneTime := 1
		tooltip, , , , 2
		tooltip, , , , 3
		tooltip, >, %FishBarMaxRight%, 1390, 4
		Direction := 0
		sleep 500
		}
	}
else
	{
	OneTime := 0
	PixelSearch, WhiteBarLeftX, , BarLeft, BarTop, BarRight, BarBottom, 0xFFFFFF, %DynamicWhiteBarTolerance%, Fast
	if (ErrorLevel == 0)
		{
		tooltip, |, %WhiteBarLeftX%, 1390, 2
		WhiteBarRightX := WhiteBarLeftX+BarSize
		tooltip, |, %WhiteBarRightX%, 1390, 3
		WhiteBarX := WhiteBarLeftX+HalfBarSize
		DeadZoneLeft := WhiteBarX-SixthBarSize
		DeadZoneRight := WhiteBarX+SixthBarSize
		if (FishBarX > DeadZoneLeft && FishBarX < DeadZoneRight)
			{
			tooltip, SPAMMING, , , 6
			send {lbutton down}
			sleep 30
			send {lbutton up}
			sleep 5
			}
		else if (FishBarX > WhiteBarX)
			{
			Distance := QuarterBarSize*RightStrength
			CounterDistance := Distance/RightDivision
			tooltip, D:%Distance% C:%CounterDistance%, , , 6
			
			;go right
			tooltip, >, %WhiteBarX%, 1410, 4
			send {lbutton down}
			sleep %Distance%
			send {lbutton up}
			if (Direction == 0)
				{
				CounterDistance := CounterDistance*CounterMultiplier
				}
			Direction := 1
			sleep %CounterDistance%
			}
		else
			{
			Distance := QuarterBarSize*RightStrength
			CounterDistance := Distance/RightDivision
			tooltip, D:%Distance% C:%CounterDistance%, , , 6
			
			;go left
			tooltip, <, %WhiteBarX%, 1410, 4
			send {lbutton up}
			sleep %Distance%
			send {lbutton down}
			if (Direction == 1)
				{
				CounterDistance := CounterDistance*CounterMultiplier
				}
			Direction := 0
			sleep %CounterDistance%
			}
		}
	else
		{
		PixelSearch, ArrowX, , BarLeft, BarTop, BarRight, BarBottom, 0x878584, %ArrowTolerance%, Fast
		tooltip, , , , 2
		tooltip, , , , 3
		if (FishBarX > ArrowX)
			{
			Distance := HalfBarSize*RightStrength
			CounterDistance := Distance/RightDivision
			tooltip, D:%Distance% C:%CounterDistance%, , , 6
			
			;go right
			tooltip, >, %WhiteBarX%, 1410, 4
			send {lbutton down}
			sleep %Distance%
			send {lbutton up}
			if (Direction == 0)
				{
				CounterDistance := CounterDistance*CounterMultiplier
				}
			Direction := 1
			sleep %CounterDistance%
			}
		else
			{
			Distance := HalfBarSize*RightStrength
			CounterDistance := Distance/LeftDivision
			tooltip, D:%Distance% C:%CounterDistance%, , , 6
			
			;go left
			tooltip, <, %WhiteBarX%, 1410, 4
			send {lbutton up}
			sleep %Distance%
			send {lbutton down}
			if (Direction == 1)
				{
				CounterDistance := CounterDistance*CounterMultiplier
				}
			Direction := 0
			sleep %CounterDistance%
			}
		}
	}

goto BarMinigameLoop
BarMinigameFinish:

sleep %EndMinigameDelay%
goto Start

;===============================================

TurnCameraModeOn:
PixelSearch, , , BackpackLeft, BackpackTop, BackpackRight, BackpackBottom, 0xF7F7F7, %BackpackColorTolerance%, Fast
if (ErrorLevel == 0)
	{
	send %NavigationKey%
	sleep 250
	loop, 10
		{
		send {right}
		sleep 10
		}
	sleep 250
	send {enter}
	sleep 250
	send %NavigationKey%
	sleep 100
	}
return

TurnCameraModeOff:
PixelSearch, , , BackpackLeft, BackpackTop, BackpackRight, BackpackBottom, 0xF7F7F7, %BackpackColorTolerance%, Fast
if (ErrorLevel == 1)
	{
	send %NavigationKey%
	sleep 250
	loop, 10
		{
		send {right}
		sleep 10
		}
	sleep 250
	send {enter}
	sleep 250
	send %NavigationKey%
	sleep 100
	}
return