#SingleInstance Force
#Requires AutoHotkey v2
#Requires AutoHotkey v2
class OCR {
static IID_IRandomAccessStream := "{905A0FE1-BC53-11DF-8C49-001E4FC686DA}"
, IID_IPicture            := "{7BF80980-BF32-101A-8BBB-00AA00300CAB}"
, IID_IAsyncInfo          := "{00000036-0000-0000-C000-000000000046}"
, IID_IAsyncOperation_OcrResult        := "{c7d7118e-ae36-59c0-ac76-7badee711c8b}"
, IID_IAsyncOperation_SoftwareBitmap   := "{c4a10980-714b-5501-8da2-dbdacce70f73}"
, IID_IAsyncOperation_BitmapDecoder    := "{aa94d8e9-caef-53f6-823d-91b6e8340510}"
, IID_IAsyncOperationCompletedHandler_OcrResult        := "{989c1371-444a-5e7e-b197-9eaaf9d2829a}"
, IID_IAsyncOperationCompletedHandler_SoftwareBitmap   := "{b699b653-33ed-5e2d-a75f-02bf90e32619}"
, IID_IAsyncOperationCompletedHandler_BitmapDecoder    := "{bb6514f2-3cfb-566f-82bc-60aabd302d53}"
, IID_IPdfDocumentStatics := "{433A0B5F-C007-4788-90F2-08143D922599}"
, Vtbl_GetDecoder := {bmp:6, jpg:7, jpeg:7, png:8, tiff:9, gif:10, jpegxr:11, ico:12}
, PerformanceMode := 0
, DisplayImage := 0
class IBase {
__New(ptr?) {
if IsSet(ptr) && !ptr
throw ValueError('Invalid IUnknown interface pointer', -2, this.__Class)
this.DefineProp("ptr", {Value:ptr ?? 0})
}
__Delete() => this.ptr ? ObjRelease(this.ptr) : 0
}
static __New() {
this.prototype.__OCR := this
this.IBase.prototype.__OCR := this
this.OCRLine.base := this.IBase, this.OCRLine.prototype.base := this.IBase.prototype
this.OCRWord.base := this.IBase, this.OCRWord.prototype.base := this.IBase.prototype
this.LanguageFactory := this.CreateClass("Windows.Globalization.Language", ILanguageFactory := "{9B0252AC-0C27-44F8-B792-9793FB66C63E}")
this.SoftwareBitmapFactory := this.CreateClass("Windows.Graphics.Imaging.SoftwareBitmap", "{c99feb69-2d62-4d47-a6b3-4fdb6a07fdf8}")
this.BitmapTransform := this.CreateClass("Windows.Graphics.Imaging.BitmapTransform")
this.BitmapDecoderStatics := this.CreateClass("Windows.Graphics.Imaging.BitmapDecoder", IBitmapDecoderStatics := "{438CCB26-BCEF-4E95-BAD6-23A822E58D01}")
this.BitmapEncoderStatics := this.CreateClass("Windows.Graphics.Imaging.BitmapEncoder", IBitmapDecoderStatics := "{a74356a7-a4e4-4eb9-8e40-564de7e1ccb2}")
this.SoftwareBitmapStatics := this.CreateClass("Windows.Graphics.Imaging.SoftwareBitmap", ISoftwareBitmapStatics := "{df0385db-672f-4a9d-806e-c2442f343e86}")
this.OcrEngineStatics := this.CreateClass("Windows.Media.Ocr.OcrEngine", IOcrEngineStatics := "{5BFFA85A-3384-3540-9940-699120D428A8}")
ComCall(6, this.OcrEngineStatics, "uint*", &MaxImageDimension:=0)
this.MaxImageDimension := MaxImageDimension
DllCall("Dwmapi\DwmIsCompositionEnabled", "Int*", &compositionEnabled:=0)
this.CAPTUREBLT := compositionEnabled ? 0 : 0x40000000
this.GrayScaleMCode := this.MCode((A_PtrSize = 4)
? "2,x86:VVdWU4PsCIt0JCiLVCQki0QkIMHuAok0JIXSD4SDAAAAhcB0f408tQAAAAAx9ol8JASLfCQcjRyHMf+NdCYAkItEJByNDLiNtCYAAAAAZpCLEYPBBInQD7buwegQae1OAgAAD7bAacAsAQAAAegPtuqB4gAAAP9r7W4B6MHoConFCcLB4AjB5RAJ6gnQiUH8Odl1vIPGAQM8JANcJAQ5dCQkdZyDxAgxwFteX13D"
: "2,x64:QVZVV1ZTRInOSYnLQYnSRYnGwe4CRYXAdHJFMclFMcCF0nRoDx9AAESJyg8fRAAAidCDwgFJjQyDizmJ+In7wegQD7bvD7bAae1OAgAAacAsAQAAAehAD7bvgecAAAD/a+1uAejB6AqJxQnHweAIweUQCe8Jx4k5RDnSdbNBg8ABQQHxQQHyRTnGdZwxwFteX11BXsM=")
this.InvertColorsMCode := this.MCode((A_PtrSize = 4)
? "2,x86:VVdWU4PsCIt8JCiLVCQki0QkIMHvAok8JIXSdF+FwHRbwecCMe2JfCQEi3wkHI00hzH/jXQmAJCLRCQcjQyokIsRg8EEidCJ04Hi/wAA//fQ99OA8v8lAAD/AIHjAP8AAAnYCdCJQfw58XXUg8cBAywkA3QkBDl8JCR1vIPECDHAW15fXcM="
: "2,x64:VVdWU0SJz0iJy0GJ00SJxsHvAkWFwHRbRTHJRTHAhdJ0UWYPH0QAAESJyQ8fRAAAiciDwQFMjRSDQYsSidCJ1YHi/wAA//fQ99WA8v8lAAD/AIHlAP8AAAnoCdBBiQJBOct1zEGDwAFBAflBAftEOcZ1tTHAW15fXcM=")
}
__New(RandomAccessStreamOrSoftwareBitmap, lang := "FirstFromAvailableLanguages", transform := 1, decoder := "") {
local SoftwareBitmap := 0, RandomAccessStream := 0, width, height, x, y, w, h, __OCR := this.__OCR, scale, grayscale, invertcolors
__OCR.__ExtractTransformParameters(RandomAccessStreamOrSoftwareBitmap, &transform)
scale := transform.scale, grayscale := transform.grayscale, invertcolors := transform.invertcolors, rotate := transform.rotate, flip := transform.flip
__OCR.__ExtractNamedParameters(RandomAccessStreamOrSoftwareBitmap, "x", &x, "y", &y, "w", &w, "h", &h, "lang", &lang, "decoder", &decoder, "RandomAccessStream", &RandomAccessStreamOrSoftwareBitmap, "RAS", &RandomAccessStreamOrSoftwareBitmap, "SoftwareBitmap", &RandomAccessStreamOrSoftwareBitmap)
__OCR.LoadLanguage(lang)
try SoftwareBitmap := ComObjQuery(RandomAccessStreamOrSoftwareBitmap, "{689e0708-7eef-483f-963f-da938818e073}")
if SoftwareBitmap {
ComCall(8, SoftwareBitmap, "uint*", &width:=0)
ComCall(9, SoftwareBitmap, "uint*", &height:=0)
this.ImageWidth := width, this.ImageHeight := height
if (Floor(width*scale) > __OCR.MaxImageDimension) or (Floor(height*scale) > __OCR.MaxImageDimension)
throw ValueError("Image is too big - " width "x" height ".`nIt should be maximum - " __OCR.MaxImageDimension " pixels (with scale applied)")
if scale != 1 || IsSet(x) || rotate || flip
SoftwareBitmap := __OCR.TransformSoftwareBitmap(SoftwareBitmap, &width, &height, scale, rotate, flip, x?, y?, w?, h?)
goto SoftwareBitmapCommon
}
RandomAccessStream := RandomAccessStreamOrSoftwareBitmap
if decoder {
ComCall(__OCR.Vtbl_GetDecoder.%decoder%, __OCR.BitmapDecoderStatics, "ptr", DecoderGUID:=Buffer(16))
ComCall(15, __OCR.BitmapDecoderStatics, "ptr", DecoderGUID, "ptr", RandomAccessStream, "ptr*", BitmapDecoder:=ComValue(13,0))
} else
ComCall(14, __OCR.BitmapDecoderStatics, "ptr", RandomAccessStream, "ptr*", BitmapDecoder:=ComValue(13,0))
__OCR.WaitForAsync(&BitmapDecoder)
BitmapFrame := ComObjQuery(BitmapDecoder, IBitmapFrame := "{72A49A1C-8081-438D-91BC-94ECFC8185C6}")
ComCall(12, BitmapFrame, "uint*", &width:=0)
ComCall(13, BitmapFrame, "uint*", &height:=0)
if (width > __OCR.MaxImageDimension) or (height > __OCR.MaxImageDimension)
throw ValueError("Image is too big - " width "x" height ".`nIt should be maximum - " __OCR.MaxImageDimension " pixels")
BitmapFrameWithSoftwareBitmap := ComObjQuery(BitmapDecoder, IBitmapFrameWithSoftwareBitmap := "{FE287C9A-420C-4963-87AD-691436E08383}")
if !IsSet(x) && (width < 40 || height < 40 || scale != 1) {
scale := scale = 1 ? 40.0 / Min(width, height) : scale, this.ImageWidth := Floor(width*scale), this.ImageHeight := Floor(height*scale)
ComCall(7, __OCR.BitmapTransform, "int", this.ImageWidth)
ComCall(9, __OCR.BitmapTransform, "int", this.ImageHeight)
ComCall(8, BitmapFrame, "uint*", &BitmapPixelFormat:=0)
ComCall(9, BitmapFrame, "uint*", &BitmapAlphaMode:=0)
ComCall(8, BitmapFrameWithSoftwareBitmap, "uint", BitmapPixelFormat, "uint", BitmapAlphaMode, "ptr", __OCR.BitmapTransform, "uint", IgnoreExifOrientation := 0, "uint", DoNotColorManage := 0, "ptr*", SoftwareBitmap:=ComValue(13,0))
} else {
this.ImageWidth := width, this.ImageHeight := height
ComCall(6, BitmapFrameWithSoftwareBitmap, "ptr*", SoftwareBitmap:=ComValue(13,0))
}
__OCR.WaitForAsync(&SoftwareBitmap)
if IsSet(x) || rotate || flip
SoftwareBitmap := __OCR.TransformSoftwareBitmap(SoftwareBitmap, &width, &height, scale, rotate, flip, x?, y?, w?, h?)
SoftwareBitmapCommon:
if (grayscale || invertcolors || __OCR.DisplayImage) {
ComCall(15, SoftwareBitmap, "int", 2, "ptr*", BitmapBuffer := ComValue(13,0))
MemoryBuffer := ComObjQuery(BitmapBuffer, "{fbc4dd2a-245b-11e4-af98-689423260cf8}")
ComCall(6, MemoryBuffer, "ptr*", MemoryBufferReference := ComValue(13,0))
BufferByteAccess := ComObjQuery(MemoryBufferReference, "{5b0d3235-4dba-4d44-865e-8f1d0e4fd04d}")
ComCall(3, BufferByteAccess, "ptr*", &SoftwareBitmapByteBuffer:=0, "uint*", &BufferSize:=0)
if invertcolors
DllCall(__OCR.InvertColorsMCode, "ptr", SoftwareBitmapByteBuffer, "uint", width, "uint", height, "uint", (width*4+3) // 4 * 4, "cdecl uint")
if grayscale
DllCall(__OCR.GrayScaleMCode, "ptr", SoftwareBitmapByteBuffer, "uint", width, "uint", height, "uint", (width*4+3) // 4 * 4, "cdecl uint")
if __OCR.DisplayImage {
local hdc := DllCall("GetDC", "ptr", 0, "ptr"), bi := Buffer(40, 0), hbm
NumPut("uint", 40, "int", width, "int", -height, "ushort", 1, "ushort", 32, bi)
hbm := DllCall("CreateDIBSection", "ptr", hdc, "ptr", bi, "uint", 0, "ptr*", &ppvBits:=0, "ptr", 0, "uint", 0, "ptr")
DllCall("ntdll\memcpy", "ptr", ppvBits, "ptr", SoftwareBitmapByteBuffer, "uint", BufferSize, "cdecl")
__OCR.DisplayHBitmap(hbm)
}
BufferByteAccess := "", MemoryBufferReference := "", MemoryBuffer := "", BitmapBuffer := ""
}
ComCall(6, __OCR.OcrEngine, "ptr", SoftwareBitmap, "ptr*", OcrResult:=ComValue(13,0))
__OCR.WaitForAsync(&OcrResult)
this.ptr := OcrResult.ptr, ObjAddRef(OcrResult.ptr)
if RandomAccessStream is __OCR.IBase
__OCR.CloseIClosable(RandomAccessStream)
if SoftwareBitmap is __OCR.IBase
__OCR.CloseIClosable(SoftwareBitmap)
if scale != 1
__OCR.NormalizeCoordinates(this, scale)
}
__Delete() => this.ptr ? ObjRelease(this.ptr) : 0
Text {
get {
ComCall(8, this, "ptr*", &hAllText:=0)
buf := DllCall("Combase.dll\WindowsGetStringRawBuffer", "ptr", hAllText, "uint*", &length:=0, "ptr")
this.DefineProp("Text", {Value:StrGet(buf, "UTF-16")})
this.__OCR.DeleteHString(hAllText)
return this.Text
}
}
TextAngle {
get => (ComCall(7, this, "double*", &value:=0), value)
}
Lines {
get {
ComCall(6, this, "ptr*", LinesList:=this.__OCR.IBase())
ComCall(7, LinesList, "int*", &count:=0)
lines := []
loop count {
ComCall(6, LinesList, "int", A_Index-1, "ptr*", OcrLine:=this.__OCR.OCRLine())
lines.Push(OcrLine)
}
this.DefineProp("Lines", {Value:lines})
return lines
}
}
Words {
get {
local words := [], line, word
for line in this.Lines
for word in line.Words
words.Push(word)
this.DefineProp("Words", {Value:words})
return words
}
}
Click(Obj, WhichButton?, ClickCount?, DownOrUp?) {
if !obj.HasProp("x") && InStr(Type(obj), "OCR")
obj := this.__OCR.WordsBoundingRect(obj.Words)
local x := obj.x, y := obj.y, w := obj.w, h := obj.h, mode := "Screen", hwnd
if this.HasProp("Relative") {
if this.Relative.HasOwnProp("Window")
mode := "Window", hwnd := this.Relative.Window.Hwnd
else if this.Relative.HasOwnProp("Client")
mode := "Client", hwnd := this.Relative.Client.Hwnd
if IsSet(hwnd) && !WinActive(hwnd) {
WinActivate(hwnd)
WinWaitActive(hwnd,,1)
}
x += this.Relative.%mode%.x, y += this.Relative.%mode%.y
}
oldCoordMode := A_CoordModeMouse
CoordMode "Mouse", mode
Click(x+w//2, y+h//2, WhichButton?, ClickCount?, DownOrUp?)
CoordMode "Mouse", oldCoordMode
}
ControlClick(obj, WinTitle?, WinText?, WhichButton?, ClickCount?, Options?, ExcludeTitle?, ExcludeText?) {
if !obj.HasProp("x") && InStr(Type(obj), "OCR")
obj := this.__OCR.WordsBoundingRect(obj.Words)
local x := obj.x, y := obj.y, w := obj.w, h := obj.h, hWnd
if this.HasProp("Relative") && (this.Relative.HasOwnProp("Client") || this.Relative.HasOwnProp("Window")) {
mode := this.Relative.HasOwnProp("Client") ? "Client" : "Window"
, obj := this.Relative.%mode%, x += obj.x, y += obj.y, hWnd := obj.hWnd
if mode = "Window" {
RECT := Buffer(16, 0), pt := Buffer(8, 0)
DllCall("user32\GetWindowRect", "Ptr", hWnd, "Ptr", RECT)
winX := NumGet(RECT, 0, "Int"), winY := NumGet(RECT, 4, "Int")
NumPut("int", winX+x, "int", winY+y, pt)
DllCall("user32\ScreenToClient", "Ptr", hWnd, "Ptr", pt)
x := NumGet(pt,0,"int"), y := NumGet(pt,4,"int")
}
} else if IsSet(WinTitle) {
hWnd := WinExist(WinTitle, WinText?, ExcludeTitle?, ExcludeText?)
pt := Buffer(8), NumPut("int",x,pt), NumPut("int", y,pt,4)
DllCall("ScreenToClient", "Int", Hwnd, "Ptr", pt)
x := NumGet(pt,0,"int"), y := NumGet(pt,4,"int")
} else
throw TargetError("ControlClick needs to be called either after a OCR.FromWindow result or with a WinTitle argument")
ControlClick("X" (x+w//2) " Y" (y+h//2), hWnd,, WhichButton?, ClickCount?, Options?)
}
Highlight(obj?, showTime?, color:="Red", d:=2) {
static Guis := Map()
local x, y, w, h, key, resultObjs, key2, oObj, rect, ResultGuis, GuiObj, iw, ih
if IsSet(showTime) && showTime = "clearall" {
for key, resultObjs in Guis {
for key2, oObj in resultObjs {
try oObj.GuiObj.Destroy()
SetTimer(oObj.TimerObj, 0)
}
}
Guis := Map()
return this
}
if !Guis.Has(this.ptr)
Guis[this.ptr] := Map()
if !IsSet(obj) {
for key, oObj in Guis[this.ptr] {
try oObj.GuiObj.Destroy()
SetTimer(oObj.TimerObj, 0)
}
Guis.Delete(this.ptr)
return this
}
if !IsObject(obj)
throw ValueError("First argument 'obj' must be an object", -1)
ResultGuis := Guis[this.ptr]
if (!IsSet(showTime) && ResultGuis.Has(obj)) || (IsSet(showTime) && showTime = "clear") {
try ResultGuis[obj].GuiObj.Destroy()
SetTimer(ResultGuis[obj].TimerObj, 0)
ResultGuis.Delete(obj)
return this
} else if !IsSet(showTime)
showTime := 2000
if Type(obj) = this.__OCR.prototype.__Class ".OCRLine" || Type(obj) = this.__OCR.prototype.__Class
rect := this.__OCR.WordsBoundingRect(obj.Words*)
else
rect := obj
x := rect.x, y := rect.y, w := rect.w, h := rect.h
if this.HasProp("Relative") {
if this.Relative.HasOwnProp("Client")
WinGetClientPos(&rX, &rY,,, this.Relative.Client.hWnd), x += rX + this.Relative.Client.x, y += rY + this.Relative.Client.y
else if this.Relative.HasOwnProp("Window")
WinGetPos(&rX, &rY,,, this.Relative.Window.hWnd), x += rX + this.Relative.Window.x, y += rY + this.Relative.Window.y
else if this.Relative.HasOwnProp("Screen")
x += this.Relative.Screen.X, y += this.Relative.Screen.Y
}
if !ResultGuis.Has(obj) {
ResultGuis[obj] := {}
ResultGuis[obj].GuiObj := Gui("+AlwaysOnTop -Caption +ToolWindow -DPIScale +E0x08000000")
ResultGuis[obj].TimerObj := ObjBindMethod(this, "Highlight", obj, "clear")
}
GuiObj := ResultGuis[obj].GuiObj
GuiObj.BackColor := color
iw:= w+d, ih:= h+d, w:=w+d*2, h:=h+d*2, x:=x-d, y:=y-d
WinSetRegion("0-0 " w "-0 " w "-" h " 0-" h " 0-0 " d "-" d " " iw "-" d " " iw "-" ih " " d "-" ih " " d "-" d, GuiObj.Hwnd)
GuiObj.Show("NA x" . x . " y" . y . " w" . w . " h" . h)
if showTime > 0 {
Sleep(showTime)
this.Highlight(obj)
} else if showTime < 0
SetTimer(ResultGuis[obj].TimerObj, -Abs(showTime))
return this
}
ClearHighlight(obj) => this.Highlight(obj, "clear")
static ClearAllHighlights() => this.Prototype.Highlight(,"clearall")
FindString(needle, i:=1, casesense:=False, wordCompareFunc?, searchArea?) {
local line, counter, found, x1, y1, x2, y2, splitNeedle, result, word
if !(needle is String)
throw TypeError("Needle is required to be a string, not type " Type(needle), -1)
if needle == ""
throw ValueError("Needle cannot be an empty string", -1)
splitNeedle := StrSplit(RegExReplace(needle, " +", " "), " "), needleLen := splitNeedle.Length
if !IsSet(wordCompareFunc)
wordCompareFunc := casesense ? ((arg1, arg2) => arg1 == arg2) : ((arg1, arg2) => arg1 = arg2)
If IsSet(searchArea) {
x1 := searchArea.HasOwnProp("x1") ? searchArea.x1 : -100000
y1 := searchArea.HasOwnProp("y1") ? searchArea.y1 : -100000
x2 := searchArea.HasOwnProp("x2") ? searchArea.x2 : 100000
y2 := searchArea.HasOwnProp("y2") ? searchArea.y2 : 100000
}
for line in this.Lines {
if IsSet(wordCompareFunc) || InStr(l := line.Text, needle, casesense) {
counter := 0, found := []
for word in line.Words {
If IsSet(searchArea) && (word.x < x1 || word.y < y1 || word.x+word.w > x2 || word.y+word.h > y2)
continue
t := word.Text, len := StrLen(t)
if wordCompareFunc(t, splitNeedle[found.Length+1]) {
found.Push(word)
if found.Length == needleLen {
if ++counter == i {
result := this.__OCR.WordsBoundingRect(found*)
result.Words := found
return result
} else
found := []
}
} else
found := []
}
}
}
throw TargetError('The target string "' needle '" was not found', -1)
}
FindStrings(needle, casesense:=False, wordCompareFunc?, searchArea?) {
local line, counter, found, x1, y1, x2, y2, splitNeedle, result, word
if !(needle is String)
throw TypeError("Needle is required to be a string, not type " Type(needle), -1)
if needle == ""
throw ValueError("Needle cannot be an empty string", -1)
splitNeedle := StrSplit(RegExReplace(needle, " +", " "), " "), needleLen := splitNeedle.Length
if !IsSet(wordCompareFunc)
wordCompareFunc := casesense ? ((arg1, arg2) => arg1 == arg2) : ((arg1, arg2) => arg1 = arg2)
If IsSet(searchArea) {
x1 := searchArea.HasOwnProp("x1") ? searchArea.x1 : -100000
y1 := searchArea.HasOwnProp("y1") ? searchArea.y1 : -100000
x2 := searchArea.HasOwnProp("x2") ? searchArea.x2 : 100000
y2 := searchArea.HasOwnProp("y2") ? searchArea.y2 : 100000
}
results := []
for line in this.Lines {
if IsSet(wordCompareFunc) || InStr(l := line.Text, needle, casesense) {
counter := 0, found := []
for word in line.Words {
If IsSet(searchArea) && (word.x < x1 || word.y < y1 || word.x+word.w > x2 || word.y+word.h > y2)
continue
t := word.Text, len := StrLen(t)
if wordCompareFunc(t, splitNeedle[found.Length+1]) {
found.Push(word)
if found.Length == needleLen {
result := this.__OCR.WordsBoundingRect(found*)
result.Words := found
results.Push(result)
counter := 0, found := [], result := unset
}
} else
found := []
}
}
}
return results
}
Filter(callback) {
if !HasMethod(callback)
throw ValueError("Filter callback must be a function", -1)
local result := this.Clone(), line, croppedLines := [], croppedText := "", croppedWords := [], lineText := "", word
ObjAddRef(result.ptr)
for line in result.Lines {
croppedWords := [], lineText := ""
for word in line.Words {
if callback(word)
croppedWords.Push(word), lineText .= word.Text " "
}
if croppedWords.Length {
line := {Text:Trim(lineText), Words:croppedWords}
line.base.__Class := this.__OCR.prototype.__Class ".OCRLine"
croppedLines.Push(line)
croppedText .= lineText
}
}
result.DefineProp("Lines", {Value:croppedLines})
result.DefineProp("Text", {Value:Trim(croppedText)})
result.DefineProp("Words", this.__OCR.Prototype.GetOwnPropDesc("Words"))
return result
}
Crop(x1:=-100000, y1:=-100000, x2:=100000, y2:=100000) => this.Filter((word) => word.x >= x1 && word.y >= y1 && (word.x+word.w) <= x2 && (word.y+word.h) <= y2)
class OCRLine {
Text {
get {
ComCall(7, this, "ptr*", &hText:=0)
buf := DllCall("Combase.dll\WindowsGetStringRawBuffer", "ptr", hText, "uint*", &length:=0, "ptr")
text := StrGet(buf, "UTF-16")
this.__OCR.DeleteHString(hText)
this.DefineProp("Text", {Value:text})
return text
}
}
Words {
get {
ComCall(6, this, "ptr*", WordsList:=this.__OCR.IBase())
ComCall(7, WordsList, "int*", &WordsCount:=0)
words := []
loop WordsCount {
ComCall(6, WordsList, "int", A_Index-1, "ptr*", OcrWord:=this.__OCR.OCRWord())
words.Push(OcrWord)
}
this.DefineProp("Words", {Value:words})
return words
}
}
BoundingRect {
get => this.DefineProp("BoundingRect", {Value:this.__OCR.WordsBoundingRect(this.Words*)}).BoundingRect
}
x {
get => this.BoundingRect.x
}
y {
get => this.BoundingRect.y
}
w {
get => this.BoundingRect.w
}
h {
get => this.BoundingRect.h
}
}
class OCRWord {
Text {
get {
ComCall(7, this, "ptr*", &hText:=0)
buf := DllCall("Combase.dll\WindowsGetStringRawBuffer", "ptr", hText, "uint*", &length:=0, "ptr")
text := StrGet(buf, "UTF-16")
this.__OCR.DeleteHString(hText)
this.DefineProp("Text", {Value:text})
return text
}
}
BoundingRect {
get {
ComCall(6, this, "ptr", RECT := Buffer(16, 0))
this.DefineProp("x", {Value:Integer(NumGet(RECT, 0, "float"))})
, this.DefineProp("y", {Value:Integer(NumGet(RECT, 4, "float"))})
, this.DefineProp("w", {Value:Integer(NumGet(RECT, 8, "float"))})
, this.DefineProp("h", {Value:Integer(NumGet(RECT, 12, "float"))})
return this.DefineProp("BoundingRect", {Value:{x:this.x, y:this.y, w:this.w, h:this.h}}).BoundingRect
}
}
x {
get => this.BoundingRect.x
}
y {
get => this.BoundingRect.y
}
w {
get => this.BoundingRect.w
}
h {
get => this.BoundingRect.h
}
}
static FromFile(FileName, lang?, transform:=1) {
this.__ExtractTransformParameters(FileName, &transform)
this.__ExtractNamedParameters(FileName, "lang", &lang, "FileName", &FileName)
if !(fe := FileExist(FileName)) or InStr(fe, "D")
throw TargetError("File `"" FileName "`" doesn't exist", -1)
GUID := this.CLSIDFromString(this.IID_IRandomAccessStream)
DllCall("ShCore\CreateRandomAccessStreamOnFile", "wstr", FileName, "uint", Read := 0, "ptr", GUID, "ptr*", IRandomAccessStream:=this.IBase())
return this(IRandomAccessStream, lang?, transform, this.Vtbl_GetDecoder.HasOwnProp(ext := StrSplit(FileName, ".")[-1]) ? ext : "")
}
static FromPDF(FileName, lang?, transform:=1, start:=1, end?) {
this.__ExtractTransformParameters(FileName, &transform)
this.__ExtractNamedParameters(FileName, "lang", &lang, "start", &start, "end", &end, "FileName", &FileName)
if !(fe := FileExist(FileName)) or InStr(fe, "D")
throw TargetError("File `"" FileName "`" doesn't exist", -1)
DllCall("ShCore\CreateRandomAccessStreamOnFile", "wstr", FileName, "uint", Read := 0, "ptr", GUID := this.CLSIDFromString(this.IID_IRandomAccessStream), "ptr*", IRandomAccessStream:=ComValue(13,0))
PdfDocumentStatics := this.CreateClass("Windows.Data.Pdf.PdfDocument", this.IID_IPdfDocumentStatics)
ComCall(8, PdfDocumentStatics, "ptr", IRandomAccessStream, "ptr*", PdfDocument:=this.IBase())
this.WaitForAsync(&PdfDocument)
this.CloseIClosable(IRandomAccessStream)
if !IsSet(end) {
ComCall(7, PdfDocument, "uint*", &end:=0)
if !end
throw Error("Unable to get PDF page count", -1)
}
local results := []
Loop (end+1-start)
results.Push(this.FromPDFPage(PdfDocument, start+(A_Index-1), lang?, transform))
return results
}
static FromPDFPage(FileName, page:=1, lang?, transform:=1) {
this.__ExtractTransformParameters(FileName, &transform)
this.__ExtractNamedParameters(FileName, "page", page, "lang", &lang, "FileName", &FileName)
if FileName is String {
if !(fe := FileExist(FileName)) or InStr(fe, "D")
throw TargetError("File `"" FileName "`" doesn't exist", -1)
GUID := OCR.CLSIDFromString(OCR.IID_IRandomAccessStream)
DllCall("ShCore\CreateRandomAccessStreamOnFile", "wstr", FileName, "uint", Read := 0, "ptr", GUID, "ptr*", IRandomAccessStream:=OCR.IBase())
PdfDocumentStatics := this.CreateClass("Windows.Data.Pdf.PdfDocument", this.IID_IPdfDocumentStatics)
ComCall(8, PdfDocumentStatics, "ptr", IRandomAccessStream, "ptr*", PdfDocument:=this.IBase())
this.WaitForAsync(&PdfDocument)
} else
PdfDocument := FileName
ComCall(6, PdfDocument, "uint", page-1, "ptr*", PdfPage:=this.IBase())
InMemoryRandomAccessStream := this.CreateClass("Windows.Storage.Streams.InMemoryRandomAccessStream")
ComCall(6, PdfPage, "ptr", InMemoryRandomAccessStream, "ptr*", asyncInfo:=this.IBase())
this.WaitForAsync(&asyncInfo)
if FileName is String
this.CloseIClosable(IRandomAccessStream)
PdfPage := "", PdfDocument := "", IRandomAccessStream := ""
return this(InMemoryRandomAccessStream, lang?, transform)
}
static FromWindow(WinTitle:="", lang?, transform:=1, onlyClientArea:=0, mode:=4) {
this.__ExtractTransformParameters(WinTitle, &transform)
local result, X := 0, Y := 0, W := 0, H := 0, sX, sY, hBitMap, hwnd, customRect := 0, scale := transform.scale
this.__ExtractNamedParameters(WinTitle, "x", &x, "y", &y, "w", &w, "h", &h, "onlyClientArea", &onlyClientArea, "mode", &mode, "lang", &lang, "WinTitle", &Wintitle)
this.__ExtractNamedParameters(onlyClientArea, "x", &x, "y", &y, "w", &w, "h", &h, "onlyClientArea", &onlyClientArea)
if (x !=0 || y != 0 || w != 0 || h != 0)
customRect := 1
if IsObject(WinTitle)
WinTitle := ""
if !(hWnd := WinExist(WinTitle))
throw TargetError("Target window not found", -1)
if DllCall("IsIconic", "uptr", hwnd)
DllCall("ShowWindow", "uptr", hwnd, "int", 4)
if mode < 4 && mode&1 {
oldStyle := WinGetExStyle(hwnd), i := 0
WinSetTransparent(255, hwnd)
While (WinGetTransparent(hwnd) != 255 && ++i < 30)
Sleep 100
}
WinGetPos(&wX, &wY, &wW, &wH, hWnd)
If onlyClientArea = 1 {
WinGetClientPos(&cX, &cY, &cW, &cH, hWnd)
W := W || cW, H := H || cH, sX := X + cX, sY := Y + cY
} else {
W := W || wW, H := H || wH, sX := X + wX, sY := Y + wY
}
if mode = 5 {
SoftwareBitmap := this.CreateDirect3DSoftwareBitmapFromWindow(hWnd)
local offsetX := 0, offsetY := 0, sbW := SoftwareBitmap.W, sbH := SoftwareBitmap.H, sbX := SoftwareBitmap.X, sbY := SoftwareBitmap.Y
if scale != 1 || transform.rotate || transform.flip || customRect || onlyClientArea {
local tX := X, tY := Y, tW := W, tH := H
if onlyClientArea
tX -= SoftwareBitmap.X-cX, tY -= SoftwareBitmap.Y-cY
else
tX -= SoftwareBitmap.X-wX, tY -= SoftwareBitmap.Y-wY
if tX < 0
tW += tX, offsetX := -tX, tX := 0
if tY < 0
tH += tY, offsetY := -tY, tY := 0
tW := Min(sbW-tX, tW), tH := Min(sbH-tY, tH)
SoftwareBitmap := this.TransformSoftwareBitmap(SoftwareBitmap, &sbW, &sbH, scale, transform.rotate, transform.flip, tX, tY, tW, tH)
transform.scale := 1, transform.rotate := 0, transform.flip := 0
}
result := this(SoftwareBitmap, lang?, transform)
} else {
hBitMap := this.CreateHBitmap(X, Y, W, H, {hWnd:hWnd, onlyClientArea:onlyClientArea, mode:(mode//2)}, scale)
if mode&1
WinSetExStyle(oldStyle, hwnd)
result := this(this.HBitmapToSoftwareBitmap(hBitMap,, transform), lang?)
}
result.Relative := {Screen:{X:sX, Y:sY, W:W, H:H}}
, result.Relative.%(onlyClientArea = 1 ? "Client" : "Window")% := {X:X, Y:Y, W:W, H:H, hWnd:hWnd}
this.NormalizeCoordinates(result, scale)
if mode = 5 && !onlyClientArea
result.OffsetCoordinates(offsetX, offsetY)
return result
}
static FromDesktop(lang?, transform:=1, monitor?) {
if IsSet(lang) {
this.__ExtractTransformParameters(lang, &transform)
lang := lang.HasProp("lang") ? lang : unset
}
MonitorGet(monitor?, &Left, &Top, &Right, &Bottom)
return this.FromRect(Left, Top, Right-Left, Bottom-Top, lang?, transform)
}
static FromRect(x, y?, w?, h?, lang?, transform:=1) {
this.__ExtractTransformParameters(x, &transform)
this.__ExtractNamedParameters(x, "y", &y, "w", &w, "h", &h, "lang", &lang, "x", &x)
local scale := transform.scale
, hBitmap := this.CreateHBitmap(X, Y, W, H,, scale)
, result := this(this.HBitmapToSoftwareBitmap(hBitmap,, transform), lang?)
result.Relative := {Screen:{x:x, y:y, w:w, h:h}}
return this.NormalizeCoordinates(result, scale)
}
static FromBitmap(bitmap, lang?, transform:=1, hDC?) {
this.__ExtractTransformParameters(bitmap, &transform)
local result, pDC, hBitmap, hBM2, oBM, oBM2, pBitmapInfo := Buffer(32, 0), W, H, scale := transform.scale
this.__ExtractNamedParameters(bitmap, "hDC", &hDC, "lang", &lang, "hBitmap", &bitmap, "pBitmap", &bitmap, "bitmap", &bitmap)
if !DllCall("GetObject", "ptr", bitmap, "int", pBitmapInfo.Size, "ptr", pBitmapInfo) {
DllCall("gdiplus\GdipCreateHBITMAPFromBitmap", "UPtr", bitmap, "UPtr*", &hBitmap:=0, "Int", 0xffffffff)
DllCall("GetObject", "ptr", hBitmap, "int", pBitmapInfo.Size, "ptr", pBitmapInfo)
} else
hBitmap := bitmap
W := NumGet(pBitmapInfo, 4, "int"), H := NumGet(pBitmapInfo, 8, "int")
if scale != 1 || (W && H && (W < 40 || H < 40)) {
sW := Ceil(W * scale), sH := Ceil(H * scale)
hDC := DllCall("CreateCompatibleDC", "Ptr", 0, "Ptr")
, oBM := DllCall("SelectObject", "Ptr", hDC, "Ptr", hBitmap, "Ptr")
, pDC := DllCall("CreateCompatibleDC", "Ptr", hDC, "Ptr")
, hBM2 := DllCall("CreateCompatibleBitmap", "Ptr", hDC, "Int", Max(40, sW), "Int", Max(40, sH), "Ptr")
, oBM2 := DllCall("SelectObject", "Ptr", pDC, "Ptr", hBM2, "Ptr")
if sW < 40 || sH < 40
DllCall("StretchBlt", "Ptr", pDC, "Int", 0, "Int", 0, "Int", Max(40,sW), "Int", Max(40,sH), "Ptr", hDC, "Int", 0, "Int", 0, "Int", 1, "Int", 1, "UInt", 0x00CC0020 | this.CAPTUREBLT)
PrevStretchBltMode := DllCall("SetStretchBltMode", "Ptr", PDC, "Int", 3, "Int")
, DllCall("StretchBlt", "Ptr", pDC, "Int", 0, "Int", 0, "Int", sW, "Int", sH, "Ptr", hDC, "Int", 0, "Int", 0, "Int", W, "Int", H, "UInt", 0x00CC0020 | this.CAPTUREBLT)
, DllCall("SetStretchBltMode", "Ptr", PDC, "Int", PrevStretchBltMode)
, DllCall("SelectObject", "Ptr", pDC, "Ptr", oBM2)
, DllCall("SelectObject", "Ptr", hDC, "Ptr", oBM)
, DllCall("DeleteDC", "Ptr", hDC)
result := this(this.HBitmapToSoftwareBitmap(hBM2, pDC, transform), lang?)
this.NormalizeCoordinates(result, scale)
DllCall("DeleteDC", "Ptr", pDC)
, DllCall("DeleteObject", "UPtr", hBM2)
return result
}
return this(this.HBitmapToSoftwareBitmap(hBitmap, hDC?, transform), lang?)
}
static GetAvailableLanguages() {
ComCall(7, this.OcrEngineStatics, "ptr*", &LanguageList := 0)
ComCall(7, LanguageList, "int*", &count := 0)
Loop count {
ComCall(6, LanguageList, "int", A_Index - 1, "ptr*", &Language := 0)
ComCall(6, Language, "ptr*", &hText := 0)
buf := DllCall("Combase.dll\WindowsGetStringRawBuffer", "ptr", hText, "uint*", &length := 0, "ptr")
text .= StrGet(buf, "UTF-16") "`n"
this.DeleteHString(hText)
ObjRelease(Language)
}
ObjRelease(LanguageList)
return text
}
static LoadLanguage(lang:="FirstFromAvailableLanguages") {
local hString, Language:=this.IBase(), OcrEngine:=this.IBase()
if this.HasOwnProp("CurrentLanguage") && this.HasOwnProp("OcrEngine") && this.CurrentLanguage = lang
return
if (lang = "FirstFromAvailableLanguages")
ComCall(10, this.OcrEngineStatics, "ptr*", OcrEngine)
else {
hString := this.CreateHString(lang)
, ComCall(6, this.LanguageFactory, "ptr", hString, "ptr*", Language)
, this.DeleteHString(hString)
, ComCall(9, this.OcrEngineStatics, "ptr", Language, "ptr*", OcrEngine)
}
if (OcrEngine.ptr = 0)
Throw Error(lang = "FirstFromAvailableLanguages" ? "Failed to use FirstFromAvailableLanguages for OCR:`nmake sure the primary language pack has OCR capabilities installed.`n`nAlternatively try `"en-us`" as the language." : "Can not use language `"" lang "`" for OCR, please install language pack.")
this.OcrEngine := OcrEngine, this.CurrentLanguage := lang
}
static WordsBoundingRect(words*) {
if !words.Length
throw ValueError("This function requires at least one argument")
local X1 := 100000000, Y1 := 100000000, X2 := -100000000, Y2 := -100000000, word
for word in words {
X1 := Min(word.x, X1), Y1 := Min(word.y, Y1), X2 := Max(word.x+word.w, X2), Y2 := Max(word.y+word.h, Y2)
}
return {X:X1, Y:Y1, W:X2-X1, H:Y2-Y1, X2:X2, Y2:Y2}
}
static WaitText(needle, timeout:=-1, func?, casesense:=False, comparefunc?) {
local endTime := A_TickCount+timeout, result, line, total
if !IsSet(func)
func := this.FromDesktop
if !IsSet(comparefunc)
comparefunc := InStr.Bind(,,casesense)
While timeout > 0 ? (A_TickCount < endTime) : 1 {
result := func(), total := ""
for line in result.Lines
total .= line.Text "`n"
if comparefunc(Trim(total, "`n"), needle)
return result
}
return
}
static Cluster(objs, eps_x:=-1, eps_y:=-1, minPts:=1, compareFunc?, &noise?) {
local clusters := [], start := 0, cluster, word
visited := Map(), clustered := Map(), C := [], c_n := 0, sum := 0, noise := IsSet(noise) && (noise is Array) ? noise : []
if !IsObject(objs) || !(objs is Array)
throw ValueError("objs argument must be an Array", -1)
if !objs.Length
return []
if IsSet(compareFunc) && !HasMethod(compareFunc)
throw ValueError("compareFunc must be a valid function", -1)
if !IsSet(compareFunc) {
if (eps_y < 0) {
for point in objs
sum += point.h
eps_y := (sum // objs.Length) // 2
}
compareFunc := (p1, p2) => Abs(p1.y+p1.h//2-p2.y-p2.h//2)<eps_y && (eps_x < 0 || (Abs(p1.x+p1.w-p2.x)<eps_x || Abs(p1.x-p2.x-p2.w)<eps_x))
}
for point in objs {
visited[point] := 1, neighbourPts := [], RegionQuery(point)
if !clustered.Has(point) {
C.Push([]), c_n += 1, C[c_n].Push(point), clustered[point] := 1
ExpandCluster(point)
}
if C[c_n].Length < minPts
noise.Push(C[c_n]), C.RemoveAt(c_n), c_n--
}
for cluster in C {
OCR.SortArray(cluster,,"x")
br := OCR.WordsBoundingRect(cluster*), br.Words := cluster, br.Text := ""
for word in cluster
br.Text .= word.Text " "
br.Text := RTrim(br.Text)
clusters.Push(br)
}
OCR.SortArray(clusters,,"y")
return clusters
ExpandCluster(P) {
local point
for point in neighbourPts {
if !visited.Has(point) {
visited[point] := 1, RegionQuery(point)
if !clustered.Has(point)
C[c_n].Push(point), clustered[point] := 1
}
}
}
RegionQuery(P) {
local point
for point in objs
if !visited.Has(point)
if compareFunc(P, point)
neighbourPts.Push(point)
}
}
static SortArray(arr, optionsOrCallback:="N", key?) {
static sizeofFieldType := 16
if HasMethod(optionsOrCallback)
pCallback := CallbackCreate(CustomCompare.Bind(optionsOrCallback), "F Cdecl", 2), optionsOrCallback := ""
else {
if InStr(optionsOrCallback, "N")
pCallback := CallbackCreate(IsSet(key) ? NumericCompareKey.Bind(key) : NumericCompare, "F CDecl", 2)
if RegExMatch(optionsOrCallback, "i)C(?!0)|C1|COn")
pCallback := CallbackCreate(IsSet(key) ? StringCompareKey.Bind(key,,True) : StringCompare.Bind(,,True), "F CDecl", 2)
if RegExMatch(optionsOrCallback, "i)C0|COff")
pCallback := CallbackCreate(IsSet(key) ? StringCompareKey.Bind(key) : StringCompare, "F CDecl", 2)
if InStr(optionsOrCallback, "Random")
pCallback := CallbackCreate(RandomCompare, "F CDecl", 2)
if !IsSet(pCallback)
throw ValueError("No valid options provided!", -1)
}
mFields := NumGet(ObjPtr(arr) + (8 + (VerCompare(A_AhkVersion, "<2.1-") > 0 ? 3 : 5)*A_PtrSize), "Ptr")
DllCall("msvcrt.dll\qsort", "Ptr", mFields, "UInt", arr.Length, "UInt", sizeofFieldType, "Ptr", pCallback, "Cdecl")
CallbackFree(pCallback)
if RegExMatch(optionsOrCallback, "i)R(?!a)")
this.ReverseArray(arr)
if InStr(optionsOrCallback, "U")
arr := this.Unique(arr)
return arr
CustomCompare(compareFunc, pFieldType1, pFieldType2) => (ValueFromFieldType(pFieldType1, &fieldValue1), ValueFromFieldType(pFieldType2, &fieldValue2), compareFunc(fieldValue1, fieldValue2))
NumericCompare(pFieldType1, pFieldType2) => (ValueFromFieldType(pFieldType1, &fieldValue1), ValueFromFieldType(pFieldType2, &fieldValue2), fieldValue1 - fieldValue2)
NumericCompareKey(key, pFieldType1, pFieldType2) => (ValueFromFieldType(pFieldType1, &fieldValue1), ValueFromFieldType(pFieldType2, &fieldValue2), fieldValue1.%key% - fieldValue2.%key%)
StringCompare(pFieldType1, pFieldType2, casesense := False) => (ValueFromFieldType(pFieldType1, &fieldValue1), ValueFromFieldType(pFieldType2, &fieldValue2), StrCompare(fieldValue1 "", fieldValue2 "", casesense))
StringCompareKey(key, pFieldType1, pFieldType2, casesense := False) => (ValueFromFieldType(pFieldType1, &fieldValue1), ValueFromFieldType(pFieldType2, &fieldValue2), StrCompare(fieldValue1.%key% "", fieldValue2.%key% "", casesense))
RandomCompare(pFieldType1, pFieldType2) => (Random(0, 1) ? 1 : -1)
ValueFromFieldType(pFieldType, &fieldValue?) {
static SYM_STRING := 0, PURE_INTEGER := 1, PURE_FLOAT := 2, SYM_MISSING := 3, SYM_OBJECT := 5
switch SymbolType := NumGet(pFieldType + 8, "Int") {
case PURE_INTEGER: fieldValue := NumGet(pFieldType, "Int64")
case PURE_FLOAT: fieldValue := NumGet(pFieldType, "Double")
case SYM_STRING: fieldValue := StrGet(NumGet(pFieldType, "Ptr")+2*A_PtrSize)
case SYM_OBJECT: fieldValue := ObjFromPtrAddRef(NumGet(pFieldType, "Ptr"))
case SYM_MISSING: return
}
}
}
static ReverseArray(arr) {
local len := arr.Length + 1, max := (len // 2), i := 0
while ++i <= max
temp := arr[len - i], arr[len - i] := arr[i], arr[i] := temp
return arr
}
static UniqueArray(arr) {
local unique := Map()
for v in arr
unique[v] := 1
return [unique*]
}
static FlattenArray(arr) {
local r := []
for v in arr {
if v is Array
r.Push(this.FlattenArray(v)*)
else
r.Push(v)
}
return r
}
static TransformSoftwareBitmap(SoftwareBitmap, &sbW, &sbH, scale:=1, rotate:=0, flip:=0, X?, Y?, W?, H?) {
InMemoryRandomAccessStream := this.SoftwareBitmapToRandomAccessStream(SoftwareBitmap)
ComCall(this.Vtbl_GetDecoder.png, this.BitmapDecoderStatics, "ptr", DecoderGUID:=Buffer(16))
ComCall(15, this.BitmapDecoderStatics, "ptr", DecoderGUID, "ptr", InMemoryRandomAccessStream, "ptr*", BitmapDecoder:=ComValue(13,0))
this.WaitForAsync(&BitmapDecoder)
BitmapFrameWithSoftwareBitmap := ComObjQuery(BitmapDecoder, IBitmapFrameWithSoftwareBitmap := "{FE287C9A-420C-4963-87AD-691436E08383}")
BitmapFrame := ComObjQuery(BitmapDecoder, IBitmapFrame := "{72A49A1C-8081-438D-91BC-94ECFC8185C6}")
BitmapTransform := this.CreateClass("Windows.Graphics.Imaging.BitmapTransform")
local sW := Floor(sbW*scale), sH := Floor(sbH*scale), intermediate
if scale != 1 {
ComCall(7, BitmapTransform, "uint", sW)
ComCall(9, BitmapTransform, "uint", sH)
}
if rotate {
ComCall(15, BitmapTransform, "uint", rotate//90)
if rotate = 90 || rotate = 270
intermediate := sW, sW := sH, sH := intermediate
}
if flip
ComCall(13, BitmapTransform, "uint", flip)
if IsSet(X) {
bounds := Buffer(16,0), NumPut("int", Floor(X*scale), "int", Floor(Y*scale), "int", Floor(Min(sbW-X, W)*scale), "int", Floor(Min(sbH-Y, H)*scale), bounds)
ComCall(17, BitmapTransform, "ptr", bounds)
}
ComCall(8, BitmapFrame, "uint*", &BitmapPixelFormat:=0)
ComCall(9, BitmapFrame, "uint*", &BitmapAlphaMode:=0)
ComCall(8, BitmapFrameWithSoftwareBitmap, "uint", BitmapPixelFormat, "uint", BitmapAlphaMode, "ptr", BitmapTransform, "uint", IgnoreExifOrientation := 0, "uint", DoNotColorManage := 0, "ptr*", SoftwareBitmap:=ComValue(13,0))
this.WaitForAsync(&SoftwareBitmap)
this.CloseIClosable(InMemoryRandomAccessStream)
sbW := sW, sbH := sH
return SoftwareBitmap
}
static CreateDIBSection(w, h, hdc?, bpp:=32, &ppvBits:=0) {
local hdc2 := IsSet(hdc) ? hdc : DllCall("GetDC", "Ptr", 0, "UPtr")
, bi := Buffer(40, 0), hbm
NumPut("int", 40, "int", w, "int", h, "ushort", 1, "ushort", bpp, "int", 0, bi)
hbm := DllCall("CreateDIBSection", "uint", hdc2, "ptr" , bi, "uint" , 0, "uint*", &ppvBits:=0, "uint" , 0, "uint" , 0)
if !IsSet(hdc)
DllCall("ReleaseDC", "Ptr", 0, "Ptr", hdc2)
return hbm
}
static CreateHBitmap(X, Y, W, H, hWnd:=0, scale:=1) {
local sW := Ceil(W*scale), sH := Ceil(H*scale), onlyClientArea := 0, mode := 2, HDC, obm, hbm, pdc, hbm2
if hWnd {
if IsObject(hWnd)
onlyClientArea := hWnd.HasOwnProp("onlyClientArea") ? hWnd.onlyClientArea : onlyClientArea, mode := hWnd.HasOwnProp("mode") ? hWnd.mode : mode, hWnd := hWnd.hWnd
HDC := DllCall("GetDCEx", "Ptr", hWnd, "Ptr", 0, "Int", 2|!onlyClientArea, "Ptr")
if mode > 0 {
PDC := DllCall("CreateCompatibleDC", "Ptr", 0, "Ptr")
HBM := DllCall("CreateCompatibleBitmap", "Ptr", HDC, "Int", Max(40,X+W), "Int", Max(40,Y+H), "Ptr")
, OBM := DllCall("SelectObject", "Ptr", PDC, "Ptr", HBM, "Ptr")
, DllCall("PrintWindow", "Ptr", hWnd, "Ptr", PDC, "UInt", (mode=2?2:0)|!!onlyClientArea)
if scale != 1 || X != 0 || Y != 0 {
PDC2 := DllCall("CreateCompatibleDC", "Ptr", PDC, "Ptr")
, HBM2 := DllCall("CreateCompatibleBitmap", "Ptr", PDC, "Int", Max(40,sW), "Int", Max(40,sH), "Ptr")
, OBM2 := DllCall("SelectObject", "Ptr", PDC2, "Ptr", HBM2, "Ptr")
, PrevStretchBltMode := DllCall("SetStretchBltMode", "Ptr", PDC, "Int", 3, "Int")
, DllCall("StretchBlt", "Ptr", PDC2, "Int", 0, "Int", 0, "Int", sW, "Int", sH, "Ptr", PDC, "Int", X, "Int", Y, "Int", W, "Int", H, "UInt", 0x00CC0020 | this.CAPTUREBLT)
, DllCall("SetStretchBltMode", "Ptr", PDC, "Int", PrevStretchBltMode)
, DllCall("SelectObject", "Ptr", PDC2, "Ptr", obm2)
, DllCall("DeleteDC", "Ptr", PDC)
, DllCall("DeleteObject", "UPtr", HBM)
, hbm := hbm2, pdc := pdc2
}
DllCall("SelectObject", "Ptr", PDC, "Ptr", OBM)
, DllCall("DeleteDC", "Ptr", HDC)
, oHBM := this.IBase(HBM), oHBM.DC := PDC
return oHBM.DefineProp("__Delete", {call:(this, *)=>(DllCall("DeleteObject", "Ptr", this), DllCall("DeleteDC", "Ptr", this.DC))})
}
} else {
HDC := DllCall("GetDC", "Ptr", 0, "Ptr")
}
PDC := DllCall("CreateCompatibleDC", "Ptr", HDC, "Ptr")
, HBM := DllCall("CreateCompatibleBitmap", "Ptr", HDC, "Int", Max(40,sW), "Int", Max(40,sH), "Ptr")
, OBM := DllCall("SelectObject", "Ptr", PDC, "Ptr", HBM, "Ptr")
if sW < 40 || sH < 40
DllCall("StretchBlt", "Ptr", PDC, "Int", 0, "Int", 0, "Int", Max(40,sW), "Int", Max(40,sH), "Ptr", HDC, "Int", X, "Int", Y, "Int", 1, "Int", 1, "UInt", 0x00CC0020 | this.CAPTUREBLT)
PrevStretchBltMode := DllCall("SetStretchBltMode", "Ptr", PDC, "Int", 3, "Int")
, DllCall("StretchBlt", "Ptr", PDC, "Int", 0, "Int", 0, "Int", sW, "Int", sH, "Ptr", HDC, "Int", X, "Int", Y, "Int", W, "Int", H, "UInt", 0x00CC0020 | this.CAPTUREBLT)
, DllCall("SetStretchBltMode", "Ptr", PDC, "Int", PrevStretchBltMode)
, DllCall("SelectObject", "Ptr", PDC, "Ptr", OBM)
, DllCall("DeleteDC", "Ptr", HDC)
, oHBM := this.IBase(HBM), oHBM.DC := PDC
return oHBM.DefineProp("__Delete", {call:(this, *)=>(DllCall("DeleteObject", "Ptr", this), DllCall("ReleaseDC", "Ptr", 0, "Ptr", this.DC))})
}
static CreateDirect3DSoftwareBitmapFromWindow(hWnd) {
static init := 0, DXGIDevice, Direct3DDevice, Direct3D11CaptureFramePoolStatics, GraphicsCaptureItemInterop, GraphicsCaptureItemGUID, D3D_Device, D3D_Context
local x, y, w, h, rect
if !init {
DllCall("LoadLibrary","str","DXGI")
DllCall("LoadLibrary","str","D3D11")
DllCall("LoadLibrary","str","Dwmapi")
DllCall("D3D11\D3D11CreateDevice", "ptr", 0, "int", D3D_DRIVER_TYPE_HARDWARE := 1, "ptr", 0, "uint", D3D11_CREATE_DEVICE_BGRA_SUPPORT := 0x20, "ptr", 0, "uint", 0, "uint", D3D11_SDK_VERSION := 7, "ptr*", D3D_Device:=ComValue(13, 0), "ptr*", 0, "ptr*", D3D_Context:=ComValue(13, 0))
DXGIDevice := ComObjQuery(D3D_Device, IID_IDXGIDevice := "{54ec77fa-1377-44e6-8c32-88fd5f44c84c}")
DllCall("D3D11\CreateDirect3D11DeviceFromDXGIDevice", "ptr", DXGIDevice, "ptr*", GraphicsDevice:=ComValue(13, 0))
Direct3DDevice := ComObjQuery(GraphicsDevice, IDirect3DDevice := "{A37624AB-8D5F-4650-9D3E-9EAE3D9BC670}")
Direct3D11CaptureFramePoolStatics := this.CreateClass("Windows.Graphics.Capture.Direct3D11CaptureFramePool", IDirect3D11CaptureFramePoolStatics := "{7784056a-67aa-4d53-ae54-1088d5a8ca21}")
GraphicsCaptureItemStatics := this.CreateClass("Windows.Graphics.Capture.GraphicsCaptureItem", IGraphicsCaptureItemStatics := "{A87EBEA5-457C-5788-AB47-0CF1D3637E74}")
GraphicsCaptureItemInterop := ComObjQuery(GraphicsCaptureItemStatics, IGraphicsCaptureItemInterop := "{3628E81B-3CAC-4C60-B7F4-23CE0E0C3356}")
GraphicsCaptureItemGUID := Buffer(16,0)
DllCall("ole32\CLSIDFromString", "wstr", IGraphicsCaptureItem := "{79c3f95b-31f7-4ec2-a464-632ef5d30760}", "ptr", GraphicsCaptureItemGUID)
init := 1
}
DllCall("Dwmapi.dll\DwmGetWindowAttribute", "ptr", hWnd, "uint", DWMWA_EXTENDED_FRAME_BOUNDS := 9, "ptr", rect := Buffer(16,0), "uint", 16)
x := NumGet(rect, 0, "int"), y := NumGet(rect, 4, "int"), w := NumGet(rect, 8, "int") - x, h := NumGet(rect, 12, "int") - y
ComCall(6, Direct3D11CaptureFramePoolStatics, "ptr", Direct3DDevice, "int", B8G8R8A8UIntNormalized := 87, "int", numberOfBuffers := 2, "int64", (h << 32) | w, "ptr*", Direct3D11CaptureFramePool:=ComValue(13, 0))
if ComCall(3, GraphicsCaptureItemInterop, "ptr", hWnd, "ptr", GraphicsCaptureItemGUID, "ptr*", GraphicsCaptureItem:=ComValue(13, 0), "uint") {
this.CloseIClosable(Direct3D11CaptureFramePool)
throw Error("Failed to capture GraphicsItem of window",, -1)
}
ComCall(10, Direct3D11CaptureFramePool, "ptr", GraphicsCaptureItem, "ptr*", GraphicsCaptureSession:=ComValue(13, 0))
GraphicsCaptureSession2 := ComObjQuery(GraphicsCaptureSession, IGraphicsCaptureSession2 := "{2c39ae40-7d2e-5044-804e-8b6799d4cf9e}")
ComCall(7, GraphicsCaptureSession2, "int", 0)
if (Integer(StrSplit(A_OSVersion, ".")[3]) >= 20348) {
GraphicsCaptureSession3 := ComObjQuery(GraphicsCaptureSession, IGraphicsCaptureSession3 := "{f2cdd966-22ae-5ea1-9596-3a289344c3be}")
ComCall(7, GraphicsCaptureSession3, "int", 0)
}
ComCall(6, GraphicsCaptureSession)
Loop {
ComCall(7, Direct3D11CaptureFramePool, "ptr*", Direct3D11CaptureFrame:=ComValue(13, 0))
if (Direct3D11CaptureFrame.ptr != 0)
break
}
ComCall(6, Direct3D11CaptureFrame, "ptr*", Direct3DSurface:=ComValue(13, 0))
ComCall(11, this.SoftwareBitmapStatics, "ptr", Direct3DSurface, "ptr*", SoftwareBitmap:=ComValue(13, 0))
OCR.WaitForAsync(&SoftwareBitmap)
this.CloseIClosable(Direct3D11CaptureFramePool)
this.CloseIClosable(GraphicsCaptureSession)
if GraphicsCaptureSession2 {
this.CloseIClosable(GraphicsCaptureSession2)
}
if IsSet(GraphicsCaptureSession3) {
this.CloseIClosable(GraphicsCaptureSession3)
}
this.CloseIClosable(Direct3D11CaptureFrame)
this.CloseIClosable(Direct3DSurface)
SoftwareBitmap.x := x, SoftwareBitmap.y := y, SoftwareBitmap.w := w, SoftwareBitmap.h := h
return SoftwareBitmap
}
static HBitmapToRandomAccessStream(hBitmap) {
static PICTYPE_BITMAP := 1
, BSOS_DEFAULT   := 0
, sz := 8 + A_PtrSize*2
local PICTDESC, riid, size, pIRandomAccessStream
DllCall("Ole32\CreateStreamOnHGlobal", "Ptr", 0, "UInt", true, "Ptr*", pIStream:=ComValue(13,0), "UInt")
, PICTDESC := Buffer(sz, 0)
, NumPut("uint", sz, "uint", PICTYPE_BITMAP, "ptr", IsInteger(hBitmap) ? hBitmap : hBitmap.ptr, PICTDESC)
, riid := this.CLSIDFromString(this.IID_IPicture)
, DllCall("OleAut32\OleCreatePictureIndirect", "Ptr", PICTDESC, "Ptr", riid, "UInt", 0, "Ptr*", pIPicture:=ComValue(13,0), "UInt")
, ComCall(15, pIPicture, "Ptr", pIStream, "UInt", true, "uint*", &size:=0, "UInt")
, riid := this.CLSIDFromString(this.IID_IRandomAccessStream)
, DllCall("ShCore\CreateRandomAccessStreamOverStream", "Ptr", pIStream, "UInt", BSOS_DEFAULT, "Ptr", riid, "Ptr*", pIRandomAccessStream:=this.IBase(), "UInt")
Return pIRandomAccessStream
}
static HBitmapToSoftwareBitmap(hBitmap, hDC?, transform?) {
local bi := Buffer(40, 0), W, H, BitmapBuffer, MemoryBuffer, MemoryBufferReference, BufferByteAccess, BufferSize
hDC := (hBitmap is OCR.IBase ? hBitmap.DC : (hDC ?? dhDC := DllCall("GetDC", "Ptr", 0, "UPtr")))
NumPut("uint", 40, bi, 0)
DllCall("GetDIBits", "ptr", hDC, "ptr", hBitmap, "uint", 0, "uint", 0, "ptr", 0, "ptr", bi, "uint", 0)
W := NumGet(bi, 4, "int"), H := NumGet(bi, 8, "int")
ComCall(7, this.SoftwareBitmapFactory, "int", 87, "int", W, "int", H, "int", 0, "ptr*", SoftwareBitmap := ComValue(13,0))
ComCall(15, SoftwareBitmap, "int", 2, "ptr*", BitmapBuffer := ComValue(13,0))
MemoryBuffer := ComObjQuery(BitmapBuffer, "{fbc4dd2a-245b-11e4-af98-689423260cf8}")
ComCall(6, MemoryBuffer, "ptr*", MemoryBufferReference := ComValue(13,0))
BufferByteAccess := ComObjQuery(MemoryBufferReference, "{5b0d3235-4dba-4d44-865e-8f1d0e4fd04d}")
ComCall(3, BufferByteAccess, "ptr*", &SoftwareBitmapByteBuffer:=0, "uint*", &BufferSize:=0)
NumPut("short", 32, "short", 0, bi, 14), NumPut("int", -H, bi, 8)
DllCall("GetDIBits", "ptr", hDC, "ptr", hBitmap, "uint", 0, "uint", H, "ptr", SoftwareBitmapByteBuffer, "ptr", bi, "uint", 0)
if IsSet(transform) {
if (transform.HasProp("grayscale") && transform.grayscale)
DllCall(this.GrayScaleMCode, "ptr", SoftwareBitmapByteBuffer, "uint", w, "uint", h, "uint", (w*4+3) // 4 * 4, "cdecl uint")
if (transform.HasProp("invertcolors") && transform.invertcolors)
DllCall(this.InvertColorsMCode, "ptr", SoftwareBitmapByteBuffer, "uint", w, "uint", h, "uint", (w*4+3) // 4 * 4, "cdecl uint")
}
if IsSet(dhDC)
DllCall("DeleteDC", "ptr", dhDC)
BufferByteAccess := "", MemoryBufferReference := "", MemoryBuffer := "", BitmapBuffer := ""
return SoftwareBitmap
}
static MCode(mcode) {
static e := Map('1', 4, '2', 1), c := (A_PtrSize=8) ? "x64" : "x86"
if (!regexmatch(mcode, "^([0-9]+),(" c ":|.*?," c ":)([^,]+)", &m))
return
if (!DllCall("crypt32\CryptStringToBinary", "str", m.3, "uint", 0, "uint", e[m.1], "ptr", 0, "uint*", &s := 0, "ptr", 0, "ptr", 0))
return
p := DllCall("GlobalAlloc", "uint", 0, "ptr", s, "ptr")
if (c="x64")
DllCall("VirtualProtect", "ptr", p, "ptr", s, "uint", 0x40, "uint*", &op := 0)
if (DllCall("crypt32\CryptStringToBinary", "str", m.3, "uint", 0, "uint", e[m.1], "ptr", p, "uint*", &s, "ptr", 0, "ptr", 0))
return p
DllCall("GlobalFree", "ptr", p)
}
static DisplayHBitmap(hBitmap) {
local gImage := Gui("-DPIScale"), W, H
, hPic := gImage.Add("Text", "0xE w640 h640")
SendMessage(0x172, 0, hBitmap,, hPic.hWnd)
hPic.GetPos(,,&W, &H)
gImage.Show("w" (W+20) " H" (H+20))
WinWaitClose gImage
}
static SoftwareBitmapToRandomAccessStream(SoftwareBitmap) {
InMemoryRandomAccessStream := this.CreateClass("Windows.Storage.Streams.InMemoryRandomAccessStream")
ComCall(8, this.BitmapEncoderStatics, "ptr", encoderId := Buffer(16, 0))
ComCall(13, this.BitmapEncoderStatics, "ptr", encoderId, "ptr", InMemoryRandomAccessStream, "ptr*", BitmapEncoder:=ComValue(13,0))
this.WaitForAsync(&BitmapEncoder)
BitmapEncoderWithSoftwareBitmap := ComObjQuery(BitmapEncoder, "{686cd241-4330-4c77-ace4-0334968b1768}")
ComCall(6, BitmapEncoderWithSoftwareBitmap, "ptr", SoftwareBitmap)
ComCall(19, BitmapEncoder, "ptr*", asyncAction:=ComValue(13,0))
this.WaitForAsync(&asyncAction)
ComCall(11, InMemoryRandomAccessStream, "int64", 0)
return InMemoryRandomAccessStream
}
static CreateClass(str, interface?) {
local hString := this.CreateHString(str), result
if !IsSet(interface) {
result := DllCall("Combase.dll\RoActivateInstance", "ptr", hString, "ptr*", cls:=this.IBase(), "uint")
} else {
GUID := this.CLSIDFromString(interface)
result := DllCall("Combase.dll\RoGetActivationFactory", "ptr", hString, "ptr", GUID, "ptr*", cls:=this.IBase(), "uint")
}
if (result != 0) {
if (result = 0x80004002)
throw Error("No such interface supported", -1, interface)
else if (result = 0x80040154)
throw Error("Class not registered", -1)
else
throw Error(result)
}
this.DeleteHString(hString)
return cls
}
static CreateHString(str) => (DllCall("Combase.dll\WindowsCreateString", "wstr", str, "uint", StrLen(str), "ptr*", &hString:=0), hString)
static DeleteHString(hString) => DllCall("Combase.dll\WindowsDeleteString", "ptr", hString)
static WaitForAsync(&obj) {
local AsyncInfo := ComObjQuery(obj, this.IID_IAsyncInfo), status, ErrorCode
Loop {
ComCall(7, AsyncInfo, "uint*", &status:=0)
if (status != 0) {
if (status != 1) {
ComCall(8, ASyncInfo, "uint*", &ErrorCode:=0)
throw Error("AsyncInfo failed with status error " ErrorCode, -1)
}
break
}
Sleep this.PerformanceMode ? -1 : 1
}
ComCall(8, obj, "ptr*", ObjectResult:=this.IBase())
obj := ObjectResult
}
static CloseIClosable(pClosable) {
static IClosable := "{30D5A829-7FA4-4026-83BB-D75BAE4EA99E}"
local Close := ComObjQuery(pClosable, IClosable)
ComCall(6, Close)
}
static CLSIDFromString(IID) {
local CLSID := Buffer(16), res
if res := DllCall("ole32\CLSIDFromString", "WStr", IID, "Ptr", CLSID, "UInt")
throw Error("CLSIDFromString failed. Error: " . Format("{:#x}", res))
Return CLSID
}
static NormalizeCoordinates(result, scale) {
local word
if scale != 1 {
for word in result.Words
word.x := Integer(word.x / scale), word.y := Integer(word.y / scale), word.w := Integer(word.w / scale), word.h := Integer(word.h / scale), word.BoundingRect := {X:word.x, Y:word.y, W:word.w, H:word.h}
}
return result
}
static __ExtractNamedParameters(obj, params*) {
local i := 0
if !IsObject(obj) || Type(obj) != "Object"
return 0
Loop params.Length // 2 {
name := params[++i], value := params[++i]
if obj.HasProp(name)
%value% := obj.%name%
}
return 1
}
static __ExtractTransformParameters(obj, &transform) {
local scale := 1, grayscale := 0, invertcolors := 0, rotate := 0, flip := 0
if IsObject(obj)
this.__ExtractNamedParameters(obj, "scale", &scale, "grayscale", &grayscale, "invertcolors", &invertcolors, "rotate", &rotate, "flip", &flip, "transform", &transform)
if IsObject(transform) {
for prop in ["scale", "grayscale", "invertcolors", "rotate", "flip"]
if !transform.HasProp(prop)
transform.%prop% := %prop%
} else
transform := {scale:scale, grayscale:grayscale, invertcolors:invertcolors, rotate:rotate, flip:flip}
transform.flip := transform.flip = "y" ? 1 : transform.flip = "x" ? 2 : transform.flip
}
OffsetCoordinates(offsetX?, offsetY?) {
if !IsSet(offsetX) || !IsSet(offsetY) {
if this.HasOwnProp("Relative") {
if this.Relative.HasOwnProp("Client")
offsetX := this.Relative.Client.x, offsetY := this.Relative.Client.x
else if this.Relative.HasOwnProp("Window")
offsetX := this.Relative.Window.x, offsetY := this.Relative.Window.y
else
throw Error("No appropriate Relative property found",, -1)
} else
throw Error("No Relative property found",, -1)
}
if offsetX = 0 && offsetY = 0
return this
local word
for word in this.Words
word.x += offsetX, word.y += offsetY, word.BoundingRect := {X:word.x, Y:word.y, W:word.w, H:word.h}
return this
}
static ConvertWinPos(X, Y, &outX, &outY, relativeFrom:="", relativeTo:="screen", winTitle?, winText?, excludeTitle?, excludeText?) {
relativeFrom := relativeFrom || A_CoordModeMouse
if relativeFrom = relativeTo {
outX := X, outY := Y
return
}
local hWnd := WinExist(winTitle?, winText?, excludeTitle?, excludeText?)
switch relativeFrom, 0 {
case "screen", "s":
if relativeTo = "window" || relativeTo = "w" {
DllCall("user32\GetWindowRect", "Int", hWnd, "Ptr", RECT := Buffer(16))
outX := X-NumGet(RECT, 0, "Int"), outY := Y-NumGet(RECT, 4, "Int")
} else {
pt := Buffer(8), NumPut("int",X,pt), NumPut("int",Y,pt,4)
DllCall("ScreenToClient", "Int", hWnd, "Ptr", pt)
outX := NumGet(pt,0,"int"), outY := NumGet(pt,4,"int")
}
case "window", "w":
WinGetPos(&outX, &outY,,,hWnd)
outX += X, outY += Y
if relativeTo = "client" || relativeTo = "c" {
pt := Buffer(8), NumPut("int",outX,pt), NumPut("int",outY,pt,4)
DllCall("ScreenToClient", "Int", hWnd, "Ptr", pt)
outX := NumGet(pt,0,"int"), outY := NumGet(pt,4,"int")
}
case "client", "c":
pt := Buffer(8), NumPut("int",X,pt), NumPut("int",Y,pt,4)
DllCall("ClientToScreen", "Int", hWnd, "Ptr", pt)
outX := NumGet(pt,0,"int"), outY := NumGet(pt,4,"int")
if relativeTo = "window" || relativeTo = "w" {
DllCall("user32\GetWindowRect", "Int", hWnd, "Ptr", RECT := Buffer(16))
outX -= NumGet(RECT, 0, "Int"), outY -= NumGet(RECT, 4, "Int")
}
}
}
}
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
DllCall("SetThreadDpiAwarenessContext", "ptr", -3)
global size := 50, minsize := 5, step := 3
global isTracking := true
global searchWords := [
"sparkling", "shiny", "giant", "big", "mythical", "hexed", "abyssal", "electric",
"fossilized", "darkened", "translucent", "lunar", "solarblaze", "frozen", "midas",
"negative", "glossy", "scorched", "silver", "albino", "mosaic", "amber"
]
counter := 0
SetTimer(TrackMouse,10)
TrackMouse()
{
global
counter++
if (isTracking) {
MouseGetPos(&x, &y)
Highlight(x - size // 2, y + 10, size, size)
text := OCR.FromRect(x - size // 2, y + 10, size, size, "en-us").Text
text2 := text
foundWords := GetFoundWords(text)
ToolTip("Made by AsphaltCake`nGUI by texture`n`nP: start`nM: exit`nZ: shrink`nX: Expand`nC: lock`n`n" counter "`nRaw Text: " text2 "`nFound Words: " . StrJoin(foundWords, ", "), 50, HalfY - 300)
}
else {
Highlight(x - size // 2, y + 10, size, size)
text := OCR.FromRect(x - size // 2, y + 10, size, size, "en-us").Text
text2 := text
foundWords := GetFoundWords(text)
ToolTip("Made by AsphaltCake`nGUI by texture`n`nP: start`nM: exit`nZ: shrink`nX: Expand`nC: lock`n`n" counter "`nRaw Text: " text2 "`nFound Words: " . StrJoin(foundWords, ", "), 50, HalfY - 300)
}
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
ToolTip(stateTooltip, 50, HalfY, 2)
return
}
m::exitapp
z::global size-=(size > minsize ? step : 0)
x::global size+=step
o::reload
p::
{
global
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
}
c:: {
global isTracking, sparkling, shiny, giant, big, mythical, hexed, abyssal, electric
global fossilized, darkened, translucent, lunar, solarblaze, frozen, midas, negative
global glossy, scorched, silver, albino, mosaic, amber
isTracking := !isTracking
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
ToolTip(stateTooltip, 50, HalfY, 2)
}
GetFoundWords(text) {
global searchWords, sparkling, shiny, giant, big, mythical, hexed, abyssal, electric
global fossilized, darkened, translucent, lunar, solarblaze, frozen, midas, negative
global glossy, scorched, silver, albino, mosaic, amber
text := StrLower(StrReplace(text, " ", ""))
foundWords := []
for word in searchWords {
if (InStr(text, word)) {
foundWords.Push(word)
%word% := 1
}
}
return foundWords
}
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
{
global
ChkSparkling := ogcCheckBoxChkSparkling.Value
sparkling := (ChkSparkling = 0 ? 1 : 0)
Return
}
GShiny(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkShiny2 := ogcCheckBoxChkShiny2.Value
shiny := (ChkShiny2 = 0 ? 1 : 0)
Return
}
GGiant(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkGiant3 := ogcCheckBoxChkGiant3.Value
giant := (ChkGiant3 = 0 ? 1 : 0)
Return
}
GBig(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkBig4 := ogcCheckBoxChkBig4.Value
big := (ChkBig4 = 0 ? 1 : 0)
Return
}
GMythical(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkMythical5 := ogcCheckBoxChkMythical5.Value
mythical := (ChkMythical5 = 0 ? 1 : 0)
Return
}
GAbyssal(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkAbyssal6 := ogcCheckBoxChkAbyssal6.Value
abyssal := (ChkAbyssal6 = 0 ? 1 : 0)
Return
}
GFossilized(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkFossilized7 := ogcCheckBoxChkFossilized7.Value
fossilized := (ChkFossilized7 = 0 ? 1 : 0)
Return
}
GLunar(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkLunar8 := ogcCheckBoxChkLunar8.Value
lunar := (ChkLunar8 = 0 ? 1 : 0)
Return
}
GSolarBlaze(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkSolarblaze9 := ogcCheckBoxChkSolarblaze9.Value
solarblaze := (ChkSolarblaze9 = 0 ? 1 : 0)
Return
}
GMidas(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkMidas10 := ogcCheckBoxChkMidas10.Value
midas := (ChkMidas10 = 0 ? 1 : 0)
Return
}
GGlossy(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkGlossy11 := ogcCheckBoxChkGlossy11.Value
glossy := (ChkGlossy11 = 0 ? 1 : 0)
Return
}
GSilver(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkSilver12 := ogcCheckBoxChkSilver12.Value
silver := (ChkSilver12 = 0 ? 1 : 0)
Return
}
GMosaic(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkMosaic13 := ogcCheckBoxChkMosaic13.Value
mosaic := (ChkMosaic13 = 0 ? 1 : 0)
Return
}
GHexed(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkHexed14 := ogcCheckBoxChkHexed14.Value
hexed := (ChkHexed14 = 0 ? 1 : 0)
Return
}
GElectric(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkElectric15 := ogcCheckBoxChkElectric15.Value
electric := (ChkElectric15 = 0 ? 1 : 0)
Return
}
GDarkened(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkDarkened16 := ogcCheckBoxChkDarkened16.Value
darkened := (ChkDarkened16 = 0 ? 1 : 0)
Return
}
GTranslucent(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkTranslucent17 := ogcCheckBoxChkTranslucent17.Value
translucent := (ChkTranslucent17 = 0 ? 1 : 0)
Return
}
GFrozen(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkFrozen18 := ogcCheckBoxChkFrozen18.Value
frozen := (ChkFrozen18 = 0 ? 1 : 0)
Return
}
GNegative(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkNegative19 := ogcCheckBoxChkNegative19.Value
negative := (ChkNegative19 = 0 ? 1 : 0)
Return
}
GScorched(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkScorched20 := ogcCheckBoxChkScorched20.Value
scorched := (ChkScorched20 = 0 ? 1 : 0)
Return
}
GAlbino(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkAlbino21 := ogcCheckBoxChkAlbino21.Value
albino := (ChkAlbino21 = 0 ? 1 : 0)
Return
}
GAmber(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkAmber22 := ogcCheckBoxChkAmber22.Value
amber := (ChkAmber22 = 0 ? 1 : 0)
Return
}
GMultipleMode(A_GuiEvent := "", GuiCtrlObj := "", Info := "", *)
{
global
ChkMultipleMode23 := ogcCheckBoxChkMultipleMode23.Value
multiple := (ChkMultipleMode23 = 0 ? 1 : 0)
Return
}
MainWindowLEscape:
MainWindowLClose:
ExitApp()