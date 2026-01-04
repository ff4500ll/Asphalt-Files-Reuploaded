;sell = 1600 125
;confirm = 1420 727
;garden = 1280 125

$m:: exitapp
$p::
settimer, spame, 2
loop,
{
click, 1280, 125
sleep 100
send {w down}
send {a down}
sleep 300
send {a up}
sleep 400
send {w up}
sleep 1500
send {d down}
sleep 800
send {d up}
sleep 11000
click, 1600, 125
sleep 1300
click, 1420 727
sleep 1500
}
return

spame:
send e
return