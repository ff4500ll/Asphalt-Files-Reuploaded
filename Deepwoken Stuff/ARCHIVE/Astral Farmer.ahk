$[:: reload

$]::
tooltip, macro is running (press [ to disable)
loop,
{
mousemove, 1200, 350
sleep 100

send {7 down}
sleep 100
send {7 up}
sleep 100

send {4 down}
sleep 100
send {4 up}
sleep 1500
send {4 down}
sleep 100
send {4 up}
sleep 1000

send {8 down}
sleep 100
send {8 up}
sleep 500
click, 930, 750
sleep 100
}
return