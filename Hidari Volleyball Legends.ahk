#ifWinActive, Roblox
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1

;===================================;===================================;

pause = off
trigger := 0
JumpDelay1 := 400
JumpDelay2 := 450
JumpDelay3 := 500
JumpDelay4 := 550
JumpDelay := JumpDelay1

$up::
if (JumpDelay == JumpDelay1)
{
JumpDelay := JumpDelay2
}
else if (JumpDelay == JumpDelay2)
{
JumpDelay := JumpDelay3
}
else if (JumpDelay == JumpDelay3)
{
JumpDelay := JumpDelay4
}
else if (JumpDelay == JumpDelay4)
{
JumpDelay := JumpDelay4
}
return

$down::
if (JumpDelay == JumpDelay1)
{
JumpDelay := JumpDelay1
}
else if (JumpDelay == JumpDelay2)
{
JumpDelay := JumpDelay1
}
else if (JumpDelay == JumpDelay3)
{
JumpDelay := JumpDelay2
}
else if (JumpDelay == JumpDelay4)
{
JumpDelay := JumpDelay3
}
return

$xbutton1::
$xbutton2::
send {rbutton down}
return

$space::
send {shift}
sleep 30
send {space}
sleep 100
send {shift}
return

$/::
send {/ down}
keywait /
send {/ up}
if pause = off
{
pause = on
suspend, on
}
return

~$esc::
~$enter::
suspend, off
pause = off
return

$0:: exitapp
$9::
sleep 100
send {w up}
send {a up}
send {d up}
send {s up}
send {rbutton up}
if (trigger == 1)
{
send {shift}
}
send {esc}
sleep 50
send {esc}
reload
return

$1::
if (trigger == 0)
{
send {shift}
sleep 50
send {lbutton}
sleep 50
send {rbutton down}
trigger := 1
}
return

~$2::
if (trigger == 1)
	{
	trigger := 0
	ReloopHere2:
	PixelSearch, xxx, yyy, 1100, 1135, 1450, 1145, 0xFFFFFF, 0, Fast
	if (ErrorLevel == 0)
		{
		if (xxx > 1385)
			{
			send {lbutton}
			goto endcycle2
			}
		}
	goto ReloopHere2
	endcycle2:
	send {d down}
	sleep 150
	send {d up}
	sleep %JumpDelay%
	send {shift}
	send {rbutton up}	
	sleep 50
	send {space}
	sleep 50
	send {w down}
	send {lbutton}
	sleep 1000
	send {w up}
	}
return