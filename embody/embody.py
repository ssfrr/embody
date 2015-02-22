from jinja2 import Environment, PackageLoader
from pycparser import parse_file, c_ast
from pycparser.c_generator import CGenerator
import os
from os import path
import yaml


def make_output_name(in_name, out_name,
                     out_dir=None, prefix=None, extension=None):
    '''Generates a full output filename given the input filename, a target
    output filename, a target directory, a prefix, and an extension. If the
    output name is given it is used unchanged. If a directory is given, the
    output is in that directory with a filename based on the input filename,
    using the given prefix and extension. If no output directory is given, the
    same directory as the given file is used.'''

    if out_name is not None:
        return out_name

    pathname, basename = path.split(in_name)
    # if an output directory is given, use it. Otherwise use the same directory
    # as the input
    if out_dir is not None:
        pathname = out_dir
    # remove the final extension
    basename = '.'.join(basename.split('.')[:-1])
    return path.join(pathname, prefix + basename + extension)


class FuncDeclVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.stubs = []

    def visit_FuncDecl(self, node):
        gen = CGenerator()
        self.stubs.append(gen.visit(node))


def generate_fake(in_filename, fake_src_filename,
                  fake_header_filename, cpp_args=[]):
    cfg = _get_config()
    ast = parse_file(in_filename, use_cpp=True, cpp_args=cpp_args)
    v = FuncDeclVisitor()
    v.visit(ast)

    env = Environment(loader=PackageLoader('embody', 'templates'))
    with open(fake_header_filename, 'w') as fake_header:
        fake_header_template = env.get_template('fake.h')
        ctx = {
            'include_guard':
                path.basename(fake_header_filename).upper().replace('.', '_'),
            'header': path.basename(in_filename),
        }
        fake_header.write(fake_header_template.render(**ctx))

    with open(fake_src_filename, 'w') as fake_src:
        fake_src_template = env.get_template('fake.c')
        ctx = {
            'fake_include': path.basename(fake_header_filename),
            'funcs': v.stubs
        }
        fake_src.write(fake_src_template.render(**ctx))


def _get_config():
    '''Searches for embody config files and returns a dictionary of options. A
    config file is called either .embodyrc.yaml or .embody/config.yaml. We
    first search in $HOME, then the project root, then any directories in the
    path between the project root and the current directory. The project root
    is assumed to be the first parent directory where we find a .git or .hg
    directory.

    All config files found are combined, with later files overriding earlier.
    This means that you can have settings in $HOME/.embodyrc.yaml that are
    generally useful, and then override them on a project-by-project basis'''

    config = _get_dir_config(os.getenv('HOME'))
    config.update(_get_project_config(os.getcwdu()))
    return config


def _get_project_config(path):
    '''Looks for a config file in the current directory, and all parent
    directories until it finds a .git or .hg file'''


    config = {}
    root_files = {'.git', '.hg'}
    dirfiles = set(os.listdir(path))
    # start by recursively getting the parent config if we're not at the
    # project root
    if not dirfiles.intersection(root_files):
        parentdir = os.path.split(path)[0]
        if parentdir != path:
            config.update(_get_project_config(parentdir))

    # now override the parent's config with any data from the current directory
    config.update(_get_dir_config(path))
    return config


def _get_dir_config(path):
    '''Looks for a config file in the current directory'''
    config = {}
    cfgfilename = '.embodyrc.yaml'
    cfgdirname = '.embody'
    cfgdirfilename = 'config.yaml'

    dirfiles = os.listdir(path)

    if cfgfilename in dirfiles:
        with open(os.path.join(path, cfgfilename)) as cfgfile:
            config.update(yaml.load(cfgfile))

    if cfgdirname in dirfiles and \
            cfgdirfilename in os.listdir(
                os.path.join(path, cfgdirname)):
        with open(os.path.join(path, cfgdirname, cfgdirfilename)) as cfgfile:
            config.update(yaml.load(cfgfile))

    return config
