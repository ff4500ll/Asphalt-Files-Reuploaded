#ifWinActive, Roblox
#SingleInstance Force
#MaxHotkeysPerInterval 1000000000000
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1

pause = off

ManaToggle := false
LastWDownTime := 0

$xbutton2::lbutton
$r::-
$z::9
$x::0
$c::=

$h::
if (ManaToggle == false)
	{
	ManaToggle := true
	settimer, ChargeMana, 100
	}
else
	{
	ManaToggle := false
	settimer, ChargeMana, Off
	}
return

ChargeMana:
if (ManaToggle == false)
settimer, ChargeMana, Off
Send {g down}
Sleep 95
Send {g up}
return

~$w::
if (ManaToggle == true)
	{
	if (AvoidSpam == true)
	return
	AvoidSpam := true
	CurrentTime := A_TickCount
	if (CurrentTime-LastWDownTime <= 300)
		{
		settimer, ChargeMana, Off
		StateOfMana := false
		}
	LastWDownTime := CurrentTime
	}
return

w up::
if (ManaToggle == true)
	{
	AvoidSpam := false
	if (StateOfMana == false)
		{
		settimer, ChargeMana, 100
		StateOfMana := true
		}
	}
return

$o:: reload

~$`::
~$tab::
suspend, off
if pause = off
{
pause = on
tooltip, Paused
suspend, on
return
}
if pause = on
{
pause = off
tooltip
return
}
return

~$/::
if pause = off
{
pause = on
tooltip, Paused
suspend, on
return
}
else
return
return

~$esc::
~$enter::
suspend, off
pause = off
tooltip
return

*$lbutton::
settimer, lbutton, 10
gosub, lbutton
return
$lbutton up::
settimer, lbutton, off
	if (StateOfMana == false)
		{
		settimer, ChargeMana, 100
		StateOfMana := true
		}
return
lbutton:
GetKeyState, lbuttonstate, lbutton, p
if lbuttonstate = U
settimer, lbutton, off
send {lbutton down}
sleep 5
send {lbutton up}
return

*$e::
settimer, e, 100
gosub, e
return
$e up::
settimer, e, off
return
e:
GetKeyState, estate, e, p
if estate = U
settimer, e, off
send {e down}
sleep 50
send {e up}
return

*$q::
	if (StateOfMana == false)
		{
		settimer, ChargeMana, 100
		StateOfMana := true
		}
gosub, q
return
$q up::
settimer, q, off
return
q:
GetKeyState, qstate, q, p
if qstate = U
settimer, q, off
send {q down}
sleep 50
send {q up}
return