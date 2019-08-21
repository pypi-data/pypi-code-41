#!/usr/bin/python3

if __name__ == "__main__":
    
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--config", default="cmaker.config")
    args = parser.parse_args()
    
    from cmaker.maker import Maker
    from cmaker.compiler import Compiler
    
    maker = Maker(args.config)
    
    try:
        maker.make(args.input, args.output)
    except Compiler.Error:
        raise SystemExit("ERROR: Early termination.")
