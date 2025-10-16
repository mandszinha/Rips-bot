{ pkgs }:
{
  deps = [
    pkgs.python311Full    # Python 3.11
    pkgs.nodejs           # Node.js necessário para Playwright
    pkgs.curl
    pkgs.gcc
    pkgs.glib
    pkgs.glibc
    pkgs.libX11
    pkgs.libXcomposite
    pkgs.libXdamage
    pkgs.libXfixes
    pkgs.libgbm
    pkgs.libxkbcommon
    pkgs.alsaLib
    pkgs.nss
    pkgs.nspr
    pkgs.dbus
    pkgs.atk
    pkgs.atspi2
    pkgs.cairo
    pkgs.pango
  ];
}

