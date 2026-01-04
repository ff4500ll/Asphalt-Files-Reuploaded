#ifWinActive, Roblox
#SingleInstance Force
setkeydelay, 0
setmousedelay, 0

;==============    General Settings    =============;;===================================================;;===================================================;;===================================================;

RecastRodDelay := 2000
RodThrowDelay := 500

;==============    Shake Settings    ===============;;===================================================;;===================================================;;===================================================;

; maximum time in seconds before reset (failsafe)
SecondMax := 20
FishBarTolerance := 0

; if you prefer UI navigation method
NavigationShake := true
NavigationKey := "\"
NavigationDelay := 10

; if you prefer clicking the circles method
ClickShake := false
ClickShakeTolerance := 1
ClickShakeDelay := 1
RetryClickDelay := 50
RetryClickCount := 10

;===========    Bar Minigame Settings    ===========;;===================================================;;===================================================;;===================================================;

; this is v6 reeling mechanics (new one)
ModernMode := true
WhiteBarTolerance := 20
MaxSideWait := 500
HalfSideMode := true

; this is just v3 code 1:1 for those who preferred it (old one)
LegacyMode := false
Strength := 1.2
Stability := 0.8
HoldBypassMultiplier := 1.3
ReleaseBypassMultiplier := 1.1
BarSizeMultiplier := 1
BarTrackTolerance := 5

;===================================================;;===================================================;;===================================================;;===================================================;

if (ClickShake == true and NavigationShake == true)
	{
	MsgBox, Disable ClickShake or NavigationShake (dont set both to true)
	exitapp
	}
else if (ClickShake == false and NavigationShake == false)
	{
	MsgBox, Enable ClickShake or NavigationShake (dont set both to false)
	exitapp
	}
if (ModernMode == true and LegacyMode == true)
	{
	MsgBox, Disable ModernMode or LegacyMode (dont set both to true)
	exitapp
	}
else if (ModernMode == false and LegacyMode == false)
	{
	MsgBox, Enable ModernMode or LegacyMode (dont set both to false)
	exitapp
	}

;===================================================;;===================================================;;===================================================;;===================================================;

EndShakeScanLeft := A_ScreenWidth/2.0078
EndShakeScanRight := A_ScreenWidth/1.9922
EndShakeScanTop := A_ScreenHeight/1.1842
EndShakeScanBottom := A_ScreenHeight/1.1501

ShakeLeft := A_ScreenWidth/4.1967
ShakeRight := A_ScreenWidth/1.3128
ShakeTop := A_ScreenHeight/4.4307
ShakeBottom := A_ScreenHeight/1.3211

SmallNumbering := A_ScreenWidth/94.8148
BalanceBarLeft := A_ScreenWidth/3.3246
BalanceBarRight := A_ScreenWidth-(A_ScreenWidth/3.3246)
BalanceBarTop := A_ScreenHeight/1.1774
BalanceBarBottom := A_ScreenHeight/1.1492

FishScanLeft := A_ScreenWidth/3.3464
FishScanRight := A_ScreenWidth-FishScanLeft
FishScanTop := EndShakeScanTop
FishScanBottom := EndShakeScanBottom

FishTrackHeight := A_ScreenHeight/1.0397
ResolutionScaling := 2560/A_ScreenWidth
InversedResolutionScaling := A_ScreenWidth/2560

RightMultiplier := RightMultiplier*SteadyDelay
LeftMultiplier := LeftMultiplier*SteadyDelay

;===================================================;;===================================================;;===================================================;;===================================================;

tooltipSide := A_ScreenWidth/20
tooltipSpacing := A_ScreenHeight/70
tooltip1 := A_ScreenHeight/3+20
tooltip, Made By AsphaltCake, tooltipSide, tooltip1, 1
tooltip2 := A_ScreenHeight/3+60
tooltip, Press "P" To Start, tooltipSide, tooltip2, 2
tooltip3 := A_ScreenHeight/3+100
tooltip, Enable Fullscreen Mode, tooltipSide, tooltip3, 3

