setkeydelay, 0
setmousedelay, 0

$xbutton1::
send {g down}
sleep 2000
send {g up}
loop,
{
send {space down}
sleep 50
send {space up}
sleep 50
send {lbutton down}
sleep 50
send {lbutton up}
sleep 600
send {g down}
sleep 1200
send {g up}
}
return

$xbutton2::
send {g up}
reload
