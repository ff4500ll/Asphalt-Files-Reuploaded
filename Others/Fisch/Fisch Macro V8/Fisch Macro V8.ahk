#ifWinActive, Roblox
#SingleInstance Force
setkeydelay, 0
setmousedelay, 0
CoordMode, Tooltip, Screen
CoordMode, Pixel, Screen
CoordMode, Mouse, Screen

;======    General Settings    ===================================================================;

; How long to wait after fishing before recasting the rod
ExtraRodRecastDelay := 500

; How long to hold the cast for before releasing
HoldRodCastDuration := 500

; How long to wait for the bobber to land in water
WaitForBobberDelay := 1000

; Scan for illegal background pixels
IdleScanDelay := 10

;======    Shake Settings    =====================================================================;

; Change To "Navigation" or "Click"
ShakeMode := "Click"
WhiteBarColorTolerance := 15
FishBarColorTolerance := 0

; Navigation UI Settings
NavigationKey := "\"
AutoEnableCameraMode := true
NavigationFailsafeTimer := 20
NavigationInputDelay := 10

; Click Circle Settings
ClickFailsafeTimer := 20
WhiteCircleColorTolerance := 0
ClickDelay := 100
RetryBypassCounter := 10

;======    Bar Minigame Settings    ==============================================================;

; Set to true to manually catch the fish
DisableMinigameMode := false

; You generally dont want to change these
IncreaseIfCantFindWhiteBar := 15
IncreaseIfCantFindFishBar := 0
IncreaseIfCantFindArrow := 0

; You generally dont want to change these
FailScanDelay := 1
MinimumDifferenceAllowed := 10

; Settings that affect Stable Control (stable = within correct location)
MaximumStableDifferenceAllowed := 250
StableRightMultiplier := 2
StableRightDivision := 3
StableLeftMultiplier := 1
StableLeftDivision := 1

; Settings that affect Unstable Control (unstable = outside correct location)
MaximumUnstableDifferenceAllowed := 600
UnstableMovementDuration := 150
UnstableRightMultiplier := 3
UnstableRightDivision := 1.5
UnstableLeftMultiplier := 3
UnstableLeftDivision := 1.5

; For when the fish bar goes to the extreme ends
; (to counter when the fishbar goes in then just straight leaves)
MaxHoldDuration := 1000
MaxReleaseDuration := 700

;==================================================================================================

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

;==================================================================================================

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

;==================================================================================================

tooltip, Made By AsphaltCake, tooltipSide, tooltip1, 1
tooltip, Press "P" To Begin, tooltipSide, tooltip3, 3
tooltip, Press "M" To Exit Script, tooltipSide, tooltip4, 4
tooltip, HOLD YOUR FISHING ROD, tooltipSide, tooltip6, 6
tooltip, Disable Higher Saturation (ingame menu), tooltipSide, tooltip7, 7
tooltip, Disable Higher Brightness (ingame menu), tooltipSide, tooltip8, 8
if (ShakeMode == "Navigation")
	{
	tooltip, Enable Camera Mode (top right icon), tooltipSide, tooltip9, 9
	tooltip, Shake Mode: Navigation, tooltipSide, tooltip11, 11
	tooltip, Shake Key: %NavigationKey%, tooltipSide, tooltip12, 12
	}
else if (ShakeMode == "Click")
	{
	tooltip, Shake Mode: Click, tooltipSide, tooltip10, 10
	}
settimer, IdleScan, %IdleScanDelay%

