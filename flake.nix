{
    inputs = {
        nixpkgs = {
            url = "github:NixOS/nixpkgs/nixos-24.11";
        };
    };
    outputs = 
    {self, nixpkgs, ...}:
    let 
        system = "x86_64-linux";
        pkgs = import nixpkgs {
            inherit system;
        };
    in
    {
        inherit pkgs;
        devShells.${system}.default = pkgs.mkShell {
            packages = with pkgs; [
                python312Packages.pycairo
                python312Packages.pygobject3
                python312Packages.python-dotenv
                python312Packages.pyaml
                python312Full
                gtk3-x11
            ];
        };
    };
}
