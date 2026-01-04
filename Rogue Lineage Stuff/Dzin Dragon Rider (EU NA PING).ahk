#ifWinActive, Roblox
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

~$esc:: ; chat unpause
~$enter::
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

$xbutton2::
send {g down}
send {rbutton}
sleep 250
send {f down}
sleep 500
send {f up}
send {g up}
return

$xbutton1:: ; spell run
send {g up}
send {w up}
send {w down}
send {w up}
send {lbutton}
send {w down}
return

return