setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
SetTitleMatchMode 2
CurrentOrePosition := 2
xcoords := A_ScreenWidth/20
ycoords := A_ScreenHeight/1.2
ycoords2 := A_ScreenHeight/1.2+20
tooltip, Press P To Begin, xcoords, ycoords, 1
tooltip, Failsafe: Disabled, xcoords, ycoords2, 2
Process, Close, RobloxPlayerBeta.exe
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
Autosell := true
return
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
FailsafeTimer:
Timer++
Countdown := SetTimer-Timer
tooltip, Failsafe: %Countdown%, xcoords, ycoords2, 2
if (Timer > SetTimer)
	{
	Failed := true
	settimer, FailsafeTimer, off
	tooltip, Failsafe: Triggered, xcoords, ycoords2, 2
	}
return
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
DangerScan:
PixelSearch, , , DangerX1, 0, DangerX2, DangerY2, 0x00008D, 0, Fast
if (ErrorLevel == 0)
	{
	incombat := true
	Process, Close, RobloxPlayerBeta.exe
	settimer, DangerScan, off
	}
return
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
SpamE:
send {e down}
sleep 50
send {e up}
return
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
LookDown:
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", Down1)
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", Down2)
sleep 100
send {rbutton down}
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", Down1)
sleep 100
send {rbutton up}
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", Down3)
return
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
LookUp:
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", Up1)
sleep 100
send {rbutton down}
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", Up2)
sleep 100
send {rbutton up}
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", Up3)
return
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
$m:: exitapp
$p::
ForceResetStart:
xcoords := A_ScreenWidth/20
ycoords := A_ScreenHeight/1.2
ycoords2 := A_ScreenHeight/1.2+20
CenterX1 := A_ScreenWidth/3
CenterX2 := A_ScreenWidth-(A_ScreenWidth/3)
CenterY1 := A_ScreenHeight/3
CenterY2 := A_ScreenHeight-(A_ScreenHeight/3)
MiddleX := A_ScreenWidth/2
MiddleY := A_ScreenHeight/2
TopLeftX2 := A_ScreenWidth/3
TopLeftY2 := A_ScreenHeight/3
DangerX1 := A_ScreenWidth/3
DangerX2 := A_ScreenWidth-DangerX1
DangerY2 := A_ScreenHeight/4
CaveY1 := A_ScreenHeight/24
CaveY2 := A_ScreenHeight/6.2608
CaveX2 := A_ScreenWidth/3.7647
Down1 := A_ScreenHeight
Down2 := -(A_ScreenHeight/1.2)
Down3 := -(A_ScreenHeight/2)
Up1 := A_ScreenHeight
Up2 := -(A_ScreenHeight/1.2)
Up3 := A_ScreenHeight/3
tooltip, Closing Roblox, xcoords, ycoords, 1
sleep 5000
Process, Close, RobloxPlayerBeta.exe
tooltip, Closing Roblox (10s), xcoords, ycoords, 1
sleep 5000
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
Timer := 0
SetTimer := 30
Failed := false
settimer, FailsafeTimer, 1000
PlayStart:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *10 %A_ScriptDir%\Images\Play.png
if (ErrorLevel == 0)
	{
	tooltip, Starting Roblox, xcoords, ycoords, 1
	click %xxx% %yyy%
	sleep 2000
	}
else
	{
	tooltip, Failed To Start Roblox, xcoords, ycoords, 1
	sleep 2000
	if (Failed == true)
	goto ForceResetStart
	goto PlayStart
	}
settimer, FailsafeTimer, off
tooltip, Failsafe: Disabled, xcoords, ycoords2, 2
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
PressKeyToContinueStartfail:
Timer := 0
SetTimer := 30
Failed := false
settimer, FailsafeTimer, 1000
PressKeyToContinueStart:
ImageSearch, , , CenterX1, CenterY1, CenterX2, A_ScreenHeight, *50 %A_ScriptDir%\Images\PressKeyToContinue.png
if (ErrorLevel == 1)
	{
	ImageSearch, , , CenterX1, CenterY1, CenterX2, CenterY2, *50 %A_ScriptDir%\Images\Leave.png
	if (ErrorLevel == 0)
		{
		goto ForceResetStart
		}
	else
		{
		ImageSearch, , , 0, 0, A_ScreenWidth, A_ScreenHeight, *10 %A_ScriptDir%\Images\Play.png
		if (ErrorLevel == 0)
			{
			goto PlayStart
			}
		else
			{
			tooltip, Waiting For Roblox, xcoords, ycoords, 1
			sleep 500
			if (Failed == true)
			goto ForceResetStart
			goto PressKeyToContinueStart
			}
		}
	}
