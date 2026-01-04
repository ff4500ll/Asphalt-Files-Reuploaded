#ifWinActive, Roblox
#SingleInstance Force
setkeydelay, 0
setmousedelay, 0
CoordMode, Tooltip, Screen
CoordMode, Pixel, Screen
CoordMode, Mouse, Screen

;======    General Settings    ===================================================================;

; How long to wait after fishing before recasting the rod
RodRecastDelay := 2000

; How long to hold the cast for before releasing
HoldRodCastDuration := 500

; How long to wait for the bobber to land in water
WaitForBobberDelay := 1000

;======    Shake Settings    =====================================================================;

; Change To "Navigation" or "Click"
ShakeMode := "Navigation"
WhiteBarColorTolerance := 15
FishBarColorTolerance := 0

; Navigation UI Settings
NavigationKey := "\"
NavigationFailsafeTimer := 20
NavigationInputDelay := 10

; Click Circle Settings
ClickFailsafeTimer := 20
WhiteCircleColorTolerance := 1
ClickDelayAfterMouseMove := 10
RescanDelayAfterClick := 50
DelayIfFailedClick := 200

;======    Bar Minigame Settings    ==============================================================;

AutoBarSizeMultiplier := true
RightBiasedStableMode := false

IncreaseIfCantFindWhiteBar := 15
IncreaseIfCantFindFishBar := 2
IncreaseIfCantFindArrow := 4

StableLowestDelay := 10
StableHighestDelay := 300
RightStableMultiplier := 1.5
RightStableDivision := 3
LeftStableMultiplier := 1
LeftStableDivision := 1.1

UnstableHighestDelay := 600
RightUnstableMultiplier := 2.4
RightUnstableDivision := 1.4
LeftUnstableMultiplier := 2.4
LeftUnstableDivision := 1.3

MaxHoldDuration := 1000
MaxReleaseDuration := 700

;==================================================================================================

