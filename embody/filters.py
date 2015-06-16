'''This is a set of Jinja2 filters useful in rendering source files'''


def section_header(title):
    '''Makes a section title into a more prominent section header'''
    over_under = '*' * len(title)
    return '\n'.join([
        '/**' + over_under + '**',
        ' * ' + title      + ' *',
        ' **' + over_under + '**/'])


def include_guard(filename):
    '''formats a filename as an include guard define'''
    filename = filename.replace('.', '_')
    return '__' + filename.upper()


template_filters = {
    'section_header': section_header,
    'include_guard': include_guard
}
