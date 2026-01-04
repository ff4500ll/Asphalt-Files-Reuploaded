#SingleInstance Force
setkeydelay, 0
setmousedelay, 0
CoordMode, Tooltip, Screen
CoordMode, Pixel, Screen
CoordMode, Mouse, Screen

;======    General Settings    ===================================================================;

; How long to wait after fishing before recasting the rod
ExtraRodRecastDelay := 1000

; How long to hold the cast for before releasing
HoldRodCastDuration := 1000

; How long to wait for the bobber to land in water
WaitForBobberDelay := 1000

;======    Shake Settings    =====================================================================;

; Change To "Navigation" or "Click"
NavigationKey := "\"
AutoEnableCameraMode := true
ShakeMode := "Click"
WhiteBarColorTolerance := 15
FishBarColorTolerance := 4

; Click Circle Settings
ClickFailsafeTimer := 20
WhiteCircleColorTolerance := 4
ClickDelay := 100
RetryBypassCounter := 10

; Navigation UI Settings
NavigationFailsafeTimer := 20
NavigationInputDelay := 10

;======    Bar Minigame Settings    ==============================================================;

; Set to true to manually catch the fish
DisableMinigameMode := false

; Range for pixel color, higher = more color detected (higher chance of false positives)
IncreaseIfCantFindWhiteBar := 15
IncreaseIfCantFindFishBar := 4

; Bar Sensitivity Control
MinimumDifferenceAllowed := 10
MaximumDifferenceAllowed := 350
RightMultiplier := 2.5
RightDivision := 1.8
LeftMultiplier := 1
LeftDivision := 1.1
AnkleBreakerRightMultiplier := 1.8
AnkleBreakerLeftMultiplier := 0.5

;=================================================================================================;

gosub calculations
if (ShakeMode != "Navigation" and ShakeMode != "Click")
	{
	MsgBox, ShakeMode is invalid, use Navigation or Click
	return
	}
if (AutoEnableCameraMode != true and AutoEnableCameraMode != false)
	{
	MsgBox, AutoEnableCameraMode is invalid, use true or false
	return
	}
if (DisableMinigameMode != true and DisableMinigameMode != false)
	{
	MsgBox, DisableMinigameMode is invalid, use true or false
	return
	}
tooltip, Made By AsphaltCake, tooltipSide, tooltip2, 2
tooltip, Press "P" To Begin, tooltipSide, tooltip4, 4
tooltip, Press "O" To Reload, tooltipSide, tooltip5, 5
tooltip, Press "M" To Exit Script, tooltipSide, tooltip6, 6
if (ShakeMode == "Navigation")
	{
	tooltip, Shake Mode: Navigation, tooltipSide, tooltip8, 8
	tooltip, Shake Key: %NavigationKey%, tooltipSide, tooltip9, 9
	if (DisableMinigameMode == true)
		{
		tooltip, Minigame Mode: Manual, tooltipSide, tooltip11, 11
		}
	else
		{
		tooltip, Minigame Mode: Automatic, tooltipSide, tooltip11, 11
		}
	}
else if (ShakeMode == "Click")
	{
	tooltip, Shake Mode: Click, tooltipSide, tooltip8, 8
	if (DisableMinigameMode == true)
		{
		tooltip, Minigame Mode: Manual, tooltipSide, tooltip10, 10
		}
	else
		{
		tooltip, Minigame Mode: Automatic, tooltipSide, tooltip10, 10
		}
	}
	
;=================================================================================================;

