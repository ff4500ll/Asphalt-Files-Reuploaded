setkeydelay, 0
setmousedelay, 0

delay := 100
halfdelay := delay/2
toggle := 0

*z::
if (toggle == 0)
{
toggle := 1
settimer, sneaker, %delay%
tooltip, sneaking
}
else
{
toggle := 0
settimer, sneaker, off
tooltip
}
return

sneaker:
send {shift down}
sleep %halfdelay%
send {shift up}
return