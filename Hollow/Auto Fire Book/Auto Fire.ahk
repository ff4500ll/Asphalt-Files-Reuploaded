#SingleInstance Force
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
SetTitleMatchMode 2

CoordMode, Tooltip, Relative
CoordMode, Pixel, Relative
CoordMode, Mouse, Relative

$m:: exitapp
$p::
restart:

ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Fire.png
if (ErrorLevel == 0)
	{
	click, %xxx%, %yyy%
	}
else
	{
	ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Ember.png
	if (ErrorLevel == 0)
		{
		click, %xxx%, %yyy%
		}
	else
		{
		ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Fiery.png
		if (ErrorLevel == 0)
			{
			click, %xxx%, %yyy%
			}
		else
			{
			ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Scald.png
			if (ErrorLevel == 0)
				{
				click, %xxx%, %yyy%
				}
			else
				{
				ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Blaze.png
				if (ErrorLevel == 0)
					{
					click, %xxx%, %yyy%
					}
				else
					{
					ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Flam.png
					if (ErrorLevel == 0)
						{
						click, %xxx%, %yyy%
						}
					else
						{
						ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Inciner.png
						if (ErrorLevel == 0)
							{
							click, %xxx%, %yyy%
							}
						else
							{
							ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Burn.png
							if (ErrorLevel == 0)
								{
								click, %xxx%, %yyy%
								}
							else
								{
								ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Ignit.png
								if (ErrorLevel == 0)
									{
									click, %xxx%, %yyy%
									}
								else
									{
									ImageSearch, xxx, yyy, 0, 0, A_ScreenWidth, A_ScreenHeight, *20 %A_ScriptDir%\Heat.png
									if (ErrorLevel == 0)
										{
										click, %xxx%, %yyy%
										}
									else
										{
									
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
sleep 50
goto restart