#ifWinActive, Roblox
setkeydelay, 0

$z::9
return
$x::0
return
$r::-
return
$c::=
return
$t::8
return

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

$q:: ; auto dash
settimer, dash, 100
gosub, dash
return
$q up::
settimer, dash, off
send {q up}
return
dash:
send {q down}
sleep 50
send {q up}
return

$mbutton::
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
return

$xbutton2::
send {rbutton}
send 3
sleep 100
send {lbutton}
return

$xbutton1::
send {g up}
send {w up}
send {w down}
send {w up}
send {lbutton}
send {w down}
return

,:: suspend