from jinja2 import Environment, PackageLoader
import clang.cindex


def open_fakefiles(infilename, outfile_basename):
    if outfile_basename is None:
        if infilename.endswith('.h'):
            outfile_basename = 'Fake' + infilename[0:-2]
        else:
            print("%s doesn't end with .c and no outfilename given, \n" +
                  "I'm confused what to call it" % infilename)
    fake_src = open(outfile_basename + '.c', 'w')
    fake_header = open(outfile_basename + '.h', 'w')
    return fake_src, fake_header


def get_template_env():
    env = Environment(loader=PackageLoader('embody', 'templates'))
    print env


def get_fake_header():
    return ''


def get_fake_source():
    return ''


def parse_header(header_filename):
    clang.cindex.Config.set_library_path(
        '/Library/Developer/CommandLineTools/usr/lib/')
    tu = clang.cindex.TranslationUnit.from_source(header_filename)
    for node in tu.cursor.get_children():
        pass