settimer, FailsafeTimer, off
tooltip, Failsafe: Disabled, xcoords, ycoords2, 2
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
tooltip, Enabling Fullscreen, xcoords, ycoords, 1
FullscreenStart:
Send, {F11}
sleep 250
WinGet, winStyle, Style, Roblox
if (winStyle & 0xC40000)
	{
	WinActivate
	Sleep, 250
	Send, {F11}
	}
sleep 500
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
Timer := 0
SetTimer := 30
Failed := false
settimer, FailsafeTimer, 1000
ContinueStart:
ImageSearch, xxx, yyy, CenterX1, CenterY1, CenterX2, A_ScreenHeight, *50 %A_ScriptDir%\Images\Continue.png
if (ErrorLevel == 1)
	{
	ImageSearch, , , CenterX1, CenterY1, CenterX2, A_ScreenHeight, *50 %A_ScriptDir%\Images\PressKeyToContinue.png
	if (ErrorLevel == 0)
		{
		goto PressKeyToContinueStartfail
		}
	else
		{
		tooltip, Waiting For Continue, xcoords, ycoords, 1
		sleep 500
		if (Failed == true)
		goto ForceResetStart
		goto ContinueStart
		}
	}
else
	{
	tooltip, Clicking Continue, xcoords, ycoords, 1
	click %xxx% %yyy%
	sleep 1000
	}
settimer, FailsafeTimer, off
tooltip, Failsafe: Disabled, xcoords, ycoords2, 2
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
Timer := 0
SetTimer := 30
Failed := false
settimer, FailsafeTimer, 1000
SlotStart:
ImageSearch, xxx, yyy, CenterX1, 0, CenterX2, CenterY2, *50 %A_ScriptDir%\Images\Slot.png
if (ErrorLevel == 1)
	{
	ImageSearch, , , CenterX1, 0, CenterX2, CenterY2, *50 %A_ScriptDir%\Images\QuickJoin.png
	if (ErrorLevel == 1)
		{
		goto ForceResetStart
		}
	}
else	
	{
	tooltip, Selecting Slot, xcoords, ycoords, 1
	click %xxx% %yyy%
	sleep 2000
	if (Failed == true)
	goto ForceResetStart
	goto SlotStart
	}
settimer, FailsafeTimer, off
tooltip, Failsafe: Disabled, xcoords, ycoords2, 2
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
RandomServerStart:
mousemove, MiddleX, MiddleY
Random, randNum, 20, 50
tooltip, Random Scrolling (%randNum%), xcoords, ycoords, 1
loop, %randNum%
	{
	send {wheeldown}
	sleep 5
	}
loop, 10
	{
	tooltip, Joining Server, xcoords, ycoords, 1
	send {click}
	sleep 5
	send {wheeldown}
	sleep 5
	}
tooltip, Waiting (3s), xcoords, ycoords, 1
sleep 3000
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
ServerUnavailableStart:
ImageSearch, xxx, yyy, CenterX1, CenterY1, CenterX2, CenterY2, *50 %A_ScriptDir%\Images\Ok.png
if (ErrorLevel == 0)
	{
	tooltip, Server Unavailable (retrying), xcoords, ycoords, 1
	click %xxx% %yyy%
	sleep 250
	ImageSearch, , , CenterX1, CenterY1, CenterX2, CenterY2, *50 %A_ScriptDir%\Images\Ok.png
	if (ErrorLevel == 0)
		{
		goto ServerUnavailableStart
		}
	sleep 250
	send {rbutton down}
	sleep 250
	send {rbutton up}
	sleep 250
	loop, 40
		{
		send {wheel up}
		sleep 5
		}
	goto RandomServerStart
	}