calculations:
WinGetActiveStats, Title, Width, Height, ScreenWidthLeft, ScreenHeightTop
ScreenWidthLeft := ScreenWidthLeft
ScreenWidthRight := ScreenWidthLeft+Width
ScreenHeightTop := ScreenHeightTop
ScreenHeightBottom := ScreenHeightTop+Height
tooltipSide := ScreenWidthLeft+(Width/20)
tooltipSpacing :=  ScreenHeightTop+(Height/2)
tooltip1 := tooltipSpacing-180
tooltip2 := tooltipSpacing-160
tooltip3 := tooltipSpacing-140
tooltip4 := tooltipSpacing-120
tooltip5 := tooltipSpacing-100
tooltip6 := tooltipSpacing-80
tooltip7 := tooltipSpacing-60
tooltip8 := tooltipSpacing-40
tooltip9 := tooltipSpacing-20
tooltip10 := tooltipSpacing
tooltip11 := tooltipSpacing+20
tooltip12 := tooltipSpacing+40
tooltip13 := tooltipSpacing+60
tooltip14 := tooltipSpacing+80
tooltip15 := tooltipSpacing+100
tooltip16 := tooltipSpacing+120
tooltip17 := tooltipSpacing+140
tooltip18 := tooltipSpacing+160
tooltip19 := tooltipSpacing+180
tooltip20 := tooltipSpacing+200
EndShakeScanLeft := ScreenWidthLeft+(Width/2.0078)
EndShakeScanRight := ScreenWidthLeft+(Width/1.9922)
EndShakeScanTop := ScreenHeightTop+(Height/1.1842)
EndShakeScanBottom := ScreenHeightTop+(Height/1.1501)
ClickShakeLeft := ScreenWidthLeft+(Width/4.1967)
ClickShakeRight := ScreenWidthLeft+(Width/1.3128)
ClickShakeTop := ScreenHeightTop+(Height/4.4307)
ClickShakeBottom := ScreenHeightTop+(Height/1.0635)
FishScanLeft := ScreenWidthLeft+(Width/3.3464)
FishScanRight := ScreenWidthRight-(Width/3.3464)
FishScanTop := EndShakeScanTop
FishScanBottom := EndShakeScanBottom
FishTrackHeight := ScreenHeightTop+(Height/1.0397)
ResolutionScaling := 2560/Width
MiddleOfScreenX := ScreenWidthLeft+(Width/2)
MiddleOfScreenY := ScreenHeightTop+(Height/2)
tooltip, Runtime: 0h 0m 0s, tooltipSide, tooltip1, 1
return

;=================================================================================================;

COCK:
COCKERS++
if (COCKERS >= 60)
{
COCKERS := 0
COCKERM++
if (COCKERM >= 60)
{
COCKERM := 0
COCKERH++
}
}
tooltip, Runtime: %COCKERH%h %COCKERM%m %COCKERS%s, tooltipSide, tooltip1, 1
if WinActive("Roblox")
	{
	return
	}
else
	{
	click, MiddleOfScreenX, MiddleOfScreenY
	reload
	}

$o:: reload
return
$m:: exitapp
return
$p::
COCKERS := 0
COCKERM := 0
COCKERH := 0
TimerToggleOnce := true
settimer, COCK, 1000
gosub, calculations
tooltip, Made By AsphaltCake, tooltipSide, tooltip2, 2
tooltip, Press "O" To Reload, tooltipSide, tooltip4, 4
tooltip, Press "M" To Exit Script, tooltipSide, tooltip5, 5
tooltip, , , , 6
tooltip, , , , 8
tooltip, , , , 9
tooltip, , , , 10
tooltip, , , , 11
send {shift down}
loop, 9
	{
	send {f10 down}
	sleep 50
	send {f10 up}
	sleep 50
	}
send {shift up}
sleep 50
send {shift down}
sleep 50
send {shift up}
sleep 50
if (ShakeMode == "Navigation")
goto SkipAllThatBullshit
loop, 12
	{
	send {wheelup}
	sleep 100
	}
send {wheeldown}
SkipAllThatBullshit:
sleep 100
mousemove, %MiddleOfScreenX%, %MiddleOfScreenY%
sleep 100
send {rbutton down}
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 10000)
sleep 100
send {rbutton up}
sleep 100
FixCameraState := false
send {2 down}
sleep 100
send {2 up}
sleep 500
PixelSearch, WhiteX, WhiteY, ClickShakeLeft, ClickShakeTop, ClickShakeRight, ClickShakeBottom, 0xFFFFFF, 0, Fast
if (ErrorLevel == 0)
	{
	FixCameraState := true
	}
sleep 100
send {3 down}
sleep 100
send {3 up}
sleep 500
PixelSearch, WhiteX, WhiteY, ClickShakeLeft, ClickShakeTop, ClickShakeRight, ClickShakeBottom, 0xFFFFFF, 0, Fast
if (ErrorLevel == 0)
	{
	FixCameraState := true
	}
sleep 100
send {1 down}
sleep 100
send {1 up}
sleep 500
if (FixCameraState == true)
	{
	send {%NavigationKey% down}
	sleep 200
	send {%NavigationKey% up}
	sleep 200
	loop, 10
		{
		send {d down}
		sleep 50
		send {d up}
		sleep 50
		}
	send {enter down}
	sleep 200
	send {enter up}
	sleep 200
	}