;==================================================================================================

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
ClickShakeBottom := ScreenHeightTop+(Height/1.3211)
FishScanLeft := ScreenWidthLeft+(Width/3.3464)
FishScanRight := ScreenWidthRight-(Width/3.3464)
FishScanTop := EndShakeScanTop
FishScanBottom := EndShakeScanBottom
FishTrackHeight := ScreenHeightTop+(Height/1.0397)
ResolutionScaling := 2560/Width
ArrowPixelOffset := 40/ResolutionScaling
CameraCheckLeft := ScreenWidthLeft+(Width/3.7155)
CameraCheckRight := ScreenWidthLeft+(Width/3.6260)
CameraCheckTop := ScreenHeightTop+(Height/3.8095)
CameraCheckBottom := ScreenHeightTop+(Height/3.5207)
MiddleOfScreenX := Width/3
MiddleOfScreenY := Height/2
IdleScan:
if (AutoEnableCameraMode == true)
	{
	PixelSearch, WhiteX, WhiteY, CameraCheckLeft, CameraCheckTop, CameraCheckRight, CameraCheckBottom, 0xFFFFFF, 0, Fast
	if (ErrorLevel == 0)
		{
		tooltip, ILLEGAL PIXEL: WHITE (if you see this check discord #common-issues) (reload to remove), WhiteX, WhiteY, 15
		}
	}
if (ShakeMode == "Click")
	{
	PixelSearch, WhiteX, WhiteY, ClickShakeLeft, ClickShakeTop, ClickShakeRight, ClickShakeBottom, 0xFFFFFF, %WhiteCircleColorTolerance%, Fast
	if (ErrorLevel == 0)
		{
		tooltip, ILLEGAL PIXEL: CLICK (if you see this check discord #common-issues) (reload to remove), WhiteX, WhiteY, 14
		}
	}
PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
if (ErrorLevel == 0)
	{
	tooltip, ILLEGAL PIXEL: FISH BAR (if you see this check discord #common-issues) (reload to remove), FishX, FishY, 16
	}
return
	
;==================================================================================================

$o:: reload
return
$m:: exitapp
return
$p::
settimer, IdleScan, off
tooltip, , , , 1
tooltip, , , , 3
tooltip, , , , 4
tooltip, , , , 6
tooltip, , , , 7
tooltip, , , , 8
tooltip, , , , 9
tooltip, , , , 10
tooltip, , , , 11
tooltip, , , , 12
tooltip, , , , 13
tooltip, , , , 14
tooltip, , , , 15
tooltip, , , , 16
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
ClickShakeBottom := ScreenHeightTop+(Height/1.3211)
FishScanLeft := ScreenWidthLeft+(Width/3.3464)
FishScanRight := ScreenWidthRight-(Width/3.3464)
FishScanTop := EndShakeScanTop
FishScanBottom := EndShakeScanBottom
FishTrackHeight := ScreenHeightTop+(Height/1.0397)
ResolutionScaling := 2560/Width
ArrowPixelOffset := 40/ResolutionScaling
CameraCheckLeft := ScreenWidthLeft+(Width/3.7155)
CameraCheckRight := ScreenWidthLeft+(Width/3.6260)
CameraCheckTop := ScreenHeightTop+(Height/3.8095)
CameraCheckBottom := ScreenHeightTop+(Height/3.5207)

tooltip, Made By AsphaltCake, tooltipSide, tooltip1, 1
tooltip, Press "O" To Reload, tooltipSide, tooltip3, 3
tooltip, Press "M" To Exit Script, tooltipSide, tooltip4, 4

goto StartMacro

;==================================================================================================

StartMacro:
if (ShakeMode == "Click")
AutoEnableCameraMode := false
goto CastBobber

;==================================================================================================

CastBobber:
if (AutoEnableCameraMode == false)
	{
	tooltip, Waiting 1000ms, tooltipSide, tooltip6, 6
	sleep 1000
	goto SkipCameraChecks
	}
tooltip, Checking Camera State, tooltipSide, tooltip6, 6
FixCameraState := false
send {2 down}
sleep 100
send {2 up}
sleep 500
PixelSearch, WhiteX, WhiteY, CameraCheckLeft, CameraCheckTop, CameraCheckRight, CameraCheckBottom, 0xFFFFFF, 0, Fast
if (ErrorLevel == 0)
	{
	FixCameraState := true
	}
send {3 down}
sleep 100
send {3 up}
sleep 500
PixelSearch, WhiteX, WhiteY, CameraCheckLeft, CameraCheckTop, CameraCheckRight, CameraCheckBottom, 0xFFFFFF, 0, Fast
if (ErrorLevel == 0)
	{
	FixCameraState := true
	}
send {1 down}
sleep 100
send {1 up}
sleep 500

if (FixCameraState == true)
	{
	tooltip, Enabling Camera Mode, tooltipSide, tooltip6, 6
	send {%NavigationKey% down}
	sleep 100
	send {%NavigationKey% up}
	sleep 100
	loop, 5
		{
		send {right down}
		sleep 100
		send {right up}
		sleep 100
		}
	send {enter down}
	sleep 100
	send {enter up}
	sleep 1000
	}

SkipCameraChecks:
tooltip, Waiting %ExtraRodRecastDelay%ms, tooltipSide, tooltip6, 6
sleep %ExtraRodRecastDelay%
send {lbutton down}
tooltip, Casting Rod For %HoldRodCastDuration%ms, tooltipSide, tooltip6, 6
sleep %HoldRodCastDuration%
send {lbutton up}
tooltip, Waiting %HoldRodCastDuration%ms For Bobber, tooltipSide, tooltip6, 6
sleep %WaitForBobberDelay%
if (ShakeMode == "Navigation")
goto StartNavigation
if (ShakeMode == "Click")
tooltip, Waiting 500ms For ClickShake, tooltipSide, tooltip6, 6
sleep 500
goto StartClick

;==================================================================================================

ClickFailsafe:
ClickCount++
tooltip, FailSafe: %ClickCount%/%ClickFailsafeTimer%, tooltipSide, tooltip6, 6
if (ClickCount >= ClickFailsafeTimer)
	{
	settimer, ClickFailsafe, off
	ClickForceReset := true
	}
return

StartClick:
ClickCount2 := 0
tooltip, FailSafe: 0/%ClickFailsafeTimer%, tooltipSide, tooltip6, 6
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
		StartClick4:
		PixelSearch, ArrowX, ArrowY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %IncreaseIfCantFindArrow%, Fast
		if (ErrorLevel == 0)
			{
			WhiteOffset := FishX-WhiteX
			ArrowOffset := FishX-ArrowX
			tooltip, , , , 6
			goto StartFishingOnce
			}
		else
			{
			sleep 10
			goto StartClick4
			}
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

;==================================================================================================

NavigationFailsafe:
NavigationCount++
tooltip, FailSafe: %NavigationCount%/%NavigationFailsafeTimer%, tooltipSide, tooltip6, 6
if (NavigationCount >= NavigationFailsafeTimer)
	{
	settimer, NavigationFailsafe, off
	NavigationForceReset := true
	}
return

StartNavigation:
tooltip, FailSafe: 0/%NavigationFailsafeTimer%, tooltipSide, tooltip6, 6
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
		StartNavigation4:
		PixelSearch, ArrowX, ArrowY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %IncreaseIfCantFindArrow%, Fast
		if (ErrorLevel == 0)
			{
			WhiteOffset := FishX-WhiteX
			ArrowOffset := FishX-ArrowX
			tooltip, , , , 6
			goto StartFishingOnce
			}
		else
			{
			sleep 10
			goto StartNavigation4
			}
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


;==================================================================================================

ManualMinigameMode:
PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
if (ErrorLevel == 0)
	{
	sleep 100
	tooltip, Manual Fishing In Progress, tooltipSide, tooltip6, 6
	goto ManualMinigameMode
	}
else
	{
	tooltip, Manual Fishing Complete, tooltipSide, tooltip6, 6
	goto StartMacro
	}

;==================================================================================================

StartFishingOnce:

DynamicMaxLeft := FishScanLeft+WhiteOffset
DynamicMaxRight := FishScanRight-WhiteOffset

TriggerMaxLeft := FishScanLeft+WhiteOffset
TriggerMaxRight := FishScanRight-WhiteOffset

ReleaseMaxLeft := FishScanLeft+WhiteOffset*1.5
ReleaseMaxRight := FishScanRight-WhiteOffset*1.5

MaxToggleRight := false
MaxToggleLeft := false

StartFishing:

PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
if (ErrorLevel == 0)
	{
	tooltip, ., %FishX%, %FishTrackHeight%, 20
	if (MaxToggleRight == true)
		{
		if (FishX < ReleaseMaxRight)
			{
			MaxToggleRight := false
			}
		sleep 10
		goto StartFishing
		}
	else if (MaxToggleLeft == true)
		{
		if (FishX > ReleaseMaxLeft)
			{
			MaxToggleLeft := false
			}
		sleep 10
		goto StartFishing
		}
	else
		{
		MaxToggleRight := false
		MaxToggleLeft := false
		PixelSearch, WhiteX, WhiteY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0xFFFFFF, %IncreaseIfCantFindWhiteBar%, Fast
		if (ErrorLevel == 0)
			{
			MaxLeftWhiteX := WhiteX
			WhiteX := (WhiteX+WhiteOffset*2)-((WhiteOffset*2)*((FishX-FishScanLeft)/(FishScanRight-FishScanLeft)))
			if ((FishX-WhiteX)>0)
				{
				tooltip, Direction: >, tooltipSide, tooltip6, 6
				tooltip, >, %WhiteX%, %FishTrackHeight%, 19
				Difference := (FishX-WhiteX)*ResolutionScaling*(150/WhiteOffset)
				send {lbutton down}
				Difference := Difference*StableRightMultiplier
				if (Difference < MinimumDifferenceAllowed)
				Difference := MinimumDifferenceAllowed
				if (Difference > MaximumStableDifferenceAllowed)
				Difference := MaximumStableDifferenceAllowed
				tooltip, Hold: %Difference%ms, tooltipSide, tooltip7, 7
				tooltip, Release: 0ms, tooltipSide, tooltip8, 8
				sleep %Difference%
				PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
				if (FishX > TriggerMaxRight)
					{
					tooltip, >, %ReleaseMaxRight%, %FishTrackHeight%, 19
					tooltip, Direction: Maximum >>>, tooltipSide, tooltip6, 6
					tooltip, Hold: %MaxHoldDuration%ms, tooltipSide, tooltip7, 7
					tooltip, Release: 0ms, tooltipSide, tooltip8, 8
					MaxToggleRight := true
					MaxToggleLeft := false
					sleep %MaxHoldDuration%
					goto StartFishing
					}
				send {lbutton up}
				Difference := Difference/StableRightDivision
				tooltip, Hold: 0ms, tooltipSide, tooltip7, 7
				tooltip, Release: %Difference%ms, tooltipSide, tooltip8, 8
				sleep %Difference%
				goto StartFishing
				}
			else
				{
				tooltip, Direction: <, tooltipSide, tooltip6, 6
				tooltip, <, %WhiteX%, %FishTrackHeight%, 19
				Difference := (WhiteX-FishX)*ResolutionScaling*(150/WhiteOffset)
				send {lbutton up}
				Difference := Difference*StableLeftMultiplier
				if (Difference < MinimumDifferenceAllowed)
				Difference := MinimumDifferenceAllowed
				if (Difference > MaximumStableDifferenceAllowed)
				Difference := MaximumStableDifferenceAllowed
				tooltip, Hold: 0ms, tooltipSide, tooltip7, 7
				tooltip, Release: %Difference%m, tooltipSide, tooltip8, 8
				sleep %Difference%
				PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
				if (FishX < TriggerMaxLeft)
					{
					tooltip, <, %ReleaseMaxLeft%, %FishTrackHeight%, 19
					tooltip, Direction: Maximum <<<, tooltipSide, tooltip6, 6
					tooltip, Hold: 0ms, tooltipSide, tooltip7, 7
					tooltip, Release: %MaxReleaseDuration%ms, tooltipSide, tooltip8, 8
					MaxToggleLeft := true
					MaxToggleRight := false
					sleep %MaxReleaseDuration%
					goto StartFishing
					}
				send {lbutton down}
				Difference := Difference/StableLeftDivision
				tooltip, Hold: %Difference%ms, tooltipSide, tooltip7, 7
				tooltip, Release: 0m, tooltipSide, tooltip8, 8
				sleep %Difference%
				send {lbutton up}
				goto StartFishing
				}
			}
		else
			{
			PixelSearch, ArrowX, ArrowY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %IncreaseIfCantFindArrow%, Fast
			if (ErrorLevel == 0)
				{
				if ((FishX-ArrowX) > 0)
					{
					Temporary := FishX-WhiteOffset
					tooltip, >, %Temporary%, %FishTrackHeight%, 19
					tooltip, Direction: >>>, tooltipSide, tooltip6, 6
					send {lbutton down}
					Difference := UnstableMovementDuration*UnstableRightMultiplier*ResolutionScaling*(150/WhiteOffset)
					if (Difference > MaximumUnstableDifferenceAllowed)
					Difference := MaximumUnstableDifferenceAllowed
					tooltip, Hold: %Difference%ms, tooltipSide, tooltip7, 7
					tooltip, Release: 0ms, tooltipSide, tooltip8, 8
					sleep %Difference%
					PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
					if (FishX > TriggerMaxRight)
						{
						tooltip, >, %ReleaseMaxRight%, %FishTrackHeight%, 19
						tooltip, Direction: Maximum >>>, tooltipSide, tooltip6, 6
						tooltip, Hold: %MaxHoldDuration%ms, tooltipSide, tooltip7, 7
						tooltip, Release: 0ms, tooltipSide, tooltip8, 8
						MaxToggleRight := true
						MaxToggleLeft := false
						sleep %MaxHoldDuration%
						goto StartFishing
						}
					send {lbutton up}
					Difference := Difference/UnstableRightDivision
					tooltip, Hold: 0ms, tooltipSide, tooltip7, 7
					tooltip, Release: %Difference%ms, tooltipSide, tooltip8, 8
					sleep %Difference%
					goto StartFishing
					}
				else
					{
					Temporary := FishX+WhiteOffset
					tooltip, <, %Temporary%, %FishTrackHeight%, 19
					tooltip, Direction: <<<, tooltipSide, tooltip6, 6
					send {lbutton up}
					Difference := UnstableMovementDuration*UnstableLeftMultiplier*ResolutionScaling*(150/WhiteOffset)
					if (Difference > MaximumUnstableDifferenceAllowed)
					Difference := MaximumUnstableDifferenceAllowed
					tooltip, Hold: 0ms, tooltipSide, tooltip7, 7
					tooltip, Release: %Difference%ms, tooltipSide, tooltip8, 8
					sleep %Difference%
					PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
					if (FishX < TriggerMaxLeft)
						{
						tooltip, <, %ReleaseMaxLeft%, %FishTrackHeight%, 19
						tooltip, Direction: Maximum <<<, tooltipSide, tooltip6, 6
						tooltip, Hold: 0ms, tooltipSide, tooltip7, 7
						tooltip, Release: %MaxReleaseDuration%ms, tooltipSide, tooltip8, 8
						MaxToggleLeft := true
						MaxToggleRight := false
						sleep %MaxReleaseDuration%
						goto StartFishing
						}
					send {lbutton down}
					Difference := Difference/UnstableLeftDivision
					tooltip, Hold: %Difference%ms, tooltipSide, tooltip7, 7
					tooltip, Release: 0ms, tooltipSide, tooltip8, 8
					sleep %Difference%
					send {lbutton up}
					goto StartFishing
					}
				}
			else
				{
				sleep %FailScanDelay%
				goto StartFishing
				}
			}
		}
	}
else
	{
	tooltip, , , , 6
	tooltip, , , , 7
	tooltip, , , , 8
	tooltip, , , , 9
	tooltip, , , , 19
	tooltip, , , , 20
	goto StartMacro
	}
return

;==================================================================================================

;PixelSearch, FishX, FishY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
;PixelSearch, WhiteX, WhiteY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0xFFFFFF, %IncreaseIfCantFindWhiteBar%, Fast
;PixelSearch, ArrowX, ArrowY, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %IncreaseIfCantFindArrow%, Fast