else
	{
	tooltip, Menu Glitched (quick joining), xcoords, ycoords, 1
	QuickJoinStart:
	ImageSearch, xxx, yyy, CenterX1, 0, CenterX2, CenterY2, *50 %A_ScriptDir%\Images\QuickJoin.png
	if (ErrorLevel == 0)
		{
		sleep 250
		click %xxx% %yyy%
		sleep 3000
		ImageSearch, , , CenterX1, 0, CenterX2, CenterY2, *50 %A_ScriptDir%\Images\QuickJoin.png
		if (ErrorLevel == 0)
			{
			goto QuickJoinStart
			}
		}
	}
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
tooltip, Waiting For Character, xcoords, ycoords, 1
Timer := 0
SetTimer := 30
Failed := false
settimer, FailsafeTimer, 1000
HealthStart:
ImageSearch, , , 0, 0, TopLeftX2, TopLeftY2, *50 %A_ScriptDir%\Images\Health.png
if (ErrorLevel == 1)
	{
	if (Failed == true)
		{
		goto ForceResetStart
		}
	sleep 250
	goto HealthStart
	}
settimer, FailsafeTimer, off
tooltip, Failsafe: Disabled, xcoords, ycoords2, 2
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
send {tab}
incombat := false
settimer, DangerScan, 100
tooltip, Character Loaded (2s), xcoords, ycoords, 1
sleep 2000
ForceInnCounter++
if (ForceInnCounter > 10)
	{
	ForceInnCounter := 0
	gosub ForceInn
	goto ForceResetStart
	}
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
CheckLocationStart:
cavecount := 0
cavecheck := 0
CheckLocationStart2:
cavecount++
InCave := 1
ImageSearch, , , 0, CaveY1, CaveX2, CaveY2, *15 %A_ScriptDir%\Images\Cave1.png
if (ErrorLevel == 1)
	{
	ImageSearch, , , 0, CaveY1, CaveX2, CaveY2, *15 %A_ScriptDir%\Images\Cave2.png
	if (ErrorLevel == 1)
		{
		cavecheck++
		}
	}
sleep 200
if (cavecount < 10)
goto CheckLocationStart2
if (cavecheck >= 5)
InCave := 0
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
CheckSellStart:
ImageSearch, , , 0, 0, TopLeftX2, TopLeftY2, *50 %A_ScriptDir%\Images\InventoryFull.png
if (ErrorLevel == 0)
	{
	if (InCave == 1)
		{
		gosub ForceInn
		if (incombat == true)
		goto ForceResetStart
		gosub SellFirst
		if (incombat == true)
		goto ForceResetStart
		gosub walkback
		if (incombat == true)
		goto ForceResetStart
		goto CheckLocationStart
		}
	else
		{
		gosub SellFirst
		if (incombat == true)
		goto ForceResetStart
		gosub walkback
		if (incombat == true)
		goto ForceResetStart
		goto CheckLocationStart
		}
	}
if (InCave == 0)
gosub walkback
if (incombat == true)
goto ForceResetStart
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
LookingUp := false
tooltip, Waiting (3s), xcoords, ycoords, 1
settimer, SpamE, 100
sleep 3000
settimer, SpamE, off
tooltip, Mining Ore 1, xcoords, ycoords, 1
Timer := 0
SetTimer := 20
Failed := false
settimer, FailsafeTimer, 1000
MiningStart:
if (Failed == true)
goto ForceResetStart
PixelSearch, , , DangerX1, MiddleY, DangerX2, A_ScreenHeight, 0x267DA9, 10, Fast
if (ErrorLevel == 0)
	{
	if (LookingUp == false)
		{
		LookingUp := true
		gosub LookUp
		}
	ForceInnCounter := 0
	sleep 100
	goto MiningStart
	}
settimer, FailsafeTimer, off
tooltip, Failsafe: Disabled, xcoords, ycoords2, 2
ImageSearch, , , 0, 0, TopLeftX2, TopLeftY2, *20 %A_ScriptDir%\Images\InventoryFull.png
if (ErrorLevel == 0)
goto CheckSellStart
if (LookingUp == true)
	{
	LookingUp := false
	gosub LookDown
	}
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
if (CurrentOrePosition == 1)
	{
	tooltip, Walking Forwards, xcoords, ycoords, 1
	CurrentOrePosition := 2
	send {w down}
	sleep 300
	send {d down}
	sleep 100
	send {d up}
	sleep 1500
	send {w up}
	}
