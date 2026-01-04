#SingleInstance Force
#Requires AutoHotkey v2
#include OCR.ahk

SetWorkingDir(A_ScriptDir)

CoordMode "Mouse", "Screen"
CoordMode "ToolTip", "Screen"

HalfY := A_ScreenHeight/2

sparkling := 1
shiny := 1
giant := 1
big := 1
mythical := 1
hexed := 1
abyssal := 1
electric := 1
fossilized := 1
darkened := 1
translucent := 1
lunar := 1
solarblaze := 1
frozen := 1
midas := 1
negative := 1
glossy := 1
scorched := 1
silver := 1
albino := 1
mosaic := 1
amber := 1
multiple := 1

MainWindowN := Gui()
hMainWnd := MainWindowN.Hwnd
ogcCheckBoxChkSparkling := MainWindowN.Add("CheckBox", "vChkSparkling  x8 y8 w63 h23", "sparkling")
ogcCheckBoxChkSparkling.OnEvent("Click", GSparkling.Bind("Normal"))
hChkSparkling := ogcCheckBoxChkSparkling.hwnd
ogcCheckBoxChkShiny2 := MainWindowN.Add("CheckBox", "vChkShiny2  x8 y32 w45 h23", "shiny")
ogcCheckBoxChkShiny2.OnEvent("Click", GShiny.Bind("Normal"))
hChkShiny2 := ogcCheckBoxChkShiny2.hwnd
ogcCheckBoxChkGiant3 := MainWindowN.Add("CheckBox", "vChkGiant3  x72 y8 w42 h23", "giant")
ogcCheckBoxChkGiant3.OnEvent("Click", GGiant.Bind("Normal"))
hChkGiant3 := ogcCheckBoxChkGiant3.hwnd
ogcCheckBoxChkBig4 := MainWindowN.Add("CheckBox", "vChkBig4  x72 y32 w43 h23", "big")
ogcCheckBoxChkBig4.OnEvent("Click", GBig.Bind("Normal"))
hChkBig4 := ogcCheckBoxChkBig4.hwnd
ogcCheckBoxChkMythical5 := MainWindowN.Add("CheckBox", "vChkMythical5  x8 y96 w56 h23", "mythical")
ogcCheckBoxChkMythical5.OnEvent("Click", GMythical.Bind("Normal"))
hChkMythical5 := ogcCheckBoxChkMythical5.hwnd
ogcCheckBoxChkAbyssal6 := MainWindowN.Add("CheckBox", "vChkAbyssal6  x8 y120 w54 h23", "abyssal")
ogcCheckBoxChkAbyssal6.OnEvent("Click", GAbyssal.Bind("Normal"))
hChkAbyssal6 := ogcCheckBoxChkAbyssal6.hwnd
ogcCheckBoxChkFossilized7 := MainWindowN.Add("CheckBox", "vChkFossilized7  x8 y144 w60 h23", "fossilized")
ogcCheckBoxChkFossilized7.OnEvent("Click", GFossilized.Bind("Normal"))
hChkFossilized7 := ogcCheckBoxChkFossilized7.hwnd
ogcCheckBoxChkLunar8 := MainWindowN.Add("CheckBox", "vChkLunar8  x8 y168 w41 h23", "lunar")
ogcCheckBoxChkLunar8.OnEvent("Click", GLunar.Bind("Normal"))
hChkLunar8 := ogcCheckBoxChkLunar8.hwnd
ogcCheckBoxChkSolarblaze9 := MainWindowN.Add("CheckBox", "vChkSolarblaze9  x8 y192 w43 h23", "solar")
ogcCheckBoxChkSolarblaze9.OnEvent("Click", GSolarBlaze.Bind("Normal"))
hChkSolarblaze9 := ogcCheckBoxChkSolarblaze9.hwnd
ogcCheckBoxChkMidas10 := MainWindowN.Add("CheckBox", "vChkMidas10  x8 y216 w49 h23", "midas")
ogcCheckBoxChkMidas10.OnEvent("Click", GMidas.Bind("Normal"))
hChkMidas10 := ogcCheckBoxChkMidas10.hwnd
ogcCheckBoxChkGlossy11 := MainWindowN.Add("CheckBox", "vChkGlossy11  x8 y240 w49 h23", "glossy")
ogcCheckBoxChkGlossy11.OnEvent("Click", GGlossy.Bind("Normal"))
hChkGlossy11 := ogcCheckBoxChkGlossy11.hwnd
ogcCheckBoxChkSilver12 := MainWindowN.Add("CheckBox", "vChkSilver12  x8 y264 w45 h23", "silver")
ogcCheckBoxChkSilver12.OnEvent("Click", GSilver.Bind("Normal"))
hChkSilver12 := ogcCheckBoxChkSilver12.hwnd
ogcCheckBoxChkMosaic13 := MainWindowN.Add("CheckBox", "vChkMosaic13  x8 y288 w53 h23", "mosaic")
ogcCheckBoxChkMosaic13.OnEvent("Click", GMosaic.Bind("Normal"))
hChkMosaic13 := ogcCheckBoxChkMosaic13.hwnd
ogcCheckBoxChkHexed14 := MainWindowN.Add("CheckBox", "vChkHexed14  x72 y96 w48 h23", "hexed")
ogcCheckBoxChkHexed14.OnEvent("Click", GHexed.Bind("Normal"))
hChkHexed14 := ogcCheckBoxChkHexed14.hwnd
ogcCheckBoxChkElectric15 := MainWindowN.Add("CheckBox", "vChkElectric15  x72 y120 w54 h23", "electric")
ogcCheckBoxChkElectric15.OnEvent("Click", GElectric.Bind("Normal"))
hChkElectric15 := ogcCheckBoxChkElectric15.hwnd
ogcCheckBoxChkDarkened16 := MainWindowN.Add("CheckBox", "vChkDarkened16  x72 y144 w66 h23", "darkened")
ogcCheckBoxChkDarkened16.OnEvent("Click", GDarkened.Bind("Normal"))
hChkDarkened16 := ogcCheckBoxChkDarkened16.hwnd
ogcCheckBoxChkTranslucent17 := MainWindowN.Add("CheckBox", "vChkTranslucent17  x72 y168 w73 h23", "translucent")
ogcCheckBoxChkTranslucent17.OnEvent("Click", GTranslucent.Bind("Normal"))
hChkTranslucent17 := ogcCheckBoxChkTranslucent17.hwnd
ogcCheckBoxChkFrozen18 := MainWindowN.Add("CheckBox", "vChkFrozen18  x72 y192 w48 h23", "frozen")
ogcCheckBoxChkFrozen18.OnEvent("Click", GFrozen.Bind("Normal"))
hChkFrozen18 := ogcCheckBoxChkFrozen18.hwnd
ogcCheckBoxChkNegative19 := MainWindowN.Add("CheckBox", "vChkNegative19  x72 y216 w63 h23", "negative")
ogcCheckBoxChkNegative19.OnEvent("Click", GNegative.Bind("Normal"))
hChkNegative19 := ogcCheckBoxChkNegative19.hwnd
ogcCheckBoxChkScorched20 := MainWindowN.Add("CheckBox", "vChkScorched20  x72 y240 w65 h23", "scorched")
ogcCheckBoxChkScorched20.OnEvent("Click", GScorched.Bind("Normal"))
hChkScorched20 := ogcCheckBoxChkScorched20.hwnd
ogcCheckBoxChkAlbino21 := MainWindowN.Add("CheckBox", "vChkAlbino21  x72 y264 w48 h23", "albino")
ogcCheckBoxChkAlbino21.OnEvent("Click", GAlbino.Bind("Normal"))
hChkAlbino21 := ogcCheckBoxChkAlbino21.hwnd
ogcCheckBoxChkAmber22 := MainWindowN.Add("CheckBox", "vChkAmber22  x72 y288 w49 h23", "amber")
ogcCheckBoxChkAmber22.OnEvent("Click", GAmber.Bind("Normal"))
hChkAmber22 := ogcCheckBoxChkAmber22.hwnd
ogcCheckBoxChkMultipleMode23 := MainWindowN.Add("CheckBox", "vChkMultipleMode23  x8 y64 w82 h23", "multiple mode")
ogcCheckBoxChkMultipleMode23.OnEvent("Click", GMultipleMode.Bind("Normal"))
hChkMultipleMode23 := ogcCheckBoxChkMultipleMode23.hwnd

