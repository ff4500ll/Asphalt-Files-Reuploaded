#ifWinActive, Roblox 
setkeydelay, 0
setmousedelay, 0
on = false

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
~$enter::
suspend, off
tooltip
on = false
return

$mbutton::
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
return

$xbutton2::
send {f down}
send {space}
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