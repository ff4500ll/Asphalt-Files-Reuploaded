#ifWinActive, Roblox
setkeydelay, 0

,:: suspend
return

~$/::
if on = false
{
on = true
suspend, on
}
return

~$enter::
suspend, off
on = false
return

$3::
send 3
var := 3
return

$4::
send 4
var := 4
return

$5::
send 5
var := 5
return

$r::
send -
var := "-"
return

$c::
send {=}
var := "="
return

$y::
send 9
send {lbutton}
send %var%
return

$t::
send 0
send {lbutton down}
send %var%
send {lbutton up}
keywait t
send 0
send {lbutton}
send %var%
return

$z::
send 1
send {f down}
send %var%
return

$x::
send 8
send {lbutton}
send %var%
return

$xbutton1::
send {g down}
send 1
send {rbutton}
send %var%
sleep 100
send 1
send {f down}
send %var%
sleep 500
send {f up}
send {g up}
return

$xbutton2::
send {f down}
send {space}
return