else
	{
	tooltip, Walking Backwards, xcoords, ycoords, 1
	CurrentOrePosition := 1
	send {s down}
	sleep 300
	send {d down}
	sleep 100
	send {d up}
	sleep 1250
	send {s up}
	}
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
tooltip, Waiting (3s), xcoords, ycoords, 1
settimer, SpamE, 100
sleep 3000
settimer, SpamE, off
tooltip, Mining Ore 2, xcoords, ycoords, 1
Timer := 0
SetTimer := 20
Failed := false
settimer, FailsafeTimer, 1000
MiningStart2:
if (Failed == true)
goto ForceResetStart
PixelSearch, , , DangerX1, MiddleY, DangerX2, A_ScreenHeight, 0x267DA9, 10, Fast
if (ErrorLevel == 0)
	{
	if (LookingUp == false)
		{
		LookingUp := true
		gosub LookUp
		}
	ForceInnCounter := 0
	sleep 100
	goto MiningStart2
	}
settimer, FailsafeTimer, off
tooltip, Failsafe: Disabled, xcoords, ycoords2, 2
ImageSearch, , , 0, 0, TopLeftX2, TopLeftY2, *20 %A_ScriptDir%\Images\InventoryFull.png
if (ErrorLevel == 0)
goto CheckSellStart
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
ServerHopStart:
tooltip, Server Hopping, xcoords, ycoords, 1
send {m down}
sleep 50
send {m up}
sleep 250
FindMenuStart:
FailCounter := 0
FailCounterMax := 5
FindMenu:
tooltip, Finding Exit, xcoords, ycoords, 1
ImageSearch, xxx, yyy, CenterX1, CenterY1, CenterX2, CenterY2, *30 %A_ScriptDir%\Images\Menu.png
if (ErrorLevel == 1)
	{
	FailCounter++
	if (FailCounter > FailCounterMax)
		{
		tooltip, Unknown State Force Reset, xcoords, ycoords, 1
		sleep 500
		goto ForceResetStart
		}
	sleep 250
	goto FindMenu
	}
else
	{
	FindConfirmStart:
	if (incombat == true)
		{
		tooltip, Unknown State Force Reset, xcoords, ycoords, 1
		sleep 500
		goto ForceResetStart
		}
	tooltip, Finding Confirm, xcoords, ycoords, 1
	click %xxx% %yyy%
	sleep 250
	ImageSearch, xxx, yyy, CenterX1, CenterY1, CenterX2, CenterY2, *40 %A_ScriptDir%\Images\Confirm.png
	if (ErrorLevel == 0)
		{
		click %xxx% %yyy%
		sleep 1000
		ImageSearch, , , CenterX1, CenterY1, CenterX2, CenterY2, *40 %A_ScriptDir%\Images\Confirm.png
		if (ErrorLevel == 0)
			{
			goto FindConfirmStart
			}
		}
	else
		{
		ImageSearch, , , CenterX1, CenterY1, CenterX2, CenterY2, *30 %A_ScriptDir%\Images\Menu.png
		if (ErrorLevel == 0)
			{
			goto FindMenuStart
			}
		}
	}
settimer, DangerScan, off
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;
tooltip, Waiting For Menu Load, xcoords, ycoords, 1
WaitForCompleteLoad:
ImageSearch, , , CenterX1, CenterY1, CenterX2, A_ScreenHeight, *50 %A_ScriptDir%\Images\PressKeyToContinue.png
if (ErrorLevel == 1)
	{
	sleep 250
	goto WaitForCompleteLoad
	}
else
	{
	goto PressKeyToContinueStart
	}
return
;=====;=====;=====;=====;=====;=====;=====;=====;=====;=====;





ForceInn:
tooltip, Force Resetting, xcoords, ycoords, 1
send {esc down}
sleep 100
send {esc up}
sleep 100
send {r down}
sleep 100
send {r up}
sleep 100
send {enter down}
sleep 100
send {enter up}
sleep 10000
if (incombat == true)
return
sleep 10000
if (incombat == true)
return
sleep 10000
if (incombat == true)
return
sleep 10000
return





