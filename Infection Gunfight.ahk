#ifWinActive, Roblox
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
pause = off

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

$xbutton1::
send {rbutton down}
return

$xbutton2::
send {lbutton down}
return