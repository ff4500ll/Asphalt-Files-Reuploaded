$t::
send {space down}
sleep 100
send {t}
send {space up}
return
$v::
while getkeystate("v","P")
send v
return
$e::
while getkeystate("e","P")
send e
return
$f::
while getkeystate("f","P")
send f
return
$z::
while getkeystate("z","P")
send z
return
$r::
while getkeystate("r","P")
send r
return
$,:: suspend
return