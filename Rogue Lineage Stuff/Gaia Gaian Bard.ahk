#ifWinActive, Roblox
on = false

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

,:: suspend
return

$t::0
return

~$3::
var := 3
return

~$4::
var := 4
return

~$5::
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

$z::
send {f up}
sleep 100
send 1
send {f down}
send %var%
return

$x::
send 0
send {lbutton}
send %var%
return

$t::
send 9
send {lbutton}
send %var%
return

$y::
send 8
send {lbutton}
send %var%
return

$xbutton1::
send {f up}
send {g down}
send 1
send {rbutton}
send %var%
sleep 100
send 2
send {f down}
send %var%
sleep 500
send {f up}
send {g up}
return