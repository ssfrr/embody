embody
======

```
Usage:
 embody project [options] <name>
 embody module [options] <name>
 embody fake [options] <infile> [-- <cppargs>...]
 embody dumpconfig [options] [outfile]

embody is a set of tools for embedded C development. Configuration can be given
as command line options or in a .embodyrc.yaml file, or in .embody/config.yaml.
These config files can be placed in $HOME, or in the project directory. More
specific config files (e.g.  per project) override more general ones (e.g. in
$HOME). Command line arguments take precedence.

Valid configuration keys are:

    cpp_args
    project_root
    src_dir
    test_dir
    fake_dir
    project_name
    copyright_holder
    author
    fake_prefix

For example, to set the prefix for fake files, use `fakeprefix: "myprefix"`.
Pro Tip: use the `-v` option to see where embody has loaded the configuration.

Subcommands:
    project
        Generate an initial skeleton project

    module
        Generate a fake module within the current project

    fake
        Generate a fake header/implementation pair that implements the given
        header file. You can supply arguments to the C Preprocessor that will
        be used during parsing.

    dumpconfig
        Dump the loaded configuration to a file. (use the -v flag to see where
        it's being loaded from). If no output file is given it will be dumped
        to stdout.

Options:
 -p <name> --project=<name>       Project name used when generating modules
                                  and fakes
 -a <name> --author=<name>        the author of the code.
 -c <name> --copyright=<name>     The copyright holder. If not given then the
                                  author is used.
 -d <dir>, --srcdir=<dir>         Directory for generated header and source
 -t <dir>, --testdir=<dir>        Directory for generated test files
 -k <dir>, --fakedir=<dir>        Directory for generated fakes
 -o <file>, --outfile=<file>      Filename base for generated files. `.c` and
                                  `.h` will be appended as necessary
 -f <str>, --fakeprefix=<str>     Filename prefix for generated files
                                  (default: Fake)
 -v, --verbose                    Print extra info
 --help                           Print this helpful message
```
