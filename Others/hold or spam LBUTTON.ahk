setkeydelay, -1
setmousedelay, -1
setbatchlines, -1

toggle = false

$xbutton2::
send {lbutton down}
return

$xbutton1::
if toggle = false
{
toggle = true
settimer, spam, 100
}
else
{
toggle = false
settimer, spam, off
}
return

spam:
send {lbutton down}
sleep 50
send {lbutton up}
return