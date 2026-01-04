#ifWinActive, Roblox
setkeydelay, 0
setmousedelay, 0

;===============    Settings    ====================;

; how fast the rod moves
Sensitivity := 100

; how long to wait after fish is caught or lost
RecastDelay := 2000

; how long to hold for when casting rod
HoldCastDuration := 500

; so your shake doesnt bug out and stall
ShakeDelay := 20

; how many seconds for failsafe
FailsafeVariable := 12

; for different keyboard formats
NavigationKey := "\"

;===================================================;

; dont touch these
FishPixelRange := 0
ArrowPixelRange := 0
ScanDelay := 100
TheOtherScanDelay := 5
DistanceDivisionFactor := 3

;===================================================;

EndShakeScanLeft := A_ScreenWidth/2.0078
EndShakeScanRight := A_ScreenWidth/1.9922
EndShakeScanTop := A_ScreenHeight/1.1842
EndShakeScanBottom := A_ScreenHeight/1.1501

FishScanLeft := A_ScreenWidth/3.3464
FishScanRight := A_ScreenWidth-FishScanLeft
FishScanTop := EndShakeScanTop
FishScanBottom := EndShakeScanBottom

FishTrackHeight := A_ScreenHeight/1.0397
ResolutionScaling := 2560/A_ScreenWidth
InversedResolutionScaling := A_ScreenWidth/2560

;===================================================;

tooltipSide := A_ScreenWidth/20
tooltipSpacing := A_ScreenHeight/70
tooltip1 := A_ScreenHeight/3+(tooltipSpacing*1)
tooltip2 := A_ScreenHeight/3+(tooltipSpacing*2)
tooltip3 := A_ScreenHeight/3+(tooltipSpacing*3)
tooltip4 := A_ScreenHeight/3+(tooltipSpacing*4)
tooltip5 := A_ScreenHeight/3+(tooltipSpacing*5)
tooltip6 := A_ScreenHeight/3+(tooltipSpacing*6)
tooltip7 := A_ScreenHeight/3+(tooltipSpacing*7)
tooltip8 := A_ScreenHeight/3+(tooltipSpacing*8)
tooltip9 := A_ScreenHeight/3+(tooltipSpacing*9)
tooltip10 := A_ScreenHeight/3+(tooltipSpacing*10)
tooltip11 := A_ScreenHeight/3+(tooltipSpacing*11)
tooltip12 := A_ScreenHeight/3+(tooltipSpacing*12)
tooltip13 := A_ScreenHeight/3+(tooltipSpacing*13)
tooltip14 := A_ScreenHeight/3+(tooltipSpacing*14)
tooltip15 := A_ScreenHeight/3+(tooltipSpacing*15)
tooltip16 := A_ScreenHeight/3+(tooltipSpacing*16)
tooltip17 := A_ScreenHeight/3+(tooltipSpacing*17)
tooltip18 := A_ScreenHeight/3+(tooltipSpacing*18)
tooltip19 := A_ScreenHeight/3+(tooltipSpacing*19)
tooltip20 := A_ScreenHeight/3+(tooltipSpacing*20)

;===================================================;

tooltip, Made By AsphaltCake, tooltipSide, tooltip1, 1
tooltip, Press "P" to start, tooltipSide, tooltip3, 3

$o::
reload
return

$p::

Reset:

tooltip, Made By AsphaltCake, tooltipSide, tooltip1, 1
tooltip, Press "O" to reload, tooltipSide, tooltip3, 3

send {lbutton down}
NavigationStatus = false
sleep %HoldCastDuration%
send {lbutton up}
sleep 10

send {%NavigationKey% down}
sleep 10
send {%NavigationKey% up}
sleep 100

count := 0
Failed = false
settimer, FailSafeTimer, 1000
ShakeStart:

PixelSearch, xxx, yyy, EndShakeScanLeft, EndShakeScanTop, EndShakeScanRight, EndShakeScanBottom, 0x5B4B43, %FishPixelRange%, Fast
if (ErrorLevel = 0)
	{
	PixelSearch, xx, yy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %FishPixelRange%, Fast
		if (ErrorLevel = 0)
		{
		Offset := xxx-xx
		MaxLeft := FishScanLeft+Offset*2
		MaxRight := FishScanRight-Offset*2
		goto ShakeEnd
		}
		else
		{
		goto ShakeStart
		}
	}
