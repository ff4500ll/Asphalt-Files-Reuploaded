#ifWinActive, Roblox
setkeydelay, 0
setmousedelay, 0

;===============    Settings    ====================;

; Turn this to false if compass check breaks
CompassCheckFaceNorth = true

; Turn this to false if rod casting breaks
UseImageForRodCast = true
CustomDelay := 500

; Change these values if u dont want to always face north
LeftFromNorthValue := 0
RightFromNorthValue := 0

; These settings affect the bar balance minigame
Strength := 1.2

; This setting will make u move back after a cast (have a corner wall behind you)
TapS = false

; If it doesnt find "shake" increase this number by 1 at a time
PixelColorRange := 1

;===================================================;

; Dont change these unless you know what they do
Stability := 0.8
HoldBypassMultiplier := 1.3
ReleaseBypassMultiplier := 1.1
BarSizeMultiplier := 1
FishBarTolerance := 30
StartFishingTolerance := 15
BarTrackTolerance := 5
NorthOrangeTolerance := 5

;===================================================;

CompassLeft := A_ScreenWidth/2.02
CompassRight := A_ScreenWidth-A_ScreenWidth/2.02
CompassBottom := A_ScreenHeight/60

SmallNumbering := A_ScreenWidth/94.8148

FishBarLeft := A_ScreenWidth/2
FishBarRight := A_ScreenWidth
FishBarBottom := A_ScreenWidth/2

ShakeLeft := A_ScreenWidth/5
ShakeRight := A_ScreenWidth-(A_ScreenWidth/5)
ShakeTop := A_ScreenHeight/5
ShakeBottom := A_ScreenHeight-(A_ScreenHeight/4)

StartFishingToleranceLeft := A_ScreenWidth/2.0562
StartFishingToleranceRight := A_ScreenWidth-(A_ScreenWidth/2.0562)
StartFishingToleranceTop := A_ScreenHeight/1.1803
StartFishingToleranceBottom := A_ScreenHeight/1.1492

BalanceBarLeft := A_ScreenWidth/3.3246
BalanceBarRight := A_ScreenWidth-(A_ScreenWidth/3.3246)
BalanceBarTop := A_ScreenHeight/1.1774
BalanceBarBottom := A_ScreenHeight/1.1492

tooltipside := A_ScreenWidth/20
tooltip1 := A_ScreenHeight/2
tooltip2 := A_ScreenHeight/2+20
tooltip3 := A_ScreenHeight/2+40
tooltip4 := A_ScreenHeight/2+60
tooltip5 := A_ScreenHeight/2+80
tooltip6 := A_ScreenHeight/2+100

tooltip, Press P to begin, tooltipside, tooltip1, 1
tooltip, idle, tooltipside, tooltip2, 2
tooltip, idle, tooltipside, tooltip3, 3
tooltip, Dont use shiftlock, tooltipside, tooltip4, 4
tooltip, Disable brightness and saturation in menu, tooltipside, tooltip5, 5
tooltip, Made By AsphaltCake, tooltipside, tooltip6, 6

$o::
send {left up}
send {right up}
send {lbutton up}
reload
return

$p::
StartOfItAll:

send {lbutton up}
send {left up}
send {right up}
send {2 up}
send {1 up}

settimer, milisecondtimer, off

tooltip, Press O to disable, tooltipside, tooltip1, 1
tooltip, idle, tooltipside, tooltip2, 2
tooltip, idle, tooltipside, tooltip3, 3
tooltip, idle, tooltipside, tooltip4, 4
tooltip, idle, tooltipside, tooltip5, 5
tooltip, idle, tooltipside, tooltip6, 6

tooltip, Current Task: Selecting Rod, tooltipside, tooltip2, 2
send {2 down}
sleep 10
send {2 up}
sleep 100
send {1 down}
sleep 10
send {1 up}
sleep 400