MainWindowN.Title := "Auto Appraisal v4"
MainWindowN.Show("w270 h320")

DllCall("SetThreadDpiAwarenessContext", "ptr", -3) ; Needed for multi-monitor setups with differing DPIs

global size := 50, minsize := 5, step := 3
global isTracking := true  ; Flag to control if the box follows the mouse

; Define the list of words to search for
global searchWords := [
    "sparkling", "shiny", "giant", "big", "mythical", "hexed", "abyssal", "electric", 
    "fossilized", "darkened", "translucent", "lunar", "solarblaze", "frozen", "midas", 
    "negative", "glossy", "scorched", "silver", "albino", "mosaic", "amber"
]

counter := 0
SetTimer(TrackMouse,10)

; This function will be called repeatedly by SetTimer
TrackMouse()
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
	counter++
    if (isTracking) {
        MouseGetPos(&x, &y)
        Highlight(x - size // 2, y + 10, size, size)  ; Display box below cursor
        text := OCR.FromRect(x - size // 2, y + 10, size, size, "en-us").Text
		text2 := text
        foundWords := GetFoundWords(text)  ; Get all matching words
        ToolTip("Made by AsphaltCake`nGUI by texture`n`nP: start`nM: exit`nZ: shrink`nX: Expand`nC: lock`n`n" counter "`nRaw Text: " text2 "`nFound Words: " . StrJoin(foundWords, ", "), 50, HalfY - 300)  ; Display found words tooltip at the side
    }
    else {
        Highlight(x - size // 2, y + 10, size, size)  ; Display box below cursor
        text := OCR.FromRect(x - size // 2, y + 10, size, size, "en-us").Text
		text2 := text
        foundWords := GetFoundWords(text)  ; Get all matching words
        ToolTip("Made by AsphaltCake`nGUI by texture`n`nP: start`nM: exit`nZ: shrink`nX: Expand`nC: lock`n`n" counter "`nRaw Text: " text2 "`nFound Words: " . StrJoin(foundWords, ", "), 50, HalfY - 300)  ; Display found words tooltip at the side
    }
    
    ; Update the tooltip showing the state of each variable
    stateTooltip := "sparkling: " . sparkling . "`n"
        . "shiny: " . shiny . "`n"
        . "giant: " . giant . "`n"
        . "big: " . big . "`n"
        . "mythical: " . mythical . "`n"
        . "hexed: " . hexed . "`n"
        . "abyssal: " . abyssal . "`n"
        . "electric: " . electric . "`n"
        . "fossilized: " . fossilized . "`n"
        . "darkened: " . darkened . "`n"
        . "translucent: " . translucent . "`n"
        . "lunar: " . lunar . "`n"
        . "solarblaze: " . solarblaze . "`n"
        . "frozen: " . frozen . "`n"
        . "midas: " . midas . "`n"
        . "negative: " . negative . "`n"
        . "glossy: " . glossy . "`n"
        . "scorched: " . scorched . "`n"
        . "silver: " . silver . "`n"
        . "albino: " . albino . "`n"
        . "mosaic: " . mosaic . "`n"
        . "amber: " . amber
        
    ToolTip(stateTooltip, 50, HalfY, 2)  ; Display state tooltip below the found words tooltip with unique ID

return
} ; V1toV2: Added bracket in the end

m::exitapp
z::global size-=(size > minsize ? step : 0)  ; Smaller with Z
x::global size+=step  ; Bigger with X
o::reload

p::
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
SetTimer(TrackMouse,0)
SetTimer(TrackMouse,10)
MouseGetPos(&origX, &origY)
if (multiple == 0)
{
	returnbruh2:
	Send 1
	Sleep(250)
	Send 4
	Click
	Sleep(2500)
	Loop 10
	{
	TrackMouse()
	}
		
	if (sparkling == 0 or shiny == 0 or giant == 0 or big == 0 or mythical == 0 or hexed == 0 or abyssal == 0 or electric == 0 or fossilized == 0 or darkened == 0 or translucent == 0 or lunar == 0 or solarblaze == 0 or frozen == 0 or midas == 0 or negative == 0 or glossy == 0 or scorched == 0 or silver == 0 or albino == 0 or mosaic == 0 or amber == 0)
	{
	goto returnbruh2
	}
}
else
{
	a2ndsparkling := sparkling
	a2ndshiny := shiny
	a2ndgiant := giant
	a2ndbig := big
	a2ndmythical := mythical
	a2ndhexed := hexed
	a2ndabyssal := abyssal
	a2ndelectric := electric
	a2ndfossilized := fossilized
	a2nddarkened := darkened
	a2ndtranslucent := translucent
	a2ndlunar := lunar
	a2ndsolarblaze := solarblaze
	a2ndfrozen := frozen
	a2ndmidas := midas
	a2ndnegative := negative
	a2ndglossy := glossy
	a2ndscorched := scorched
	a2ndsilver := silver
	a2ndalbino := albino
	a2ndmosaic := mosaic
	a2ndamber := amber
	
	returnbruh:
	Send 1
	Sleep(250)
	Send 4
	Click
	Sleep(2500)
	Loop 10
	{
	TrackMouse()
	}
	
	if (a2ndsparkling == sparkling && a2ndshiny == shiny && a2ndgiant == giant && a2ndbig == big && a2ndmythical == mythical && a2ndhexed == hexed && a2ndabyssal == abyssal && a2ndelectric == electric && a2ndfossilized == fossilized && a2nddarkened == darkened && a2ndtranslucent == translucent && a2ndlunar == lunar && a2ndsolarblaze == solarblaze && a2ndfrozen == frozen && a2ndmidas == midas && a2ndnegative == negative && a2ndglossy == glossy && a2ndscorched == scorched && a2ndsilver == silver && a2ndalbino == albino && a2ndmosaic == mosaic && a2ndamber == amber)
	{
		goto returnbruh
	}
}
return
} ; V1toV2: Added bracket in the end

c:: {
    global isTracking, sparkling, shiny, giant, big, mythical, hexed, abyssal, electric
    global fossilized, darkened, translucent, lunar, solarblaze, frozen, midas, negative
    global glossy, scorched, silver, albino, mosaic, amber

    ; Toggle the tracking
    isTracking := !isTracking
    
    ; Flip the variables based on checkbox values
    sparkling := !ogcCheckBoxChkSparkling.Value
    shiny := !ogcCheckBoxChkShiny2.Value
    giant := !ogcCheckBoxChkGiant3.Value
    big := !ogcCheckBoxChkBig4.Value
    mythical := !ogcCheckBoxChkMythical5.Value
    hexed := !ogcCheckBoxChkHexed14.Value
    abyssal := !ogcCheckBoxChkAbyssal6.Value
    electric := !ogcCheckBoxChkElectric15.Value
    fossilized := !ogcCheckBoxChkFossilized7.Value
    darkened := !ogcCheckBoxChkDarkened16.Value
    translucent := !ogcCheckBoxChkTranslucent17.Value
    lunar := !ogcCheckBoxChkLunar8.Value
    solarblaze := !ogcCheckBoxChkSolarblaze9.Value
    frozen := !ogcCheckBoxChkFrozen18.Value
    midas := !ogcCheckBoxChkMidas10.Value
    negative := !ogcCheckBoxChkNegative19.Value
    glossy := !ogcCheckBoxChkGlossy11.Value
    scorched := !ogcCheckBoxChkScorched20.Value
    silver := !ogcCheckBoxChkSilver12.Value
    albino := !ogcCheckBoxChkAlbino21.Value
    mosaic := !ogcCheckBoxChkMosaic13.Value
    amber := !ogcCheckBoxChkAmber22.Value

    ; Optionally, show a tooltip with the flipped states
    stateTooltip := "sparkling: " . sparkling . "`n"
        . "shiny: " . shiny . "`n"
        . "giant: " . giant . "`n"
        . "big: " . big . "`n"
        . "mythical: " . mythical . "`n"
        . "hexed: " . hexed . "`n"
        . "abyssal: " . abyssal . "`n"
        . "electric: " . electric . "`n"
        . "fossilized: " . fossilized . "`n"
        . "darkened: " . darkened . "`n"
        . "translucent: " . translucent . "`n"
        . "lunar: " . lunar . "`n"
        . "solarblaze: " . solarblaze . "`n"
        . "frozen: " . frozen . "`n"
        . "midas: " . midas . "`n"
        . "negative: " . negative . "`n"
        . "glossy: " . glossy . "`n"
        . "scorched: " . scorched . "`n"
        . "silver: " . silver . "`n"
        . "albino: " . albino . "`n"
        . "mosaic: " . mosaic . "`n"
        . "amber: " . amber
        
    ToolTip(stateTooltip, 50, HalfY, 2)  ; Display the state tooltip
}

; Function to get all found words in the OCR result
GetFoundWords(text) {
    global searchWords, sparkling, shiny, giant, big, mythical, hexed, abyssal, electric
    global fossilized, darkened, translucent, lunar, solarblaze, frozen, midas, negative
    global glossy, scorched, silver, albino, mosaic, amber

    text := StrLower(StrReplace(text, " ", ""))  ; Make text lowercase and remove spaces
    foundWords := []

    for word in searchWords {
        if (InStr(text, word)) {
            foundWords.Push(word)
            ; Set the corresponding variable to 1 when the word is found
            %word% := 1
        }
    }
    
    return foundWords
}

; Function to join array elements into a single string with a separator
StrJoin(arr, separator) {
    result := ""
    for index, item in arr {
        if (result != "") {
            result .= separator
        }
        result .= item
    }
    return result
}

Highlight(x?, y?, w?, h?, showTime:=0, color:="Red", d:=2) {
    static guis := []

    if !IsSet(x) {
        for _, r in guis
            r.Destroy()
        guis := []
        return
    }
    if !guis.Length {
        Loop 4
            guis.Push(Gui("+AlwaysOnTop -Caption +ToolWindow -DPIScale +E0x08000000"))
    }
    Loop 4 {
        i:=A_Index
        , x1:=(i=2 ? x+w : x-d)
        , y1:=(i=3 ? y+h : y-d)
        , w1:=(i=1 or i=3 ? w+2*d : d)
        , h1:=(i=2 or i=4 ? h+2*d : d)
        guis[i].BackColor := color
        guis[i].Show("NA x" . x1 . " y" . y1 . " w" . w1 . " h" . h1)
    }
    if showTime > 0 {
        Sleep(showTime)
        Highlight()
    } else if showTime < 0
        SetTimer(Highlight, -Abs(showTime))
}

Return

GSparkling(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkSparkling := ogcCheckBoxChkSparkling.Value
    sparkling := (ChkSparkling = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GShiny(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkShiny2 := ogcCheckBoxChkShiny2.Value
    shiny := (ChkShiny2 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GGiant(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkGiant3 := ogcCheckBoxChkGiant3.Value
    giant := (ChkGiant3 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GBig(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkBig4 := ogcCheckBoxChkBig4.Value
    big := (ChkBig4 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GMythical(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkMythical5 := ogcCheckBoxChkMythical5.Value
    mythical := (ChkMythical5 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GAbyssal(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkAbyssal6 := ogcCheckBoxChkAbyssal6.Value
    abyssal := (ChkAbyssal6 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GFossilized(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkFossilized7 := ogcCheckBoxChkFossilized7.Value
    fossilized := (ChkFossilized7 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GLunar(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkLunar8 := ogcCheckBoxChkLunar8.Value
    lunar := (ChkLunar8 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GSolarBlaze(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkSolarblaze9 := ogcCheckBoxChkSolarblaze9.Value
    solarblaze := (ChkSolarblaze9 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GMidas(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkMidas10 := ogcCheckBoxChkMidas10.Value
    midas := (ChkMidas10 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GGlossy(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkGlossy11 := ogcCheckBoxChkGlossy11.Value
    glossy := (ChkGlossy11 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GSilver(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkSilver12 := ogcCheckBoxChkSilver12.Value
    silver := (ChkSilver12 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GMosaic(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkMosaic13 := ogcCheckBoxChkMosaic13.Value
    mosaic := (ChkMosaic13 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GHexed(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkHexed14 := ogcCheckBoxChkHexed14.Value
    hexed := (ChkHexed14 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GElectric(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkElectric15 := ogcCheckBoxChkElectric15.Value
    electric := (ChkElectric15 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GDarkened(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkDarkened16 := ogcCheckBoxChkDarkened16.Value
    darkened := (ChkDarkened16 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GTranslucent(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkTranslucent17 := ogcCheckBoxChkTranslucent17.Value
    translucent := (ChkTranslucent17 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GFrozen(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkFrozen18 := ogcCheckBoxChkFrozen18.Value
    frozen := (ChkFrozen18 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GNegative(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkNegative19 := ogcCheckBoxChkNegative19.Value
    negative := (ChkNegative19 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GScorched(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkScorched20 := ogcCheckBoxChkScorched20.Value
    scorched := (ChkScorched20 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GAlbino(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkAlbino21 := ogcCheckBoxChkAlbino21.Value
    albino := (ChkAlbino21 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GAmber(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkAmber22 := ogcCheckBoxChkAmber22.Value
    amber := (ChkAmber22 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

GMultipleMode(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ChkMultipleMode23 := ogcCheckBoxChkMultipleMode23.Value
    multiple := (ChkMultipleMode23 = 0 ? 1 : 0)
    Return
} ; V1toV2: Added Bracket before label

MainWindowLEscape:
MainWindowLClose:
    ExitApp()