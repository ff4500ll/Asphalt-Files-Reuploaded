#ifWinActive, Roblox
#MaxHotkeysPerInterval 1000000000000
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
pause = off

toggle = false

$,:: suspend

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

$rbutton::
if toggle = false
{
send {e down}
keywait, rbutton, t0.02
if !errorlevel
{
send {e up}
return
}
keywait, rbutton
send {e up}
toggle = true
}
else
{
send {q down}
keywait, rbutton, t0.02
if !errorlevel
{
send {q up}
return
}
keywait, rbutton
send {q up}
toggle = false
}
return

$mbutton::
while getkeystate("mbutton","P")
{
send {lbutton down}
sleep 50
send {lbutton up}
sleep 50
}
return

$r::
while getkeystate("r","P")
{
send {r down}
sleep 50
send {r up}
sleep 50
}
return

$1::
while getkeystate("1","P")
{
send {1 down}
sleep 50
send {1 up}
sleep 50
}
return

$2::
while getkeystate("2","P")
{
send {2 down}
sleep 50
send {2 up}
sleep 50
}
return

$3::
while getkeystate("3","P")
{
send {3 down}
sleep 50
send {3 up}
sleep 50
}
return

$4::
while getkeystate("4","P")
{
send {4 down}
sleep 50
send {4 up}
sleep 50
}
return

$5::
while getkeystate("5","P")
{
send {5 down}
sleep 50
send {5 up}
sleep 50
}
return