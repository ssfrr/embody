from jinja2 import Environment, PackageLoader
from clang.cindex import TranslationUnit, CursorKind
import clang.cindex


class FuncProto:
    def __init__(self, name, ret_type, args):
        self.name = name
        self.ret_type = ret_type
        # args is a list of ('type', 'name') tuples
        self.args = args

    @classmethod
    def from_cursor(cls, cursor):
        ret_type = None
        args = []
        name = ""
        if cursor.kind != CursorKind.FUNCTION_DECL:
            raise ValueError(
                "Cursor kind was %s instead of CursorKind.FUNCTION_DECL"
                % cursor.kind)
        name = cursor.spelling
        for child in cursor.get_children():
            if child.kind == CursorKind.TYPE_REF:
                ret_type = child.displayname
            elif child.kind == CursorKind.PARM_DECL:
                args.append((child.type.spelling, child.spelling))
        if ret_type is None:
            ret_type = 'void'
        return FuncProto(name, ret_type, args)


def generate_fake(in_filename, fake_src_filename,
                  fake_header_filename):
    env = Environment(loader=PackageLoader('embody', 'templates'))
    with open(fake_header_filename, 'w') as fake_header:
        fake_header_template = env.get_template('fake.h')
        ctx = {
            'include_guard': fake_header_filename.upper().replace('.', '_'),
            'header': in_filename,
        }
        fake_header.write(fake_header_template.render(**ctx))

    with open(fake_src_filename, 'w') as fake_src:
        funcs = get_funcs(in_filename)
        fake_src_template = env.get_template('fake.c')
        ctx = {
            'fake_include': fake_header_filename,
            'funcs': funcs
        }
        fake_src.write(fake_src_template.render(**ctx))


def get_funcs(header_filename):
    clang.cindex.Config.set_library_path(
        '/Library/Developer/CommandLineTools/usr/lib/')
    tu = TranslationUnit.from_source(header_filename)
    funcs = []
    for node in tu.cursor.get_children():
        if node.kind == CursorKind.FUNCTION_DECL:
            funcs.append(FuncProto.from_cursor(node))
    return funcs
