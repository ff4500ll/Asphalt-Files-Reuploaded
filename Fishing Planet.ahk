setkeydelay, -1
setmousedelay, -1
setbatchlines, -1

toggle = false
hold = false

$xbutton2::
hold = true
toggle = false
send {lbutton down}
return

$xbutton1::
hold = false
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
if hold = true
{
send {lbutton down}
settimer, spam, off
}
return