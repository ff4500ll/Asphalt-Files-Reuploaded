$xbutton1::
while getkeystate("xbutton1","P")
{
send {lbutton down}
sleep 400
send {wheeldown}
sleep 450
send {wheelup}
}
keywait xbutton1
send {lbutton up}
return