send {s down}
sleep %ShakeDelay%
send {s up}
sleep %ShakeDelay%
send {enter down}
sleep %ShakeDelay%
send {enter up}
sleep %ShakeDelay%

if Failed = true
{
goto Reset
settimer, FailSafeTimer, off
}
goto ShakeStart
ShakeEnd:
settimer, FailSafeTimer, off

settimer, Scanner, %ScanDelay%
Direction = 2
FishFound = false
ForceLeft = false
ForceRight = false
BarStart:
if FishFound = true
goto BarEnd
sleep %TheOtherScanDelay%
if Direction = 1
	{
	ForceLeft = false
	ForceRight = false
	send {lbutton up}
	hold = false
	DifferenceSensitivity := Sensitivity+(Difference*ResolutionScaling/DistanceDivisionFactor)
	tooltip, DifferenceSensitivity: %DifferenceSensitivity%, tooltipSide, tooltip5, 5
	D2 = false
	if D1 = false
		{
		D1 = true
		sleep %DifferenceSensitivity%
		}
	sleep %DifferenceSensitivity%
	send {lbutton down}
	hold = true
	sleep %Sensitivity%
	send {lbutton up}
	hold = false
	goto BarStart
	}
else if Direction = 2
	{
	ForceLeft = false
	ForceRight = false
	send {lbutton down}
	hold = true
	DifferenceSensitivity := Sensitivity+(Difference*ResolutionScaling/DistanceDivisionFactor)
	tooltip, DifferenceSensitivity: %DifferenceSensitivity%, tooltipSide, tooltip5, 5
	D1 = false
	if D2 = false
		{
		D2 = true
		sleep %DifferenceSensitivity%
		}
	sleep %DifferenceSensitivity%
	send {lbutton up}
	hold = false
	sleep %Sensitivity%
	goto BarStart
	}
else if Direction = 3
	{
	ForceRight = false
	if ForceLeft = false
		{
		ForceLeft = true
		send {lbutton up}
		hold = false
		sleep 1300
		}
	goto BarStart
	}
else if Direction = 4
	{
	ForceLeft = false
	if ForceRight = false
		{
		ForceRight = true
		send {lbutton down}
		hold = true
		sleep 1300
		}
	goto BarStart
	}
goto BarStart
BarEnd:

sleep %RecastDelay%
goto Reset
return

Scanner:
PixelSearch, xxx, yyy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x5B4B43, %FishPixelRange%, Fast
if (ErrorLevel = 0)
	{
	tooltip, ., %xxx%, %FishTrackHeight%, 20
	PixelSearch, xx, yyy, FishScanLeft, FishScanTop, FishScanRight, FishScanBottom, 0x878584, %FishPixelRange%, Fast
	if (ErrorLevel = 0)
		{
		if hold = false
			{
			xx := xx+offset
			}
		else
			{
			xx := xx-offset
			}
		if (xxx < MaxLeft)
			{
			Direction = 3
			tooltip, <, %MaxLeft%, %FishTrackHeight%, 19
			return
			}
		if (xxx > MaxRight)
			{
			Direction = 4
			tooltip, >, %MaxRight%, %FishTrackHeight%, 19
			return
			}
		Difference := xxx-xx
		if Difference > 0
			{
			Direction = 2
			Difference := xxx-xx
			tooltip, Difference: %Difference%, tooltipSide, tooltip4, 4
			tooltip, >, %xx%, %FishTrackHeight%, 19
			}
		else
			{
			Direction = 1
			Difference := xx-xxx
			tooltip, Difference: %Difference%, tooltipSide, tooltip4, 4
			tooltip, <, %xx%, %FishTrackHeight%, 19
			}
		}
	}
else
	{
	FishFound = true
	settimer, Scanner, off
	return
	}
return

FailSafeTimer:
count++
tooltip, FailSafe: %count%/%FailsafeVariable%, tooltipSide, tooltip4, 4
if count >= %FailsafeVariable%
Failed = true
return








