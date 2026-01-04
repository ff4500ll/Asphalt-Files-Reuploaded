#ifWinActive, Roblox ; focus roblox
on = false
setkeydelay, 0
setmousedelay, 0

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
suspend, on
}
return

~$esc::
~$enter:: ; chat unpause
suspend, off
on = false
return

$mbutton:: ; autoclicker
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
return

$xbutton2:: ; block climb
send {f down}
send {space}
return

$xbutton1:: ; spell run
send {g up}
send {w up}
send {w down}
send {w up}
send {lbutton}
send {w down}
return

$e::
settimer, sus, 10
send 3{click}
sleep 100
send -{click}
sleep 100
send {=}{click}
sleep 300
send 3{click}
sleep 100
send 5{click}
sleep 100
send 7{click}
sleep 100
send 8{click}
sleep 1000
settimer, sus, off
return

sus:
send {lbutton down}
sleep 5
send {lbutton up}
return

,:: suspend ; default suspend key