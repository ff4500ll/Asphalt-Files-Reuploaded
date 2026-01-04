#ifWinActive, Roblox ; focus roblox
on = false
setkeydelay, 0

~$/:: ; chat pause
if on = false
{
on = true
tooltip, macro paused ah just saying
suspend, on
}
return

~$esc::
~$enter:: ; chat unpause
suspend, off
tooltip
on = false
return

,:: suspend ; default suspend key

$v::
send {lbutton up}
send {rbutton up}
send {space up}
reload
return

$r::
send {lbutton down}
sleep 450
send {lbutton up}
return

$e::
send {lbutton down}
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -5000)
sleep 50
send {lbutton up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 1000)
return

$q::
send {lbutton down}
sleep 150
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -5000)
sleep 50
send {lbutton up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 1000)
sleep 100
send {lbutton down}
send {rbutton down}
send {lbutton up}
send {rbutton up}
return

$x::
send {lbutton down}
sleep 400
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -5000)
sleep 50
send {lbutton up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 1000)
sleep 100
send {lbutton down}
send {rbutton down}
send {lbutton up}
send {rbutton up}
sleep 100
send {lbutton down}
sleep 200
send {space down}
sleep 50
send {space up}
sleep 200
send {lbutton up}
return

$c::
send {rbutton down}
sleep 350
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -5000)
sleep 50
send {rbutton up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 1000)
sleep 100
send {lbutton down}
sleep 300
send {space down}
sleep 50
send {space up}
sleep 100
send {lbutton up}
return

$z::
send {rbutton down}
sleep 350
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -5000)
sleep 50
send {rbutton up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 1000)
sleep 100
send {rbutton down}
sleep 100
send {space down}
sleep 50
send {space up}
sleep 300
send {rbutton up}
return

$f::
send {rbutton down}
sleep 250
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -5000)
sleep 50
send {rbutton up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 1000)
sleep 200
send {rbutton down}
sleep 50
send {space down}
sleep 50
send {space up}
sleep 50
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -5000)
sleep 50
send {rbutton up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 1000)
sleep 200
send {lbutton down}
sleep 250
send {space down}
sleep 50
send {space up}
sleep 150
send {lbutton up}
return