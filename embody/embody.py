from jinja2 import Environment, PackageLoader
from pycparser import parse_file, c_ast
from pycparser.c_generator import CGenerator
import os
from getpass import getuser
from os import path
import yaml
from filters import template_filters
import logging
from datetime import date

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


#
# These are the high-level functions that typically use a lot of the execution
# state (current directory, config files, etc.)
#

def generate_fake(in_filename, cfg):
    '''Parses the given header file and generates a fake implementation C file
    and fake wrapper header file. See _make_output_name for details on how the
    output filenames are generated from the arguments.'''

    pathname, basename = path.split(in_filename)
    prefix = cfg.get('fake_prefix', '')
    out_dir = cfg.get('fake_dir', pathname)
    cpp_args = cfg.get('cpp_args', [])
    basename = '.'.join(basename.split('.')[:-1])

    logger.info('Parsing %s...' % in_filename)
    ast = parse_file(in_filename, use_cpp=True, cpp_args=cpp_args)
    if not ast.children():
        raise EmbodyError('Parsed AST is empty')
    v = FuncDeclVisitor()
    v.visit(ast)

    fake_src_filename = path.join(out_dir, prefix + basename + '.c')
    _check_output_path(fake_src_filename)
    fake_header_filename = path.join(out_dir, prefix + basename + '.h')
    _check_output_path(fake_header_filename)

    # TODO: we need to figure out how to only generate function definitions
    # from functions actually declared in the header, and not from includes. We
    # also should avoid generating definitions for functions declared inline.
    # We should also check the return type of the declared function and make
    # sure that our generated function returns an object of that type, to avoid
    # compiler warnings.

    generate_header(fake_header_filename, cfg)
    generate_source(fake_src_filename, cfg)


def generate_module(module_name, cfg):
    if " " in module_name:
        raise EmbodyError("No spaces allowed in module names")
    src_dir = cfg.get('src_dir', '')
    test_dir = cfg.get('test_dir', '')
    src_basename = module_name + '.c'
    header_basename = module_name + '.h'
    test_basename = 'Test' + module_name + '.cpp'
    src_filename = path.join(src_dir, src_basename)
    header_filename = path.join(src_dir, header_basename)
    test_filename = path.join(test_dir, test_basename)
    # first set the common attributes
    ctx_common = cfg.copy()
    ctx_common['year'] = date.today().year
    ctx_common['module_name'] = module_name

    ctx_src = ctx_common.copy()
    ctx_src['use_include_guard'] = False
    ctx_src['filename'] = src_basename
    ctx_src['project_includes'] = [header_basename]
    _generate_file(src_filename, 'Template.c', ctx_src)

    ctx_test = ctx_common.copy()
    ctx_test['use_include_guard'] = False
    ctx_test['filename'] = test_basename
    ctx_test['project_includes'] = [header_basename]
    _generate_file(test_filename, 'TestTemplate.cpp', ctx_test)

    ctx_header = ctx_common.copy()
    ctx_header['use_include_guard'] = True
    ctx_header['filename'] = header_basename
    _generate_file(header_filename, 'Template.h', ctx_header)

    logger.info("\nDon't forget to add %s and %s to your build system" %
                (src_basename, test_basename))


loaded_config = None


def save_config(cfg, filename):
    '''Takes the given configuration dict and saves it as a YAML file to the
    given location'''
    if path.exists(filename):
        if not _ask_user('%s exists, overwrite?' % filename):
            raise EmbodyError("Can't create file at %s" % filename)
    with open(filename, 'w') as f:
        yaml.dump(cfg, f)


