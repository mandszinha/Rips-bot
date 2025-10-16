{ pkgs }: 
{
  deps = [
    pkgs.python311Full
    pkgs.nodejs
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
    pkgs.atkmm
    pkgs.atspi2
  ];
}