if (ShakeMode != "Navigation" and ShakeMode != "Click")
	{
	MsgBox, %ShakeMode% is invalid, use Navigation or Click
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

;==================================================================================================

tooltip, Made By AsphaltCake, tooltipSide, tooltip1, 1
tooltip, Press "P" To Begin, tooltipSide, tooltip3, 3
tooltip, Press "M" To Exit Script, tooltipSide, tooltip4, 4
tooltip, HOLD YOUR FISHING ROD, tooltipSide, tooltip6, 6
tooltip, Disable Higher Saturation (press m), tooltipSide, tooltip7, 7
tooltip, Disable Higher Brightness (press m), tooltipSide, tooltip8, 8
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
	
;==================================================================================================

$o:: reload
return
$m:: exitapp
return
$p::
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

tooltip, Made By AsphaltCake, tooltipSide, tooltip1, 1
tooltip, Press "O" To Reload, tooltipSide, tooltip3, 3
tooltip, Press "M" To Exit Script, tooltipSide, tooltip4, 4

goto StartMacro
return

;==================================================================================================

StartMacro:
tooltip, Casting Rod For %HoldRodCastDuration%ms, tooltipSide, tooltip6, 6
send {lbutton down}
sleep %HoldRodCastDuration%
send {lbutton up}
if (ShakeMode == "Navigation")
	{
	goto ShakeNavigationMode
	}
else if (ShakeMode == "Click")
	{
	goto ShakeClickMode
	}
	
;==================================================================================================

ShakeNavigationMode:
tooltip, Enabling Navigation Mode, tooltipSide, tooltip6, 6
send {%NavigationKey% up}
sleep 250
send {%NavigationKey% down}
sleep 250
send {%NavigationKey% up}
sleep %WaitForBobberDelay%
NavigationCounter := 0
NavigationForceReset := false
tooltip, FailSafe: 0/%NavigationFailsafeTimer%, tooltipSide, tooltip6, 6
settimer, NavigationTimerFailsafe, 1000
ShakeNavigationLoop:
if (NavigationForceReset == true)
	{
	send {%NavigationKey% down}
	sleep 250
	send {%NavigationKey% up}
	sleep %RodRecastDelay%
	tooltip, Waiting %RodRecastDelay%ms, tooltipSide, tooltip6, 6
	goto StartMacro
	}
else
	{
	PixelSearch, xxx, yyy, EndShakeScanLeft, EndShakeScanTop, EndShakeScanRight, EndShakeScanBottom, 0x5B4B43, %FishBarColorTolerance%, Fast
	if (ErrorLevel == 0)
		{
		NavigationWhiteRescan:
		PixelSearch, xx, yy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0xFFFFFF, %WhiteBarColorTolerance%, Fast
		if (ErrorLevel == 0)
			{
			settimer, NavigationTimerFailsafe, off
			Offset := xxx-xx
			goto CompleteShaking
			}
		else
			{
			sleep 10
			goto NavigationWhiteRescan
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
		goto ShakeNavigationLoop
		}
	}
	
NavigationTimerFailsafe:
NavigationCounter++
tooltip, FailSafe: %NavigationCounter%/%NavigationFailsafeTimer%, tooltipSide, tooltip6, 6
if (NavigationCounter >= NavigationFailsafeTimer)
	{
	settimer, NavigationTimerFailsafe, off
	NavigationForceReset := true
	}
return

;==================================================================================================

ShakeClickMode:
ClickCounter := 0
ClickForceReset := false
settimer, ClickTimerFailsafe, 1000
ShakeClickLoop:
if (ClickForceReset == true)
	{
	goto StartMacro
	}
else
	{
	PixelSearch, xxx, yyy, ClickShakeLeft, ClickShakeTop, ClickShakeRight, ClickShakeBottom, 0xFFFFFF, %WhiteCircleColorTolerance%, Fast
	if (ErrorLevel == 0)
		{
		if (MemoryX == xxx and MemoryY == yyy)
			{
			sleep %DelayIfFailedClick%
			goto ShakeClickLoop
			}
		mousemove, %xxx%, %yyy%
		sleep %ClickDelayAfterMouseMove%
		send {click}
		sleep %RescanDelayAfterClick%
		MemoryX := xxx
		MemoryY := yyy
		goto ShakeClickLoop
		}
	else
		{
		PixelSearch, xxx, yyy, EndShakeScanLeft, EndShakeScanTop, EndShakeScanRight, EndShakeScanBottom, 0x5B4B43, %FishBarColorTolerance%, Fast
		if (ErrorLevel == 0)
			{
			ClickWhiteRescan:
			PixelSearch, xx, yy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0xFFFFFF, %WhiteBarColorTolerance%, Fast
			if (ErrorLevel == 0)
				{
				settimer, ClickTimerFailsafe, off
				Offset := xxx-xx
				goto CompleteShaking
				}
			else
				{
				sleep 10
				goto ClickWhiteRescan
				}
			}
		else
			{
			sleep 100
			goto ShakeClickLoop
			}
		}
	}

ClickTimerFailsafe:
ClickCounter++
tooltip, FailSafe: %ClickCounter%/%ClickFailsafeTimer%, tooltipSide, tooltip6, 6
if (ClickCounter >= ClickFailsafeTimer)
	{
	settimer, ClickTimerFailsafe, off
	ClickForceReset := true
	}
return

;==================================================================================================

CompleteShaking:

MaxToggleRight := false
MaxToggleLeft := false

if (AutoBarSizeMultiplier == true)
	{
	BarSizeDivision := 175/ResolutionScaling
	DynamicBarSizeMultipler := BarSizeDivision/Offset
	}
else
	{
	DynamicBarSizeMultipler := 1
	}

TriggerMaxSideMultiplier := 1/DynamicBarSizeMultipler
Temporary := (TriggerMaxSideMultiplier-1)/2
TriggerMaxSideMultiplier := TriggerMaxSideMultiplier+Temporary

DynamicMaxLeft := FishScanLeft+Offset
DynamicMaxRight := FishScanRight-Offset

MaxHoldDuration := MaxHoldDuration*DynamicBarSizeMultipler
MaxReleaseDuration := MaxReleaseDuration*DynamicBarSizeMultipler

tooltip, , , , 6

MinigameStart:
PixelSearch, xxx, yyy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %IncreaseIfCantFindFishBar%, Fast
if (ErrorLevel == 0)
	{
	tooltip, ., %xxx%, %FishTrackHeight%, 20
	if (xxx < DynamicMaxLeft)
		{
		DynamicMaxRight := FishScanRight-Offset*TriggerMaxSideMultiplier
		if (MaxToggleLeft == false)
			{
			DynamicMaxLeft := FishScanLeft+Offset*2
			MaxToggleLeft := true
			MaxToggleRight := false
			send {lbutton up}
			tooltip, Maximum Left, tooltipSide, tooltip6, 6
			tooltip, Maximum Left, tooltipSide, tooltip7, 7
			tooltip, <, %DynamicMaxLeft%, %FishTrackHeight%, 19
			sleep %MaxReleaseDuration%
			}
		sleep 10
		goto MinigameStart
		}
	else if (xxx > DynamicMaxRight)
		{
		DynamicMaxLeft := FishScanLeft+Offset*TriggerMaxSideMultiplier
		if (MaxToggleRight == false)
			{
			DynamicMaxRight := FishScanRight-Offset*2
			MaxToggleRight := true
			MaxToggleLeft := false
			send {lbutton down}
			tooltip, Maximum Right, tooltipSide, tooltip6, 6
			tooltip, Maximum Right, tooltipSide, tooltip7, 7
			tooltip, >, %DynamicMaxRight%, %FishTrackHeight%, 19
			sleep %MaxHoldDuration%
			}
		sleep 10
		goto MinigameStart
		}
	else
		{
		MaxToggleLeft := false
		MaxToggleRight := false
		DynamicMaxLeft := FishScanLeft+Offset
		DynamicMaxRight := FishScanRight-Offset
		PixelSearch, xx, yy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0xFFFFFF, %IncreaseIfCantFindWhiteBar%, Fast
		if (ErrorLevel == 0)
			{
			xx := xx+Offset
			Difference := xxx-xx
			if (Difference > 0)
				{
				Difference := (xxx-xx)*RightStableMultiplier*DynamicBarSizeMultipler*ResolutionScaling
				if (Difference < StableLowestDelay)
				Difference := StableLowestDelay
				if (Difference > StableHighestDelay)
				Difference := StableHighestDelay
				tooltip, >, %xx%, %FishTrackHeight%, 19
				send {lbutton down}
				tooltip, Release 0ms, tooltipSide, tooltip7, 7
				Temporary := Floor(Difference)
				tooltip, Hold %Temporary%ms, tooltipSide, tooltip6, 6
				sleep %Difference%
				send {lbutton up}
				tooltip, Hold 0ms, tooltipSide, tooltip6, 6
				Difference := Difference/RightStableDivision
				Temporary := Floor(Difference)
				tooltip, Release %Temporary%ms, tooltipSide, tooltip7, 7
				sleep %Difference%
				goto MinigameStart
				}
			else
				{
				Difference := (xx-xxx)*LeftStableMultiplier*DynamicBarSizeMultipler*ResolutionScaling
				if (Difference < StableLowestDelay)
				Difference := StableLowestDelay
				if (Difference > StableHighestDelay)
				Difference := StableHighestDelay
				tooltip, <, %xx%, %FishTrackHeight%, 19
				send {lbutton up}
				tooltip, Hold 0ms, tooltipSide, tooltip6, 6
				Temporary := Floor(Difference)
				tooltip, Release %Temporary%ms, tooltipSide, tooltip7, 7
				sleep %Difference%
				send {lbutton down}
				tooltip, Release 0ms, tooltipSide, tooltip7, 7
				Difference := Difference/LeftStableDivision
				Temporary := Floor(Difference)
				tooltip, Hold %Temporary%ms, tooltipSide, tooltip6, 6
				sleep %Difference%
				if (RightBiasedStableMode == true)
				goto MinigameStart
				send {lbutton up}
				goto MinigameStart
				}
			}
		else
			{
			PixelSearch, xx, yy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %IncreaseIfCantFindArrow%, Fast
			if (ErrorLevel == 0)
				{
				Difference := (xxx-xx)
				if (Difference > 0)
					{
					ToolTipOffset := xxx-Offset
					tooltip, >, %ToolTipOffset%, %FishTrackHeight%, 19
					Difference := Offset*RightUnstableMultiplier*DynamicBarSizeMultipler*ResolutionScaling
					if (Difference > UnstableHighestDelay)
					Difference := UnstableHighestDelay
					send {lbutton down}
					tooltip, Release 0ms, tooltipSide, tooltip7, 7
					Temporary := Floor(Difference)
					tooltip, Hold %Temporary%ms, tooltipSide, tooltip6, 6
					sleep %Difference%
					send {lbutton up}
					Difference := Difference/RightUnstableDivision
					tooltip, Hold 0ms, tooltipSide, tooltip6, 6
					Temporary := Floor(Difference)
					tooltip, Release %Temporary%ms, tooltipSide, tooltip7, 7
					sleep %Difference%
					}
				else
					{
					ToolTipOffset := xxx+Offset
					tooltip, <, %ToolTipOffset%, %FishTrackHeight%, 19
					Difference := Offset*LeftUnstableMultiplier*DynamicBarSizeMultipler*ResolutionScaling
					if (Difference > UnstableHighestDelay)
					Difference := UnstableHighestDelay
					send {lbutton up}
					tooltip, Hold 0ms, tooltipSide, tooltip6, 6
					Temporary := Floor(Difference)
					tooltip, Release %Temporary%ms, tooltipSide, tooltip7, 7
					sleep %Difference%
					send {lbutton down}
					Difference := Difference/LeftUnstableDivision
					tooltip, Release 0ms, tooltipSide, tooltip7, 7
					Temporary := Floor(Difference)
					tooltip, Hold %Temporary%ms, tooltipSide, tooltip6, 6
					sleep %Difference%
					send {lbutton up}
					}
				goto MinigameStart
				}
			else
				{
				goto MinigameStart
				}
			}
		}
	}
else
	{
	tooltip, Waiting %RodRecastDelay%ms, tooltipSide, tooltip6, 6
	tooltip, , , , 7
	tooltip, , , , 19
	tooltip, , , , 20
	sleep %RodRecastDelay%
	goto StartMacro
	}

;==================================================================================================