;Change this to ur wisp hotkey
Wisp := 7

;Change These To Your Graceful Flame Signs
Key1Graceful := "z"
Key2Graceful := "c"
Key3Graceful := "z"

p::
send %Wisp%
sleep 100
send {rbutton down}
sleep 100
send {rbutton up}
sleep 100
send %Key1Graceful%
sleep 100
send {rbutton down}
sleep 100
send {rbutton up}
sleep 100
send %Key2Graceful% down
sleep 100
send {rbutton down}
sleep 100
send {rbutton up}
sleep 100
send %Key3Graceful%
return