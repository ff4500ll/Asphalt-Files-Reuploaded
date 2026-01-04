#ifWinActive, Roblox
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
pause = off
Gun := 1
Position := 1
tooltipx := A_ScreenWidth/20
tooltipy := A_ScreenHeight/1.2

MainGunStand := 9
MainGunCrouch := 7
MainGunCrawl := 5
MainGunDelay := 10

SubGunStand := 3
SubGunCrouch := 2
SubGunCrawl := 1
SubGunDelay := 10

~$/::
if pause = off
{
pause = on
tooltip, Paused
suspend, on
}
return

~$esc::
~$enter::
suspend, off
pause = off
tooltip
return

~*lbutton::
while GetKeyState("LButton", "P")
	{
	if (Gun == 3)
		{
		Sleep, MainGunDelay
		}
	else if (Gun == 1 and Position == 1)
		{
		DllCall("mouse_event", "UInt", 1, "Int", 0, "Int", MainGunStand, "UInt", 0, "UInt", 0)
		Sleep, MainGunDelay
		}
	else if (Gun == 1 and Position == 2)
		{
		DllCall("mouse_event", "UInt", 1, "Int", 0, "Int", MainGunCrouch, "UInt", 0, "UInt", 0)
		Sleep, MainGunDelay
		}
	else if (Gun == 1 and Position == 3)
		{
		DllCall("mouse_event", "UInt", 1, "Int", 0, "Int", MainGunCrawl, "UInt", 0, "UInt", 0)
		Sleep, MainGunDelay
		}
	else if (Gun == 2 and Position == 1)
		{
		DllCall("mouse_event", "UInt", 1, "Int", 0, "Int", SubGunStand, "UInt", 0, "UInt", 0)
		Sleep, SubGunDelay
		}
	else if (Gun == 2 and Position == 2)
		{
		DllCall("mouse_event", "UInt", 1, "Int", 0, "Int", SubGunCrouch, "UInt", 0, "UInt", 0)
		Sleep, SubGunDelay
		}
	else if (Gun == 2 and Position == 3)
		{
		DllCall("mouse_event", "UInt", 1, "Int", 0, "Int", SubGunCrawl, "UInt", 0, "UInt", 0)
		Sleep, SubGunDelay
		}
    else
		{
		Sleep, MainGunDelay
		Sleep, SubGunDelay
		}
    }
return

$o:: reload

~*1::
Gun := 1
gosub, UpdateTooltips
return

~*2::
Gun := 2
gosub, UpdateTooltips
return

~*3::
Gun := 3
gosub, UpdateTooltips
return

~*c::
~*ctrl::
if (Position == 1)
	{
	Position := 2
	}
else if (Position == 2)
	{
	Position := 3
	}
else if (Position == 3)
	{
	Position := 1
	}
gosub, UpdateTooltips
return

~*space::
if (Position == 3)
	{
	Position := 2
	}
else if (Position == 2)
	{
	Position := 1
	}
gosub, UpdateTooltips
return

~*shift::
Position := 1
gosub, UpdateTooltips
return

$xbutton2::
if (Gun == 1 and Position == 1)
	{
	MainGunStand++
	}
else if (Gun == 1 and Position == 2)
	{
	MainGunCrouch++
	}
else if (Gun == 1 and Position == 3)
	{
	MainGunCrawl++
	}
else if (Gun == 2 and Position == 1)
	{
	SubGunStand++
	}
else if (Gun == 2 and Position == 2)
	{
	SubGunCrouch++
	}
else if (Gun == 2 and Position == 3)
	{
	SubGunCrawl++
	}
goto UpdateTooltips
return

$xbutton1::
if (Gun == 1 and Position == 1)
	{
	MainGunStand--
	}
else if (Gun == 1 and Position == 2)
	{
	MainGunCrouch--
	}
else if (Gun == 1 and Position == 3)
	{
	MainGunCrawl--
	}
else if (Gun == 2 and Position == 1)
	{
	SubGunStand--
	}
else if (Gun == 2 and Position == 2)
	{
	SubGunCrouch--
	}
else if (Gun == 2 and Position == 3)
	{
	SubGunCrawl--
	}
goto UpdateTooltips
return

UpdateTooltips:
if (Gun == 3)
	{
	tooltip, Gun: %Gun%`nPosition: %Position%`nPixel: 0, tooltipx, tooltipy
	}
else if (Gun == 1 and Position == 1)
	{
	tooltip, Gun: %Gun%`nPosition: %Position%`nPixel: %MainGunStand%, tooltipx, tooltipy
	}
else if (Gun == 1 and Position == 2)
	{
	tooltip, Gun: %Gun%`nPosition: %Position%`nPixel: %MainGunCrouch%, tooltipx, tooltipy
	}
else if (Gun == 1 and Position == 3)
	{
	tooltip, Gun: %Gun%`nPosition: %Position%`nPixel: %MainGunCrawl%, tooltipx, tooltipy
	}
else if (Gun == 2 and Position == 1)
	{
	tooltip, Gun: %Gun%`nPosition: %Position%`nPixel: %SubGunStand%, tooltipx, tooltipy
	}
else if (Gun == 2 and Position == 2)
	{
	tooltip, Gun: %Gun%`nPosition: %Position%`nPixel: %SubGunCrouch%, tooltipx, tooltipy
	}
else if (Gun == 2 and Position == 3)
	{
	tooltip, Gun: %Gun%`nPosition: %Position%`nPixel: %SubGunCrawl%, tooltipx, tooltipy
	}
return