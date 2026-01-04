#ifWinActive, Roblox ; focus roblox
on = false
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
$y::7
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

$mbutton:: ; autoclicker
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
return

$xbutton2:: ; snap ignis
send {g down}
send {rbutton}
sleep 150
send {f down}
sleep 500
send {f up}
return

$xbutton1:: ; spell run
send {g up}
send {w up}
send {w down}
send {w up}
send {lbutton}
send {w down}
return

,:: suspend ; default suspend key