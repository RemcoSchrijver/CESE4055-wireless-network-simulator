{ pkgs ? import <nixpkgs> {
    config.allowUnfree = true;
    config.cudaSupport = true;
                          }}:

pkgs.mkShell {
    packages = [
        pkgs.python311
        pkgs.python311Packages.pip
        pkgs.python311Packages.tkinter
    ];
    LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib:/run/opengl-driver/lib:$LD_LIBRARY_PATH";
}