def get_config(cmd_args=None, force_reload=False):
    '''Searches for embody config files and returns a dictionary of options. A
    config file is called either .embodyrc.yaml or .embody/config.yaml. We
    search in $HOME, then the project root. The project root is assumed to be
    the first parent directory where we find a .git or .hg directory.

    All config files found are combined, with later files overriding earlier.
    This means that you can have settings in $HOME/.embodyrc.yaml that are
    generally useful, and then override them on a project-by-project basis.

    Finally, cmd_args is a dictionary that has the final say'''

    global loaded_config
    if loaded_config is not None and not force_reload:
        return loaded_config
    else:
        loaded_config = {}
        loaded_config.update(_get_dir_config(os.getenv('HOME')))
        project_root = _find_project_root(os.getcwdu())
        if project_root is not None:
            loaded_config.update(_get_dir_config(project_root))
        if cmd_args is not None:
            loaded_config.update(cmd_args)
        _set_config_defaults(loaded_config, project_root)
        return loaded_config


def _set_config_defaults(cfg, project_root):
    '''Sets any default values that are missing from the given config.
    We do this at the end so that we can set values that depend on others
    that may be given from other configs'''

    if 'cpp_args' not in cfg:
        cfg['cpp_args'] = []
    if 'project_root' not in cfg and project_root is not None:
        cfg['project_root'] = project_root
    if 'src_dir' not in cfg and 'project_root' in cfg:
        cfg['src_dir'] = path.join(cfg['project_root'], 'src')
    if 'test_dir' not in cfg and 'project_root' in cfg:
        cfg['test_dir'] = path.join(cfg['project_root'], 'test')
    if 'fake_dir' not in cfg and 'test_dir' in cfg:
        cfg['fake_dir'] = path.join(cfg['test_dir'], 'fakes')
    if 'project_name' not in cfg and 'project_root' in cfg:
        cfg['project_name'] = path.basename(cfg['project_root'])
    if 'author' not in cfg:
        cfg['author'] = getuser()
    if 'fake_prefix' not in cfg:
        cfg['fake_prefix'] = 'Fake'


# These are the slightly lower-level (but public) functions that don't load in
# any user context (current directory or config files) so their behavior should
# be determined solely from their arguments.


def generate_source(filename, ctx):
    ctx = dict(ctx)
    ctx['use_include_guard'] = False
    ctx['filename'] = path.basename(filename)
    _generate_file(filename, 'Template.c', ctx)


def generate_header(filename, ctx):
    ctx = dict(ctx)
    ctx['use_include_guard'] = True
    ctx['filename'] = path.basename(filename)
    _generate_file(filename, 'Template.h', ctx)


#
# Internal (non-public) functions
#


def _generate_file(filename, template_filename, render_context):
    if path.exists(filename):
        if not _ask_user('%s exists, overwrite?' % filename):
            raise EmbodyError("Can't create file at %s" % filename)
    with open(filename, 'w') as f:
        template = template_env.get_template(template_filename)
        f.write(template.render(**render_context))
        logger.info('Generated %s' % filename)


def _find_project_root(start_path):
    root_files = {'.git', '.hg'}
    current_path = start_path
    while True:
        logger.debug("Looking for project root in %s" % current_path)
        dirfiles = set(os.listdir(current_path))
        if dirfiles.intersection(root_files):
            return current_path
        else:
            parent_path = os.path.split(current_path)[0]
            if parent_path == current_path:
                return None
            else:
                current_path = parent_path


def _get_dir_config(path):
    '''Looks for a config file in the given directory'''
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
            config.update(yaml.safe_load(cfgfile))

    if cfgdirname in dirfiles and \
            cfgdirfilename in os.listdir(
                os.path.join(path, cfgdirname)):
        name = os.path.join(path, cfgdirname, cfgdirfilename)
        with open(name) as cfgfile:
            logger.debug('Found %s' % name)
            config.update(yaml.safe_load(cfgfile))

    return config


def _make_output_name(in_name, prefix, extension, out_dir):
    '''Generates a full output filename given the input filename, a target
    directory, a prefix, and an extension. If a directory is given, the output
    is in that directory with a filename based on the input filename, using the
    given prefix and extension. If no output directory is given, the same
    directory as the given file is used.'''

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
