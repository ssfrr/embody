from jinja2 import Environment, PackageLoader
from pycparser import parse_file, c_ast
from pycparser.c_generator import CGenerator


class FuncDeclVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.stubs = []

    def visit_FuncDecl(self, node):
        gen = CGenerator()
        self.stubs.append(gen.visit(node))


def generate_fake(in_filename, fake_src_filename,
                  fake_header_filename):
    ast = parse_file(in_filename, use_cpp=True)
    v = FuncDeclVisitor()
    v.visit(ast)

    env = Environment(loader=PackageLoader('embody', 'templates'))
    with open(fake_header_filename, 'w') as fake_header:
        fake_header_template = env.get_template('fake.h')
        ctx = {
            'include_guard': fake_header_filename.upper().replace('.', '_'),
            'header': in_filename,
        }
        fake_header.write(fake_header_template.render(**ctx))

    with open(fake_src_filename, 'w') as fake_src:
        fake_src_template = env.get_template('fake.c')
        ctx = {
            'fake_include': fake_header_filename,
            'funcs': v.stubs
        }
        fake_src.write(fake_src_template.render(**ctx))
