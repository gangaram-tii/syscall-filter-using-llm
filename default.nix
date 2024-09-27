{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python311Full
    pkgs.python311Packages.virtualenv
    pkgs.python311Packages.numpy
    pkgs.python311Packages.pandas
    pkgs.python311Packages.matplotlib
    pkgs.python311Packages.pytorch
    pkgs.python311Packages.pandas
    pkgs.python311Packages.scikit-learn
    pkgs.python311Packages.pip
  ];

  shellHook = ''
    if [ ! -d .venv ]; then
      virtualenv .venv
      source .venv/bin/activate
      pip install textblob llm-index chromadb sentence_transformers langchain elftools 
    else
      source .venv/bin/activate
    fi
    echo "Welcome to your Python development environment."
  '';
}

