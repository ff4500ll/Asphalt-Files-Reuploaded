#ifWinActive, Roblox
setbatchlines, -1
setmousedelay, -1
setkeydelay, -1
pause = off

.::reload

*1::
send {shift down}
sleep 320
DllCall("mouse_event", "UInt", 0x01, "UInt", -600, "UInt", 0)
sleep 50
send {mbutton}
sleep 50
send {space down}
random, rand, 25, 75
sleep %rand%
send {space up}
send {shift up}
sleep 50
random, rand, 25, 75
sleep %rand%
send {space down}
random, rand, 25, 75
sleep %rand%
send {space up}
DllCall("mouse_event", "UInt", 0x01, "UInt", -1200, "UInt", 0)
sleep 50
send {space down}
random, rand, 25, 75
sleep %rand%
send {space up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 600, "UInt", 0)
sleep 100
send {space down}
random, rand, 25, 75
sleep %rand%
send {space up}
keywait 1
return

*2::
send {shift down}
sleep 320
DllCall("mouse_event", "UInt", 0x01, "UInt", -600, "UInt", 0)
sleep 50
send {mbutton}
sleep 50
send {space down}
random, rand, 25, 75
sleep %rand%
send {space up}
send {shift up}
sleep 50
random, rand, 25, 75
sleep %rand%
send {space down}
random, rand, 25, 75
sleep %rand%
send {space up}
DllCall("mouse_event", "UInt", 0x01, "UInt", -1200, "UInt", 0)
sleep 50
send {space down}
random, rand, 25, 75
sleep %rand%
send {space up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 600, "UInt", 0)
sleep 100
send {space down}
random, rand, 25, 75
sleep %rand%
send {space up}
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", -1200, "UInt", 0)
keywait 2
return

,::
suspend, off
if pause = off
{
pause = on
suspend, on
return
}
else
{
suspend, off
pause = off
}
return

~/::
if pause = off
{
pause = on
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
return