#ifWinActive, Roblox
#SingleInstance Force
#MaxHotkeysPerInterval 1000000000000
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1

pause = off
toggle = off
rightclick = off

$,::
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

~$esc::
~$enter::
suspend, off
pause = off
tooltip
return

$rbutton::
rightclick = on
settimer, spamr, 100
return

$rbutton up::
rightclick = off
settimer, spamr, off
send {rbutton up}
return

spamr:
send {lbutton down}
sleep 50
send {lbutton up}
if getkeystate("lbutton","U")
{
settimer, spamr, off
send {lbutton up}
}
return

$e::
if toggle = off
{
toggle = on
tooltip, E, 50, 1350, 2
settimer, spame, 100
}
else
{
toggle = off
tooltip, , , , 2
settimer, spame, off
}
return

spame:
send {e down}
sleep 25
send {e up}
return