if CompassCheckFaceNorth = false
goto FaceDirectionBypass
tooltip, Current Task: Searching For North, tooltipside, tooltip2, 2
tooltip, idle, tooltipside, tooltip3, 3
FaceDirection:
if (RightFromNorthValue > LeftFromNorthValue)
{
	PixelSearch, xxx, yyy, CompassLeft, 0, CompassRight, CompassBottom, 0x76B8E7, %NorthOrangeTolerance%, Fast
	if (ErrorLevel = 0)
	{
	send {left up}
	tooltip, Orange Found, tooltipside, tooltip3, 3
	goto FaceDirectionBypass
	}
	else
	{
	send {left down}
	tooltip, Rotating Left, tooltipside, tooltip3, 3
	goto FaceDirection
	}
}
else
{
	PixelSearch, xxx, yyy, CompassLeft, 0, CompassRight, CompassBottom, 0x76B8E7, %NorthOrangeTolerance%, Fast
	if (ErrorLevel = 0)
	{
	send {right up}
	tooltip, Orange Found, tooltipside, tooltip3, 3
	goto FaceDirectionBypass
	}
	else
	{
	send {right down}
	tooltip, Rotating Right, tooltipside, tooltip3, 3
	goto FaceDirection
	}
}
FaceDirectionBypass:

If (RightFromNorthValue <> 0)
{
	tooltip, Current Task: Facing User Direction, tooltipside, tooltip2, 2
	tooltip, Turning Right %RightFromNorthValue%ms, tooltipside, tooltip3, 3
	send {right down}
	sleep %RightFromNorthValue%
	send {right up}
}
If (LeftFromNorthValue <> 0)
{
	tooltip, Current Task: Facing User Direction, tooltipside, tooltip2, 2
	tooltip, Turning Left %LeftFromNorthValue%ms, tooltipside, tooltip3, 3
	send {left down}
	sleep %LeftFromNorthValue%
	send {left up}
}

if UseImageForRodCast = true
{
tooltip, Current Task: Adjusting Camera Zoom, tooltipside, tooltip2, 2
loop, 20
{
tooltip, Zooming In, tooltipside, tooltip3, 3
send {wheelup}
sleep 10
}

if TapS = true
{
send {s down}
sleep 10
send {s up}
}

tooltip, Current Task: Adjusting Camera Direction, tooltipside, tooltip2, 2
tooltip, Facing Down, tooltipside, tooltip3, 3
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 10000)
sleep 10

tooltip, Current Task: Adjusting Camera Zoom, tooltipside, tooltip2, 2
loop, 4
{
tooltip, Zooming Out, tooltipside, tooltip3, 3
send {wheeldown}
sleep 10
}
}

milicount = 0
milisecond = 5
milicheck = false
settimer, milisecondtimer, 1000

tooltip, Current Task: Casting Rod, tooltipside, tooltip2, 2
FishBar:
if UseImageForRodCast = true
{
send {lbutton down}
tooltip, Waiting For Bar, tooltipside, tooltip3, 3
ImageSearch, xxx, yyy, FishBarLeft, 0, FishBarRight, FishBarBottom, *%FishBarTolerance% %A_ScriptDir%\Images\Bar.png
	if (ErrorLevel = 0)
	{
	tooltip, Rod Casted, tooltipside, tooltip3, 3
	send {lbutton up}
	goto FishBarBypass
	}
	else
	if milicheck = true
	{
	goto StartOfItAll
	}
	goto FishBar
}
else
{
tooltip, %CustomDelay%ms Delay Mode, tooltipside, tooltip3, 3
send {lbutton down}
sleep %CustomDelay%
send {lbutton up}
}
FishBarBypass:

milicount = 0
milisecond = 5
milicheck = false
settimer, milisecondtimer, 1000

tooltip, Current Task: Auto Shaking, tooltipside, tooltip2, 2
tooltip, Found 0, tooltipside, tooltip3, 3
count = 0
resetcounter = 0
AutoShake:
sleep 5
ImageSearch, xxx, yyy, StartFishingToleranceLeft, StartFishingToleranceTop, StartFishingToleranceRight, StartFishingToleranceBottom, *%StartFishingTolerance% %A_ScriptDir%\Images\StartFishing.png
		if (ErrorLevel = 0)
		{
		settimer, milisecondtimer, off
		goto AutoShakeBypass
		}
