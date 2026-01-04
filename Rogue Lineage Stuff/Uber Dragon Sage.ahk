#ifWinActive, Roblox ; focus roblox
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
suspend, on
}
return

~$esc::
~*$esc::
~$enter:: ; chat unpause
~*$enter::
suspend, off
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

$mbutton:: ; autoclicker
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
return

$xbutton1:: ; spell run
send {g up}
sleep 10
send {w up}
sleep 10
send {w down}
send {w up}
send {lbutton}
sleep 10
send {w down}
return

$,:: suspend