sleep 100
send {m down}
sleep 100
send {m up}
sleep 500
goto SkipStartMacro
StartMacro:
mousemove, %MiddleOfScreenX%, %MiddleOfScreenY%
sleep 100
send {esc down}
sleep 100
send {esc up}
sleep 100
send {esc down}
sleep 100
send {esc up}
sleep 500
send {m down}
sleep 100
send {m up}
sleep 500
send {rbutton down}
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 10000)
sleep 100
send {rbutton up}
SkipStartMacro:
sleep 100
mousemove, %MiddleOfScreenX%, %MiddleOfScreenY%
sleep 100
sleep %ExtraRodRecastDelay%
send {lbutton up}
sleep 100
send {lbutton down}
sleep %HoldRodCastDuration%
send {lbutton up}
sleep %WaitForBobberDelay%

if (ShakeMode == "Navigation")
goto StartNavigation
if (ShakeMode == "Click")
goto StartClick

;=================================================================================================;

ClickFailsafe:
ClickCount++
tooltip, FailSafe: %ClickCount%/%ClickFailsafeTimer%, tooltipSide, tooltip7, 7
if (ClickCount >= ClickFailsafeTimer)
	{
	settimer, ClickFailsafe, off
	ClickForceReset := true
	}
return

StartClick:
ClickCount2 := 0
tooltip, FailSafe: 0/%ClickFailsafeTimer%, tooltipSide, tooltip7, 7
ClickCount := 0
ClickForceReset := false
settimer, ClickFailsafe, 1000

StartClick2:
if (ClickForceReset == true)
goto StartMacro
PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %FishBarColorTolerance%, Fast
if (ErrorLevel == 0)
	{
	settimer, ClickFailsafe, off
	if (DisableMinigameMode == true)
		{
		goto ManualMinigameMode
		}
	StartClick3:
	PixelSearch, WhiteX, WhiteY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0xFFFFFF, %WhiteBarColorTolerance%, Fast
	if (ErrorLevel == 0)
		{
		Offset := FishX-WhiteX
		tooltip, , , , 7
		goto StartFishingOnce
		}
	else
		{
		sleep 10
		goto StartClick3
		}
	}
else
	{
	PixelSearch, WhiteX, WhiteY, ClickShakeLeft, ClickShakeTop, ClickShakeRight, ClickShakeBottom, 0xFFFFFF, %WhiteCircleColorTolerance%, Fast
	if (ErrorLevel == 0)
		{
		if (WhiteX != MemoryX and WhiteY != MemoryY)
			{
			ClickCount2 := 0
			click, %WhiteX% %WhiteY%
			sleep %ClickDelay%
			MemoryX := WhiteX
			MemoryY := WhiteY
			goto StartClick2
			}
		else
			{
			ClickCount2++
			if (ClickCount2 > RetryBypassCounter)
			MemoryX := 0
			MemoryY := 0
			sleep 10
			goto StartClick2
			}
		}
	else
		{
		sleep 10
		goto StartClick2
		}
	}

;=================================================================================================;

NavigationFailsafe:
NavigationCount++
tooltip, FailSafe: %NavigationCount%/%NavigationFailsafeTimer%, tooltipSide, tooltip7, 7
if (NavigationCount >= NavigationFailsafeTimer)
	{
	settimer, NavigationFailsafe, off
	NavigationForceReset := true
	}
return

StartNavigation:
tooltip, FailSafe: 0/%NavigationFailsafeTimer%, tooltipSide, tooltip7, 7
NavigationCount := 0
NavigationForceReset := false
settimer, NavigationFailsafe, 1000
send {%NavigationKey% down}
sleep 200
send {%NavigationKey% up}
sleep 200
StartNavigation2:
if (NavigationForceReset == true)
goto StartMacro
PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %FishBarColorTolerance%, Fast
if (ErrorLevel == 0)
	{
	settimer, NavigationFailsafe, off
	if (DisableMinigameMode == true)
		{
		goto ManualMinigameMode
		}
	StartNavigation3:
	PixelSearch, WhiteX, WhiteY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0xFFFFFF, %WhiteBarColorTolerance%, Fast
	if (ErrorLevel == 0)
		{
		Offset := FishX-WhiteX
		tooltip, , , , 7
		goto StartFishingOnce
		}
	else
		{
		sleep 10
		goto StartNavigation3
		}
	}
else
	{
	send {s down}
	sleep %NavigationInputDelay%
	send {s up}
	sleep %NavigationInputDelay%
	send {enter down}
	sleep %NavigationInputDelay%
	send {enter up}
	sleep %NavigationInputDelay%
	goto StartNavigation2
	}
	
;=================================================================================================;

