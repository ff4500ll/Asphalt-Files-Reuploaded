cooldown = off

f::
if cooldown = off
{
cooldown = on
settimer, cooldowntracker, 100000
send 3
}
else
{
send {f down}
keywait f
send {f up}
}
return

cooldowntracker:
settimer, cooldowntracker, off
sleep 60000
cooldown = off
return