#ifWinActive, Roblox
#MaxHotkeysPerInterval 1000000000000
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
pause = off

$xbutton1::0
$xbutton2::9

$g::c
$z::6
$c::7
$v::8

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

*$q::
settimer, q, 100
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

*$r::
settimer, r, 100
gosub, r
return
$r up::
settimer, r, off
return
r:
GetKeyState, rstate, r, p
if rstate = U
settimer, r, off
send {r down}
sleep 50
send {r up}
return

*$mbutton::
settimer, mbutton, 100
gosub, mbutton
return
$mbutton up::
settimer, mbutton, off
return
mbutton:
GetKeyState, mbuttonstate, mbutton, p
if mbuttonstate = U
settimer, mbutton, off
send {q down}
sleep 50
send {q up}
return

,:: suspend
return