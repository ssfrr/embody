from jinja2 import Environment, PackageLoader
from pycparser import parse_file, c_ast
from pycparser.c_generator import CGenerator
import os
import sys
from os import path
import yaml
from filters import template_filters
import logging

logger = logging.getLogger(__name__)
template_env = Environment(loader=PackageLoader('embody', 'templates'),
                           trim_blocks=True,
                           keep_trailing_newline=True)
template_env.filters.update(template_filters)


class EmbodyError(Exception):
    pass


class FuncDeclVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.stubs = []

    def visit_FuncDecl(self, node):
        gen = CGenerator()
        self.stubs.append(gen.visit(node))


def _generate_file(filename, template_filename, render_context):
    with open(filename, 'w') as f:
        template = template_env.get_template(template_filename)
        f.write(template.render(**render_context))
        logger.info('Generated %s' % filename)


def generate_source(filename, **ctx):
    ctx['use_include_guard'] = False
    ctx['filename'] = path.basename(filename)
    _generate_file(filename, 'template.c', ctx)


def generate_header(filename, **ctx):
    ctx['use_include_guard'] = True
    ctx['filename'] = path.basename(filename)
    _generate_file(filename, 'template.h', ctx)


def generate_fake(in_filename,
                  out_dir=None, out_src=None, out_header=None,
                  prefix=None, cpp_args=None):
    '''Parses the given header file and generates a fake implementation C file
    and fake wrapper header file. See _make_output_name for details on how the
    output filenames are generated from the arguments.'''
    cfg = get_config()

    if prefix is None:
        prefix = cfg.get('fake_prefix', None)
    if out_dir is None:
        out_dir = cfg.get('fake_outdir', None)
    if cpp_args is None:
        cpp_args = cfg.get('fake_cpp_args', '')

    logger.info('Parsing %s...' % in_filename)
    ast = parse_file(in_filename, use_cpp=True, cpp_args=cpp_args)
    if not ast.children():
        raise EmbodyError('Parsed AST is empty')
    v = FuncDeclVisitor()
    v.visit(ast)

    fake_src_filename = _make_output_name(
        in_filename, out_src, out_dir, prefix, '.c')
    _check_output_path(fake_src_filename)
    fake_header_filename = _make_output_name(
        in_filename, out_header, out_dir, prefix, '.h')
    _check_output_path(fake_header_filename)

    # TODO: we need to figure out how to only generate function definitions
    # from functions actually declared in the header, and not from includes. We
    # also should avoid generating definitions for functions declared inline.
    # We should also check the return type of the declared function and make
    # sure that our generated function returns an object of that type, to avoid
    # compiler warnings.

    generate_header(fake_header_filename)
    generate_source(fake_src_filename)



def test_templates():
    pass


loaded_config = None
def get_config(force_reload=False):
    '''Searches for embody config files and returns a dictionary of options. A
    config file is called either .embodyrc.yaml or .embody/config.yaml. We
    first load the default config shipped with the embody package. Then we
    search in $HOME, then the project root, then any directories in the path
    between the project root and the current directory. The project root is
    assumed to be the first parent directory where we find a .git or .hg
    directory.

    All config files found are combined, with later files overriding earlier.
    This means that you can have settings in $HOME/.embodyrc.yaml that are
    generally useful, and then override them on a project-by-project basis'''

    global loaded_config
    if loaded_config is not None and not force_reload:
        return loaded_config
    else:
        # TODO: there's probably a better way to get the module path. I'm not
        # sure if this works if they do a "import embody as e"
        loaded_config = _get_dir_config(sys.modules['embody'].__path__[0])
        loaded_config.update(_get_dir_config(os.getenv('HOME')))
        loaded_config.update(_get_project_config(os.getcwdu()))
        return loaded_config


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

    logger.debug('Searching for config files in %s' % path)

    if cfgfilename in dirfiles:
        name = os.path.join(path, cfgfilename)
        with open(name) as cfgfile:
            logger.debug('Found %s' % name)
            config.update(yaml.load(cfgfile))

    if cfgdirname in dirfiles and \
            cfgdirfilename in os.listdir(
                os.path.join(path, cfgdirname)):
        name = os.path.join(path, cfgdirname, cfgdirfilename)
        with open(name) as cfgfile:
            logger.debug('Found %s' % name)
            config.update(yaml.load(cfgfile))

    return config


def _make_output_name(in_name, out_name=None,
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


def _ask_user(prompt, default=False):
    prompt += ' [Y/n] ' if default else ' [y/N] '
    inpt = raw_input(prompt)
    if len(inpt) == 0:
        return default
    if default and inpt[0].lower() == 'n':
        return False
    if not default and inpt[0].lower() == 'y':
        return True
    return default


def _check_output_path(outpath):
    '''Checks the given output path to make sure we'll be able to create
    the output file there, creating the directories if necessary'''
    dirname = path.split(outpath)[0]
    if not path.isdir(dirname):
        if path.exists(dirname):
            raise EmbodyError('%s exists and is not a directory' % dirname)
        if _ask_user('%s does not exist, create it?' % dirname):
            os.makedirs(dirname)
        else:
            raise EmbodyError("Can't create file at %s" % outpath)
    elif path.exists(outpath):
        if not _ask_user('%s exists, overwrite?' % outpath):
            raise EmbodyError("Can't create file at %s" % outpath)
