from jinja2 import Environment, PackageLoader
from pycparser import parse_file, c_ast
from pycparser.c_generator import CGenerator
import os
from os import path


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
