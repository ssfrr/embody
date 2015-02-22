from jinja2 import Environment, PackageLoader
from pycparser import parse_file, c_ast
from pycparser.c_generator import CGenerator
import os
import sys
from os import path
import yaml
import logging

logger = logging.getLogger(__name__)


class EmbodyError(Exception):
    pass


class FuncDeclVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.stubs = []

    def visit_FuncDecl(self, node):
        gen = CGenerator()
        self.stubs.append(gen.visit(node))


def generate_fake(in_filename,
                  out_dir=None, out_src=None, out_header=None,
                  prefix=None, cpp_args=None):
    '''Parses the given header file and generates a fake implementation C file
    and fake wrapper header file. See _make_output_name for details on how the
    output filenames are generated from the arguments.'''
    cfg = _get_config()
    logger.debug('Loaded config: %s' % cfg)

    if prefix is None:
        prefix = cfg.get('fake_prefix', None)
    if out_dir is None:
        out_dir = cfg.get('fake_outdir', None)
    if cpp_args is None:
        cpp_args = cfg.get('fake_cpp_args', None)

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

    env = Environment(loader=PackageLoader('embody', 'templates'))
    with open(fake_header_filename, 'w') as fake_header:
        fake_header_template = env.get_template('fake.h')
        ctx = {
            'include_guard':
                path.basename(fake_header_filename).upper().replace('.', '_'),
            'header': path.basename(in_filename),
        }
        fake_header.write(fake_header_template.render(**ctx))
        logger.info('Generated %s' % fake_header_filename)

    with open(fake_src_filename, 'w') as fake_src:
        fake_src_template = env.get_template('fake.c')
        ctx = {
            'fake_include': path.basename(fake_header_filename),
            'funcs': v.stubs
        }
        fake_src.write(fake_src_template.render(**ctx))
        logger.info('Generated %s' % fake_src_filename)


def _get_config():
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

    # TODO: there's probably a better way to get the module path. I'm not sure
    # if this works if they do a "import embody as e"
    config = _get_dir_config(sys.modules['embody'].__path__[0])
    config.update(_get_dir_config(os.getenv('HOME')))
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


def _check_output_path(outpath):
    '''Checks the given output path to make sure we'll be able to create
    the output file there, creating the directories if necessary'''
    dirname = path.split(outpath)[0]
    if not path.isdir(dirname):
        if path.exists(dirname):
            raise EmbodyError('%s exists and is not a directory' % dirname)
        create = raw_input('%s does not exist, create it? [y/N] ' % dirname)
        if len(create) > 0 and create[0].lower() == 'y':
            os.makedirs(dirname)
        else:
            raise EmbodyError("Can't create file at %s" % outpath)