if (ClickShake == false)
	{
	tooltip4 := A_ScreenHeight/3+120
	tooltip, Enable Camera Mode (top right), tooltipSide, tooltip4, 4
	tooltip5 := A_ScreenHeight/3+140
	tooltip, Disable Higher Brightness (press m for menu), tooltipSide, tooltip5, 5
	tooltip6 := A_ScreenHeight/3+160
	tooltip, Disable Higher Saturation (press m for menu), tooltipSide, tooltip6, 6
	tooltip7 := A_ScreenHeight/3+180
	tooltip, Hold Your Fishing Rod, tooltipSide, tooltip7, 7
	tooltip8 := A_ScreenHeight/3+220
	tooltip, Shake Mode: UI Navigation, tooltipSide, tooltip8, 8
	tooltip9 := A_ScreenHeight/3+240
	tooltip, Key: %NavigationKey%, tooltipSide, tooltip9, 9
	if (LegacyMode == false)
		{
		tooltip10 := A_ScreenHeight/3+280
		tooltip, Minigame Mode: Modern, tooltipSide, tooltip10, 10
		}
	else
		{
		tooltip10 := A_ScreenHeight/3+280
		tooltip, Minigame Mode: Legacy, tooltipSide, tooltip10, 10
		}
	}
else
	{
	tooltip4 := A_ScreenHeight/3+120
	tooltip, Disable Higher Brightness (press m for menu), tooltipSide, tooltip4, 4
	tooltip5 := A_ScreenHeight/3+140
	tooltip, Disable Higher Saturation (press m for menu), tooltipSide, tooltip5, 5
	tooltip6 := A_ScreenHeight/3+160
	tooltip, Hold Your Fishing Rod, tooltipSide, tooltip6, 6
	tooltip7 := A_ScreenHeight/3+200
	tooltip, Shake Mode: Click, tooltipSide, tooltip7, 7
	if (LegacyMode == false)
		{
		tooltip9 := A_ScreenHeight/3+240
		tooltip, Minigame Mode: Modern, tooltipSide, tooltip9, 9
		}
	else
		{
		tooltip9 := A_ScreenHeight/3+240
		tooltip, Minigame Mode: Legacy, tooltipSide, tooltip9, 9
		}
	}

;===================================================;;===================================================;;===================================================;;===================================================;;

$n::
send {lbutton down}
sleep 2000
send {lbutton up}
sleep 425
send {lbutton down}
sleep 425
loop,
{
send {lbutton down}
sleep 10
send {lbutton up}
sleep 10
}
return

$o:: reload
return

$p::
tooltip, Press "O" To Reload, tooltipSide, tooltip2, 2
tooltip, , , , 3
tooltip, , , , 4
tooltip, , , , 5
tooltip, , , , 6
tooltip, , , , 7
tooltip, , , , 8
tooltip, , , , 9
tooltip, , , , 10

;===================================================;;===================================================;;===================================================;;===================================================;

ResetLoop:
SecondCount := 0
ForceReset := false

send {lbutton down}
sleep %RodThrowDelay%
send {lbutton up}
goto ClickShakeStart

;===================================================;;===================================================;;===================================================;;===================================================;

ClickShakeStart:
if (ClickShake == true)
	{
	settimer, SecondCounter, 1000
	goto ClickShakeMethod
	}
else
	{
	settimer, SecondCounter, 1000
	send {%NavigationKey% down}
	sleep 100
	send {%NavigationKey% up}
	sleep 250
	goto NavigationShakeMethod
	}

;===================================================;;===================================================;;===================================================;;===================================================;

ClickShakeMethod:
if (ForceReset == true)
{
goto ResetLoop
}
PixelSearch, xxx, yyy, EndShakeScanLeft, EndShakeScanTop, EndShakeScanRight, EndShakeScanBottom, 0x5B4B43, %FishBarTolerance%, Fast
if (ErrorLevel == 0)
	{
	settimer, MiliSecondCounter, off
	goto EndShake
	}
PixelSearch, ShakeX, ShakeY, ShakeLeft, ShakeTop, ShakeRight, ShakeBottom, 0xFFFFFF, %ClickShakeTolerance%, Fast
if (ErrorLevel == 0)
	{
	if (AllowBypass == true)
	goto ShakeSkip
	if (ShakeX == OldShakeX or ShakeY == OldShakeY)
		{
		if (MiliToggle == false)
			{
			MiliCount := 0
			MiliMax := RetryClickCount
			MiliToggle := true
			settimer, MiliSecondCounter, %RetryClickDelay%
			}
		goto ClickShakeMethod
		}
	ShakeSkip:
	AllowBypass := false
	settimer, MiliSecondCounter, off
	MiliToggle := false
	mousemove, %ShakeX%, %ShakeY%
	sleep %ClickShakeDelay%
	send {click}
	OldShakeX := ShakeX
	OldShakeY := ShakeY
	goto ClickShakeMethod
	}
else
	{
	goto ClickShakeMethod
	}