PixelSearch, xxx, yyy, ShakeLeft, ShakeTop, ShakeRight, ShakeBottom, 0xFFFFFF, %PixelColorRange%, Fast
	if (ErrorLevel = 0)
	{
	if (xxx == xhold) or (yyy == yhold)
	{
		resetcounter++
		tooltip, failsafe: %resetcounter%/10, tooltipside, tooltip5, 5
		if resetcounter > 10
		{
		goto FailSafeShake
		}
		goto AutoShake
	}
	FailSafeShake:
	resetcounter = 0
	xhold := xxx
	yhold := yyy
	count++
	mousemove, xxx, yyy
	sendinput, {click}
	milicount = 0
	tooltip, Found %count%, tooltipside, tooltip3, 3
	tooltip, x:%xxx% y:%yyy%, tooltipside, tooltip4, 4
	goto AutoShake
	}
	else
	{
	tooltip, Waiting For Bar, tooltipside, tooltip4, 4
	if milicheck = true
	{
	goto StartOfItAll
	}
	goto AutoShake
	}
return
AutoShakeBypass:

toggle = false
finalcount := 0
barsizecount := 0

tooltip, Current Task: Balancing The Bar, tooltipside, tooltip2, 2
BarBalance:
sleep 10
PixelSearch, xxx, yyy, BalanceBarLeft, BalanceBarTop, BalanceBarRight, BalanceBarBottom, 0x5B4B43, %BarTrackTolerance%, Fast
if (ErrorLevel = 0)
{
tooltip, Found Bar, tooltipside, tooltip3, 3
tooltip, Bar: %xxx%, tooltipside, tooltip4, 4
PixelSearch, xx, yy, BalanceBarLeft, BalanceBarTop, BalanceBarRight, BalanceBarBottom, 0x878584, %BarTrackTolerance%, Fast
if (ErrorLevel = 0)
{
if (barsizecount < 5)
{
barsizecount++
MaxLeft := BalanceBarLeft+(((xxx-xx+SmallNumbering)*2)*BarSizeMultiplier)
MaxRight := BalanceBarRight-(((xxx-xx+SmallNumbering)*2)*BarSizeMultiplier)
tooltip, Calculating Bar Size: %barsizecount%/5, tooltipside, tooltip6, 6
sleep 100
goto BarBalance
}
	if (xxx > MaxRight)
		{
		if toggle = false
		{
		tooltip, Max Right, tooltipside, tooltip6, 6
		send {lbutton down}
		toggle = true
		}
		goto BarBalance
		}
	toggle = false
	if (xxx < MaxLeft)
		{
		tooltip, Max Left, tooltipside, tooltip6, 6
		send {lbutton up}
		goto BarBalance
		}
	tooltip, Arrow: %xx%, tooltipside, tooltip5, 5
	Difference := xxx-xx
			if Difference < (A_ScreenWidth/25)
			{
			send {lbutton down}
			sleep 10
			send {lbutton up}
			sleep 10
			}
			else
			{
			if Difference > 0
				{
				tooltip, Moving Bar Right (%Difference%), tooltipside, tooltip6, 6
				Difference := Difference * Strength * HoldBypassMultiplier
				send {lbutton down}
				sleep %Difference%
				Difference := Difference * Stability
				send {lbutton up}
				sleep %Difference%
				}
				else
				{
				tooltip, Moving Bar Left (%Difference%), tooltipside, tooltip6, 6
				Difference := xx-xxx
				Difference := Difference * Strength
				send {lbutton up}
				sleep %Difference%
				Difference := Difference * Stability * ReleaseBypassMultiplier
				send {lbutton down}
				sleep %Difference%
				send {lbutton up}
				}
			}
	}
	else
	{
	tooltip, Bar Lost, tooltipside, tooltip3, 3
	tooltip, Arrow Lost, tooltipside, tooltip4, 4
	}
}
else
{
tooltip, Bar Lost, tooltipside, tooltip3, 3
tooltip, Bar Lost, tooltipside, tooltip4, 4
finalcount++
sleep 100
if finalcount > 5
goto BarBalanceBypass
goto BarBalance
}
goto BarBalance
BarBalanceBypass:

tooltip, Current Task: Fishing Completed, tooltipside, tooltip2, 2
goto StartOfItAll
return

milisecondtimer:
milicount++
sleep 100
tooltip, failcount %milicount%/%milisecond%, tooltipside, tooltip6, 6
if milicount > %milisecond%
{
milicheck = true
settimer, milisecondtimer, off
}
return