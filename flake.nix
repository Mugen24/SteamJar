{
    inputs = {
        nixpkgs = "github:NixOS/nixpkgs/nixos-24.11";
    };
    outputs = 
    {self, nixpkgs, ...}:
    let 
        pkgs = nixpkgs;
        system = "whatever";
    in
    {
        inherit pkgs;
        devShells.${system}.default = pkgs.mkShell {
            packages = with pkgs; [
                python312Packages.pycairo
                python312Packages.pygobject3
                python312Full
            ];
        };
    };
}