;===================================================;;===================================================;;===================================================;;===================================================;

NavigationShakeMethod:
if (ForceReset == true)
{
goto ResetLoop
}
PixelSearch, xxx, yyy, EndShakeScanLeft, EndShakeScanTop, EndShakeScanRight, EndShakeScanBottom, 0x5B4B43, %FishBarTolerance%, Fast
if (ErrorLevel == 0)
	{
	settimer, SecondCounter, off
	goto EndShake
	}
else
	{
	send {s down}
	sleep %NavigationDelay%
	send {s up}
	sleep %NavigationDelay%
	send {enter down}
	sleep %NavigationDelay%
	send {enter up}
	sleep %NavigationDelay%
	goto NavigationShakeMethod
	}

;===================================================;;===================================================;;===================================================;;===================================================;

EndShake:
settimer, SecondCounter, off
tooltip, , , , 3
if (LegacyMode == true)
	{
	goto LegacyBarMode
	}
else
	{
	pleaseniggawork:
	PixelSearch, xx, yy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0xFFFFFF, %WhiteBarTolerance%, Fast
	if (ErrorLevel == 0)
		{
		Offset := xxx-xx
		if (HalfSideMode == true)
			{
			ModernMaxLeft := FishScanLeft+Offset
			ModernMaxRight := FishScanRight-Offset
			}
		else
			{
			ModernMaxLeft := FishScanLeft+Offset*2
			ModernMaxRight := FishScanRight-Offset*2
			}
		goto ModernBarMode
		}
	else
		{
		goto pleaseniggawork
		}
	}

;===================================================;;===================================================;;===================================================;;===================================================;

LegacyBarMode:
toggle = false
finalcount := 0
barsizecount := 0

tooltip, Current Task: Balancing The Bar, tooltipside, tooltip3, 3
LegacyBarBalance:
sleep 10
PixelSearch, xxx, yyy, BalanceBarLeft, BalanceBarTop, BalanceBarRight, BalanceBarBottom, 0x5B4B43, %BarTrackTolerance%, Fast
if (ErrorLevel == 0)
{
tooltip, Found Bar, tooltipside, tooltip4, 4
tooltip, Bar: %xxx%, tooltipside, tooltip5, 5
PixelSearch, xx, yy, BalanceBarLeft, BalanceBarTop, BalanceBarRight, BalanceBarBottom, 0x878584, %BarTrackTolerance%, Fast
if (ErrorLevel == 0)
{
if (barsizecount < 5)
{
	barsizecount++
	MaxLeft := BalanceBarLeft+(((xxx-xx+SmallNumbering)*2)*BarSizeMultiplier)
	MaxRight := BalanceBarRight-(((xxx-xx+SmallNumbering)*2)*BarSizeMultiplier)
	tooltip, Calculating Bar Size: %barsizecount%/5, tooltipside, tooltip6, 6
	sleep 100
	goto LegacyBarBalance
	}
	if (xxx > MaxRight)
		{
		if toggle = false
		{
		tooltip, Max Right, tooltipside, tooltip7, 7
		send {lbutton down}
		toggle = true
		}
		goto LegacyBarBalance
		}
	toggle = false
	if (xxx < MaxLeft)
		{
		tooltip, Max Left, tooltipside, tooltip7, 7
		send {lbutton up}
		goto LegacyBarBalance
		}
	tooltip, Arrow: %xx%, tooltipside, tooltip6, 6
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
				tooltip, Moving Bar Right (%Difference%), tooltipside, tooltip7, 7
				Difference := Difference * Strength * HoldBypassMultiplier
				send {lbutton down}
				sleep %Difference%
				Difference := Difference * Stability
				send {lbutton up}
				sleep %Difference%
				}
				else
				{
				tooltip, Moving Bar Left (%Difference%), tooltipside, tooltip7, 7
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
	tooltip, Bar Lost, tooltipside, tooltip4, 4
	tooltip, Arrow Lost, tooltipside, tooltip5, 5
	}
}
else
{
tooltip, Bar Lost, tooltipside, tooltip3, 3
tooltip, Bar Lost, tooltipside, tooltip4, 4
finalcount++
sleep 100
if finalcount > 5
goto EndBar
goto LegacyBarBalance
}
goto LegacyBarBalance

;===================================================;;===================================================;;===================================================;;===================================================;

ModernBarMode:

ToggleOnce := false
GoingLeft := false
GoingRight := false
MinigameComplete := false

LeftStableScaling := 5
LeftStableBiasDivision := 2

