viri = 1

$o::
loop,
{
send {g down}
sleep 500
send {g up}
send {lbutton}
sleep 200
send %viri%
sleep 800
send %viri%
}
return

$p::
loop,
{
send {g down}
sleep 500
send {g up}
send {lbutton}
sleep 1500
}
return

$m:: reload