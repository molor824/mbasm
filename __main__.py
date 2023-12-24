import sys
from lexer import Lexer
from astparser import Parser

HELP_DESC = (
"""
Usage: mbasm [files] [options]
Options:
  -h, --help          Show this message and exit
  -d, --objdump       Prints the compiled assembly code
  -o, --output [path] Path to the output file (default is 'a.bin')
  --debug             Shows debug messages
"""
)

def print_error(msg: str):
    print(f"Error: {msg}")
    sys.exit(-1)

def main():
    args = sys.argv[1:]
    input_paths = []
    out_path = 'a.bin'
    obj_dump = False
    debug_mode = False

    args_iter = iter(args)

    for arg in args_iter:
        match arg:
            case '-h' | '--help':
                print(HELP_DESC)
                return
            case '-d' | '--objdump':
                obj_dump = True
            case '-o' | '--output':
                try:
                    out_path = next(args_iter)
                except StopIteration:
                    print_error("No output path specified")
            case '--debug':
                debug_mode = True
            case _:
                input_paths.append(arg)
    
    try:
        input_files = [open(path, 'r') for path in input_paths]
    except OSError:
        print_error(f"Error: Failed to open input files: {', '.join(f"'{path}'" for path in input_paths)}")

    source = '\n'.join([file.read() for file in input_files])

    for file in input_files:
        file.close()
    
    try:
        lexer = Lexer(source)
        parser = Parser(lexer)

        nodes = parser.parse()

        for node in nodes:
            print(node)
    except SyntaxError as err:
        print_error(err.msg)

if __name__ == '__main__':
    main()