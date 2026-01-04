#ifWinActive, Roblox
#MaxHotkeysPerInterval 1000000000000
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

*$space::
while getkeystate("space","P")
{
send {space down}
sleep 10
send {space up}
sleep 10
}
return