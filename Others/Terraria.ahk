setkeydelay, 0
setbatchlines, 0

$xbutton2::
while getkeystate("xbutton2","P")
{
send {lbutton down}
sleep 50
send {lbutton up}
}
return

$p::
loop,
{
send {rbutton down}
sleep 7300
send {rbutton up}
sleep 10
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", 100)
sleep 10
send {lbutton down}
sleep 10
send {lbutton up}
sleep 10
DllCall("mouse_event", "UInt", 0x01, "UInt", 0, "UInt", -100)
sleep 10
}
return

$m:: exitapp