#ifWinActive, Roblox
on = false
setkeydelay, 0
setmousedelay, 0

$xbutton2::
send {g up}
sleep 10
send {w up}
sleep 10
send {w down}
sleep 10
send {w up}
sleep 10
send {rbutton}
sleep 10
send {w down}
return

$xbutton1::
send {g up}
sleep 10
send {w up}
sleep 10
send {w down}
sleep 10
send {w up}
sleep 10
send {lbutton}
sleep 10
send {w down}
return

$m:: reload

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

$mbutton::
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
return

,:: suspend