ManualMinigameMode:
PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
if (ErrorLevel == 0)
	{
	sleep 100
	tooltip, Manual Fishing In Progress, tooltipSide, tooltip7, 7
	goto ManualMinigameMode
	}
else
	{
	tooltip, Manual Fishing Complete, tooltipSide, tooltip7, 7
	goto StartMacro
	}
	
;=================================================================================================;

StartFishingOnce:

MaxToggleRight := false
MaxToggleLeft := false

PositionLeft := (FishScanLeft+Offset)
PositionRight := (FishScanRight-Offset)

ReleaseLeft := (FishScanLeft+Offset*1.7)
ReleaseRight := (FishScanRight-Offset*1.7)

GoingLeft := false
GoingRight := false

StartFishing:
PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
if (ErrorLevel == 0)
	{
	tooltip, ., %FishX%, %FishTrackHeight%, 20
	if (MaxToggleLeft == true)
		{
		if (FishX > ReleaseLeft)
			{
			GoingLeft := false
			GoingRight := false
			MaxToggleLeft := false
			}
		sleep 10
		goto StartFishing
		}
	else if (MaxToggleRight == true)
		{
		if (FishX < ReleaseRight)
			{
			GoingLeft := false
			GoingRight := false
			MaxToggleRight := false
			}
		sleep 10
		goto StartFishing
		}
	MaxToggleRight := false
	MaxToggleLeft := false
	PixelSearch, WhiteX, WhiteY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0xFFFFFF, %IncreaseIfCantFindWhiteBar%, Fast
	if (ErrorLevel == 0)
		{
		WhiteX := WhiteX+Offset
		Direction := FishX-WhiteX
		if (Direction > 0)
			{
			tooltip, >, %WhiteX%, %FishTrackHeight%, 19
			Difference := (FishX-WhiteX)*ResolutionScaling*RightMultiplier
			if (Difference < MinimumDifferenceAllowed)
			Difference := MinimumDifferenceAllowed
			if (Difference > MaximumDifferenceAllowed)
			Difference := MaximumDifferenceAllowed
			CounterStability := Difference/RightDivision
			tooltip, Difference: %Difference%ms, tooltipSide, tooltip7, 7
			tooltip, CounterStability: %CounterStability%ms, tooltipSide, tooltip8, 8
			tooltip, Direction: >>>, tooltipSide, tooltip9, 9
			send {lbutton down}
			sleep %Difference%
			PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
			if (FishX > PositionRight)
				{
				tooltip, >, %ReleaseRight%, %FishTrackHeight%, 19
				tooltip, Difference: bruh, tooltipSide, tooltip7, 7
				tooltip, CounterStability: bruh, tooltipSide, tooltip8, 8
				tooltip, Direction: >>>, tooltipSide, tooltip9, 9
				MaxToggleRight := true
				RescanArrow1:
				PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %IncreaseIfCantFindFishBar%, Fast
				if (Memory == FishX)
					{
					sleep 10
					goto StartFishing
					}
				Memory := FishX
				sleep 50
				goto RescanArrow1
				}
			GoingRight := true
			if (GoingLeft == true)
				{
				GoingLeft := false
				AnkleBreakerDuration := Difference*AnkleBreakerRightMultiplier
				if (AnkleBreakerDuration > MaximumDifferenceAllowed)
				AnkleBreakerDuration := MaximumDifferenceAllowed
				sleep %AnkleBreakerDuration%
				}
			send {lbutton up}
			sleep %CounterStability%
			}
		else
			{
			tooltip, <, %WhiteX%, %FishTrackHeight%, 19
			Difference := (WhiteX-FishX)*ResolutionScaling*LeftMultiplier
			if (Difference < MinimumDifferenceAllowed)
			Difference := MinimumDifferenceAllowed
			if (Difference > MaximumDifferenceAllowed)
			Difference := MaximumDifferenceAllowed
			CounterStability := Difference/LeftDivision
			tooltip, Difference: %Difference%ms, tooltipSide, tooltip7, 7
			tooltip, CounterStability: %CounterStability%ms, tooltipSide, tooltip8, 8
			tooltip, Direction: <<<, tooltipSide, tooltip9, 9
			send {lbutton up}
			sleep %Difference%
			PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
			if (FishX < PositionLeft)
				{
				tooltip, <, %ReleaseLeft%, %FishTrackHeight%, 19
				tooltip, Difference: bruh, tooltipSide, tooltip7, 7
				tooltip, CounterStability: bruh, tooltipSide, tooltip8, 8
				tooltip, Direction: <<<, tooltipSide, tooltip9, 9
				MaxToggleLeft := true
				RescanArrow2:
				PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %IncreaseIfCantFindFishBar%, Fast
				if (Memory == FishX)
					{
					sleep 10
					goto StartFishing
					}
				Memory := FishX
				sleep 50
				goto RescanArrow2
				}
			GoingLeft := true
			if (GoingRight == true)
				{
				GoingRight := false
				AnkleBreakerDuration := Difference*AnkleBreakerLeftMultiplier
				if (AnkleBreakerDuration > MaximumDifferenceAllowed)
				AnkleBreakerDuration := MaximumDifferenceAllowed
				sleep %AnkleBreakerDuration%
				}
			send {lbutton down}
			sleep %CounterStability%
			send {lbutton up}
			}
		goto StartFishing
		}
	else
		{
		PixelSearch, ArrowX, ArrowY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %IncreaseIfCantFindFishBar%, Fast
		if (ErrorLevel == 0)
			{
			Direction := FishX-ArrowX
			if (Direction > 0)
				{
				TooltipX := FishX-Offset
				tooltip, >, %TooltipX%, %FishTrackHeight%, 19
				Difference := MaximumDifferenceAllowed
				CounterStability := Difference/RightDivision
				tooltip, Difference: %Difference%ms, tooltipSide, tooltip7, 7
				tooltip, CounterStability: %CounterStability%ms, tooltipSide, tooltip8, 8
				tooltip, Direction: >>>, tooltipSide, tooltip9, 9
				send {lbutton down}
				sleep %Difference%
				PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
				if (FishX > PositionRight)
					{
					tooltip, >, %ReleaseRight%, %FishTrackHeight%, 19
					tooltip, Difference: bruh, tooltipSide, tooltip7, 7
					tooltip, CounterStability: bruh, tooltipSide, tooltip8, 8
					tooltip, Direction: >>>, tooltipSide, tooltip9, 9
					MaxToggleRight := true
					RescanArrow3:
					PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %IncreaseIfCantFindFishBar%, Fast
					if (Memory == FishX)
						{
						sleep 10
						goto StartFishing
						}
					Memory := FishX
					sleep 50
					goto RescanArrow3
					}
				GoingRight := true
				if (GoingLeft == true)
					{
					GoingLeft := false
					AnkleBreakerDuration := Difference*AnkleBreakerRightMultiplier
					if (AnkleBreakerDuration > MaximumDifferenceAllowed)
					AnkleBreakerDuration := MaximumDifferenceAllowed
					sleep %AnkleBreakerDuration%
					}
				send {lbutton up}
				sleep %CounterStability%
				}
			else
				{
				TooltipX := FishX+Offset
				tooltip, <, %TooltipX%, %FishTrackHeight%, 19
				Difference := MaximumDifferenceAllowed
				CounterStability := Difference/LeftDivision
				tooltip, Difference: %Difference%ms, tooltipSide, tooltip7, 7
				tooltip, CounterStability: %CounterStability%ms, tooltipSide, tooltip8, 8
				tooltip, Direction: <<<, tooltipSide, tooltip9, 9
				send {lbutton up}
				sleep %Difference%
				PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
				if (FishX < PositionLeft)
					{
					tooltip, <, %ReleaseLeft%, %FishTrackHeight%, 19
					tooltip, Difference: bruh, tooltipSide, tooltip7, 7
					tooltip, CounterStability: bruh, tooltipSide, tooltip8, 8
					tooltip, Direction: <<<, tooltipSide, tooltip9, 9
					MaxToggleLeft := true
					RescanArrow4:
					PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %IncreaseIfCantFindFishBar%, Fast
					if (Memory == FishX)
						{
						sleep 10
						goto StartFishing
						}
					Memory := FishX
					sleep 50
					goto RescanArrow4
					}
				GoingLeft := true
				if (GoingRight == true)
					{
					GoingRight := false
					AnkleBreakerDuration := Difference*AnkleBreakerLeftMultiplier
					if (AnkleBreakerDuration > MaximumDifferenceAllowed)
					AnkleBreakerDuration := MaximumDifferenceAllowed
					sleep %AnkleBreakerDuration%
					}
				send {lbutton down}
				sleep %CounterStability%
				send {lbutton up}
				}
			goto StartFishing
			}
		else
			{
			sleep 1
			goto StartFishing
			}
		}
	}
else
	{
	tooltip, , , , 7
	tooltip, , , , 8
	tooltip, , , , 9
	tooltip, , , , 19
	tooltip, , , , 20
	goto StartMacro
	}