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

$o:: reload

$f::7
$r::5

$q::
settimer, spamclick, 10
while getkeystate("q","P")
{
send 3
sleep 5
send e
sleep 5
}
settimer, spamclick, off
return

spamclick:
send {lbutton}
return