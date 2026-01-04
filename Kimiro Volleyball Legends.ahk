#ifWinActive, Roblox
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
pause = off
trigger := 0
xcoords := A_ScreenWidth/20
ycoords := A_ScreenHeight/1.2
x1 := 1100/2560*A_ScreenWidth
x2 := 1450/2560*A_ScreenWidth
y1 := 1135/1440*A_ScreenHeight
y2 := 1145/1440*A_ScreenHeight

;===================================;===================================;

;KAGAYAMO: SG 550 | JP 570 | US 590 | MOON 650

;KIMIRO: SG 455 | JP 490 | US 550 | MOON 570

JumpDelay1 := 455
JumpDelay2 := 490
JumpDelay3 := 550
JumpDelay4 := 570

;higher = more right
PurpleSpikeCoordinates := 1385

;===================================;===================================;

JumpDelay := JumpDelay1
if (JumpDelay == 455)
Server := "SG"
else if (JumpDelay == 490)
Server := "JP"
else if (JumpDelay == 550)
Server := "US"
else if (JumpDelay == 570)
Server := "MOON"
else
Server := "UNKNOWN"

tooltip, 1 = Setup Moving`n2 = Setup Pump Fake`n3 = Fire`n%Server% %JumpDelay%`n5 = Reload`n0 = Exit, xcoords, ycoords, 2
PurpleSpikeCoordinates := 1385/2560*A_ScreenWidth

$up::
if (JumpDelay == 455)
{
Server := "JP"
JumpDelay := JumpDelay2
}
else if (JumpDelay == 490)
{
Server := "US"
JumpDelay := JumpDelay3
}
else if (JumpDelay == 550)
{
Server := "MOON"
JumpDelay := JumpDelay4
}
else if (JumpDelay == 570)
{
Server := "MOON"
JumpDelay := JumpDelay4
}
else
Server := "UNKNOWN"
tooltip, 1 = Setup Moving`n2 = Setup Pump Fake`n3 = Fire`n%Server% %JumpDelay%`n5 = Reload`n0 = Exit, xcoords, ycoords, 2
return

$down::
if (JumpDelay == 455)
{
Server := "SG"
JumpDelay := JumpDelay1
}
else if (JumpDelay == 490)
{
Server := "SG"
JumpDelay := JumpDelay1
}
else if (JumpDelay == 550)
{
Server := "JP"
JumpDelay := JumpDelay2
}
else if (JumpDelay == 570)
{
Server := "US"
JumpDelay := JumpDelay3
}
else
Server := "UNKNOWN"
tooltip, 1 = Setup Moving`n2 = Setup Pump Fake`n3 = Fire`n%Server% %JumpDelay%`n5 = Reload`n0 = Exit, xcoords, ycoords, 2
return

~$/::
if pause = off
{
pause = on
tooltip, Paused
suspend, on
}
return

~$esc::
~$enter::
suspend, off
pause = off
tooltip
return

$0:: exitapp
$5::
tooltip, reloading
sleep 100
send {w up}
send {rbutton up}
if (trigger == 1)
{
send {shift}
}
reload
return

$1::
if (trigger == 0)
{
send {shift}
sleep 50
send {lbutton}
sleep 50
send {w down}
sleep 50
send {rbutton down}
trigger := 1
tooltip, armed Forward Jump
}
return

$2::
if (trigger == 0)
{
send {shift}
sleep 50
send {lbutton}
sleep 50
send {rbutton down}
trigger := 2
tooltip, armed Pump Fake
}
return

~$3::
if (trigger == 1)
	{
	trigger := 0
	tooltip, firing
	ReloopHere:
	PixelSearch, xxx, yyy, x1, y1, x2, y2, 0xFFFFFF, 0, Fast
	if (ErrorLevel == 0)
		{
		if (xxx > PurpleSpikeCoordinates)
			{
			send {lbutton}
			goto endcycle
			}
		}
	goto ReloopHere
	endcycle:
	send {w up}
	sleep %JumpDelay%
	send {shift}
	send {rbutton up}	
	sleep 50
	send {w down}
	sleep 10
	send {space}
	sleep 100
	send {lbutton}
	sleep 500
	send {w up}
	tooltip
	}
else if (trigger == 2)
	{
	trigger := 0
	tooltip, firing
	ReloopHere3:
	PixelSearch, xxx, yyy, x1, y1, x2, y2, 0xFFFFFF, 0, Fast
	if (ErrorLevel == 0)
		{
		if (xxx > PurpleSpikeCoordinates)
			{
			send {lbutton}
			goto endcycle3
			}
		}
	goto ReloopHere3
	endcycle3:
	delaydynamic := 1755-JumpDelay
	sleep 300
	send {shift}
	sleep 100
	send {space}
	sleep 200
	send {shift}
	sleep %delaydynamic%
	send {shift}
	sleep 50
	send {space}
	sleep 100
	send {lbutton}
	tooltip
	}
return