walkback:
tooltip, Returning To Cave, xcoords, ycoords, 1
CurrentOrePosition := 2
send {s down}
sleep 500
send {s up}
sleep 100
send {e down}
sleep 100
send {e up}
sleep 5000
send {space down}
send {a down}
send {w down}
sleep 5000
if (incombat == true)
return
send {space up}
send {a up}
send {w up}
sleep 500
send {d down}
sleep 850
send {d up}
send {w down}
sleep 2000
if (incombat == true)
return
send {w up}
send {a down}
send {s down}
sleep 4000
if (incombat == true)
return
sleep 4000
if (incombat == true)
return
send {a up}
sleep 5000
if (incombat == true)
return
sleep 5000
if (incombat == true)
return
send {s up}
send {d down}
sleep 2000
if (incombat == true)
return
send {d up}
send {a down}
sleep 1500
if (incombat == true)
return
send {a up}
send {e down}
sleep 500
send {e up}
sleep 4500
if (incombat == true)
return
sleep 4000
if (incombat == true)
return
send {a down}
sleep 5000
if (incombat == true)
return
send {a up}
send {w down}
sleep 2500
if (incombat == true)
return
send {w up}
send {a down}
sleep 6000
if (incombat == true)
return
sleep 5000
if (incombat == true)
return
send {a up}
send {w down}
sleep 4500
if (incombat == true)
return
send {w up}
send {a down}
sleep 2000
if (incombat == true)
return
send {a up}
send {w down}
loop, 10
	{
	send {space down}
	sleep 50
	send {space up}
	sleep 50
	}
sleep 1000
if (incombat == true)
return
send {w up}
send {a down}
loop, 10
	{
	send {space down}
	sleep 50
	send {space up}
	sleep 50
	}
sleep 2000
if (incombat == true)
return
send {a up}
send {w down}
send {d down}
send {space down}
sleep 200
send {space up}
topscan := A_ScreenHeight/3
leftscan := A_ScreenWidth/3
ImageSearch, xxx, yyy, 0, 0, leftscan, topscan, *50 %A_ScriptDir%\Images\Duskwalk.png
if (ErrorLevel == 0)
	{
	send {x down}
	sleep 100
	send {x up}
	sleep 1000
	click %xxx% %yyy%
	sleep 1000
	send {x down}
	sleep 100
	send {x up}
	}
else
	{
	send {tab}
	sleep 100
	topscan := A_ScreenHeight/3
	leftscan := A_ScreenWidth/3
	ImageSearch, xxx, yyy, 0, 0, leftscan, topscan, *50 %A_ScriptDir%\Images\Duskwalk.png
	if (ErrorLevel == 0)
		{
		send {x down}
		sleep 100
		send {x up}
		sleep 1000
		click %xxx% %yyy%
		sleep 1000
		send {x down}
		sleep 100
		send {x up}
		}
	else
		{
		sleep 2200
		}
	}
sleep 3000
if (incombat == true)
return
send {space down}
sleep 200
send {space up}
sleep 6000
send {w up}
send {d up}
return





SellFirst:
tooltip, Selling Platinum, xcoords, ycoords, 1
send {s down}
sleep 500
send {s up}
sleep 100
send {e down}
sleep 100
send {e up}
sleep 5000
send {space down}
send {a down}
send {w down}
sleep 5000
if (incombat == true)
return
send {space up}
send {a up}
send {w up}
sleep 500
send {d down}
sleep 850
if (incombat == true)
return
send {d up}
send {w down}
sleep 5000
if (incombat == true)
return
send {a down}
sleep 500
send {a up}
sleep 2000
if (incombat == true)
return
send {w up}
send {a down}
sleep 500
send {a up}
sleep 500
send {e down}
sleep 100
send {e up}
sleep 1000
if (incombat == true)
return
send {1 down}
sleep 100
send {1 up}
sleep 1000
if (incombat == true)
return
failcount := 0
redodasdsadas:
ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *50 %A_ScriptDir%\Images\PlatinumOre.png
if (Errorlevel == 1)
	{
	failcount++
	if (failcount > 10)
		{
		settimer, DangerScan, off
		incombat := true
		return
		}
	sleep 500
	goto redodasdsadas
	}
Click, Right %xxx% %yyy%
Sellore := false
sleep 1000
if (incombat == true)
return
send {1 down}
sleep 100
send {1 up}
sleep 1000
if (incombat == true)
return
send {s down}
sleep 5000
if (incombat == true)
return
send {d down}
sleep 800
send {d up}
sleep 5000
if (incombat == true)
return
send {s up}
send {a down}
sleep 500
send {a up}
return