RightStableScaling := 1.5
RightStableBiasDivision := 2

LeftUnstableScaling := 3
LeftUnstableBiasDivision := 2

RightUnstableScaling := 3
RightUnstableBiasDivision := 2

RightOffsetBias := 0.3

RightOffsetBias := RightOffsetBias*Offset

ModernBarBalance:
PixelSearch, xxx, yyy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, 0, Fast
if (ErrorLevel == 0)
	{
	tooltip, ., %xxx%, %FishTrackHeight%, 20
	if (xxx < ModernMaxLeft)
		{
		if (ToggleOnce == false)
			{
			GoingRight := false
			ToggleOnce := true
			send {lbutton up}
			sleep %MaxSideWait%
			}
		sleep 10
		tooltip, <, %ModernMaxLeft%, %FishTrackHeight%, 19
		}
	else if (xxx > ModernMaxRight)
		{
		if (ToggleOnce == false)
			{
			GoingLeft := false
			ToggleOnce := true
			send {lbutton down}
			sleep %MaxSideWait%
			}
		sleep 10
		tooltip, >, %ModernMaxRight%, %FishTrackHeight%, 19
		}
	else
		{
		ToggleOnce := false
		PixelSearch, xx, yy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0xFFFFFF, %WhiteBarTolerance%, Fast
		if (ErrorLevel == 0)
			{
			xx := xx+RightOffsetBias
			Difference := (xxx-xx)*RightStableScaling*ResolutionScaling
			if (Difference >= 0)
				{
				if (Difference < 10)
					Difference := 10
				tooltip, >, %xx%, %FishTrackHeight%, 19
				send {lbutton down}
				Difference := Difference
				sleep %Difference%
				send {lbutton up}
				Difference := Difference/RightStableBiasDivision
				sleep %Difference%
				GoingRight := true
				if (GoingLeft == true)
					{
					GoingLeft := false
					sleep %Difference%
					}				
				}
			else
				{
				Difference := (xx-xxx)*LeftStableScaling*ResolutionScaling
				if (Difference < 10)
					Difference := 10
				else if (Difference > Offset)
					Difference := Offset
				tooltip, <, %xx%, %FishTrackHeight%, 19
				send {lbutton up}
				Difference := Difference
				sleep %Difference%
				send {lbutton down}
				Difference := Difference/LeftStableBiasDivision
				sleep %Difference%
				GoingLeft := true
				if (GoingRight == true)
					{
					GoingRight := false
					sleep %Difference%
					}
				}
			}
		else
			{
			PixelSearch, xx, yy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, 0, Fast
			if (ErrorLevel == 0)
				{
				difference := xxx-xx
				if (difference < 0)
					{
					tooltipcoords := xxx+Offset
					tooltip, <, %tooltipcoords%, %FishTrackHeight%, 19
					send {lbutton up}
					Difference := Offset*ResolutionScaling*RightUnstableScaling
					sleep %Difference%
					Difference := Difference/LeftUnstableBiasDivision
					send {lbutton down}
					sleep %Difference%
					}
				else
					{
					tooltipcoords := xxx-Offset
					tooltip, >, %tooltipcoords%, %FishTrackHeight%, 19
					send {lbutton down}
					Difference := Offset*ResolutionScaling*LeftUnstableScaling
					sleep %Difference%
					send {lbutton up}
					Difference := Difference/RightUnstableBiasDivision
					sleep %Difference%
					}
				}
			}		
		}
	}
else
	{
	tooltip, , , , 19
	tooltip, , , , 20
	send {lbutton up}
	goto EndBar
	}
goto ModernBarBalance

;===================================================;;===================================================;;===================================================;;===================================================;

EndBar:
tooltip, Resetting, tooltipside, tooltip3, 3
tooltip, , , , 4
tooltip, , , , 5
tooltip, , , , 6
tooltip, , , , 7
tooltip, , , , 8
tooltip, , , , 9
tooltip, , , , 10
sleep %RecastRodDelay%
goto ResetLoop

;===================================================;;===================================================;;===================================================;;===================================================;

MiliSecondCounter:
MiliCount++
if (MiliCount > MiliMax)
	{
	settimer, MiliSecondCounter, off
	AllowBypass := true
	}
return

SecondCounter:
SecondCount++
tooltip, FailSafe: %SecondCount%/%SecondMax%, tooltipSide, tooltip3, 3
if (SecondCount >= SecondMax)
	{
	settimer, SecondCounter, off
	ForceReset := true
	}
return

;===================================================;;===================================================;;===================================================;;===================================================;