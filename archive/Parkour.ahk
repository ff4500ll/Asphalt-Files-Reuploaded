#ifWinActive, Roblox
setbatchlines, -1
setmousedelay, -1
setkeydelay, -1
pause = off
locked = on
Hotkey, *rbutton, Off

.::reload

~g::
if locked = on
{
locked = off
Hotkey, *rbutton, On
}
else
{
locked = on
Hotkey, *rbutton, Off
loop, 4
{
send {wheeldown}
sleep 1
}
}
keywait g
return

*xbutton2::mbutton

*1::
send e
sleep 50
send {space down}
random, rand, 25, 75
sleep %rand%
send {space up}
sleep 10
DllCall("mouse_event", "UInt", 0x01, "UInt", -1200, "UInt", 0)
sleep 10
send {space down}
random, rand, 25, 75
sleep %rand%
send {space up}
keywait xbutton1
return

*rbutton::
DllCall("mouse_event", "UInt", 0x01, "UInt", -1200, "UInt", 0)
return

*2::
*r::
send {space down}
random, rand, 25, 75
sleep %rand%
send {space up}
keywait 2
keywait r
return

*f::
send {space down}
random, rand, 10, 30
sleep %rand%
send {space up}
random, rand, 20, 40
sleep %rand%
send {space down}
random, rand, 200, 400
sleep %rand%
send {space up}
keywait f
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