#Requires AutoHotkey v2
#include OCR.ahk

CoordMode "Mouse", "Screen"
CoordMode "ToolTip", "Screen"

; Initialize variables to 0
sparkling := 0
shiny := 0
giant := 0
big := 0
mythical := 0
hexed := 0
abyssal := 0
electric := 0
fossilized := 0
darkened := 0
translucent := 0
lunar := 0
solarblaze := 0
frozen := 0
midas := 0
negative := 0
glossy := 0
scorched := 0
silver := 0
albino := 0
mosaic := 0
amber := 0

HalfY := A_ScreenHeight/2

DllCall("SetThreadDpiAwarenessContext", "ptr", -3) ; Needed for multi-monitor setups with differing DPIs

global size := 50, minsize := 5, step := 3
global isTracking := true  ; Flag to control if the box follows the mouse

; Define the list of words to search for
global searchWords := [
    "sparkling", "shiny", "giant", "big", "mythical", "hexed", "abyssal", "electric", 
    "fossilized", "darkened", "translucent", "lunar", "solarblaze", "frozen", "midas", 
    "negative", "glossy", "scorched", "silver", "albino", "mosaic", "amber"
]

Loop {
    if (isTracking) {
        MouseGetPos(&x, &y)
        Highlight(x-size//2, y+10, size, size)  ; Display box below cursor
        text := OCR.FromRect(x-size//2, y+10, size, size, "en-us").Text
        foundWords := GetFoundWords(text)  ; Get all matching words
        ToolTip("Found Words: " . StrJoin(foundWords, ", "), 50, HalfY-50)  ; Display found words tooltip at the side
    }
    else {
        Highlight(x-size//2, y+10, size, size)  ; Display box below cursor
        text := OCR.FromRect(x-size//2, y+10, size, size, "en-us").Text
        foundWords := GetFoundWords(text)  ; Get all matching words
        ToolTip("Found Words: " . StrJoin(foundWords, ", "), 50, HalfY-50)  ; Display found words tooltip at the side
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
}

m::exitapp
z::global size-=(size > minsize ? step : 0)  ; Smaller with Z
x::global size+=step  ; Bigger with X

; Toggle the tracking with C key and reset all variables to 0
c:: {
    global isTracking, sparkling, shiny, giant, big, mythical, hexed, abyssal, electric
    global fossilized, darkened, translucent, lunar, solarblaze, frozen, midas, negative
    global glossy, scorched, silver, albino, mosaic, amber

    ; Toggle the tracking
    isTracking := !isTracking
    
    ; Reset all variables to 0
    sparkling := 0
    shiny := 0
    giant := 0
    big := 0
    mythical := 0
    hexed := 0
    abyssal := 0
    electric := 0
    fossilized := 0
    darkened := 0
    translucent := 0
    lunar := 0
    solarblaze := 0
    frozen := 0
    midas := 0
    negative := 0
    glossy := 0
    scorched := 0
    silver := 0
    albino := 0
    mosaic := 0
    amber := 0
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
