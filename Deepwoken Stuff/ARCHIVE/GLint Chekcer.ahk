#MaxHotkeysPerInterval 1000000000000
CoordMode Pixel
setkeydelay, 0
pause = off
active = false
tooltip, reloaded, 300, 500, 1

$m:: reload

$p::
loop,
{
ImageSearch, nigger1, faggot2, 0, 0, A_ScreenWidth, A_ScreenHeight, *50 %A_ScriptDir%\Glint\Blade.png
xxx := nigger1 - 22
yyy := faggot2 + 40
tooltip, x:%nigger1% y:%faggot2%, 300, 540, 3
If (ErrorLevel = 2)
    tooltip, Failed to scan, 300, 520, 2
else if (ErrorLevel = 1)
    {
    tooltip, No Glint, 300, 520, 2
    tooltip, , xxx, yyy, 4
    }
else
    {
    tooltip, Glint Found, 300, 520, 2
    tooltip, x:%nigger1% y:%faggot2%, xxx, yyy, 4
    sleep 130
    send {f down}
    sleep 500
    send {f up}
    }
sleep 1
}
return



