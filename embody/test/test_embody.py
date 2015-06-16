import embody
from pkg_resources import resource_filename
from os import path


def get_pkg_filepath(path_components):
    '''Get a filename for a file in the embody package.
    path_components should be a list of path components that will
    be joined with `os.path.join`'''
    pkg_path = path.join(*path_components)
    return resource_filename('embody', pkg_path)


def check_generated_file_matches(expected_fname, generated_fname):
    with open(get_pkg_filepath(['test', 'data', expected_fname])) as f:
        expected = f.read()
    with open(generated_fname) as f:
        actual = f.read()
    assert expected == actual


def test_generate_empty_header():
    embody.generate_header(
        "/tmp/Empty.h",
        module_name='EmptyTest',
        author="Spencer Russell", year=2015)
    check_generated_file_matches('Empty.h', '/tmp/Empty.h')


def test_generate_filled_header():
    embody.generate_header(
        "/tmp/Filled.h",
        module_name='FilledTest',
        author="Spencer Russell", year=2015,
        sys_includes=['stdio.h', 'stdbool.h'],
        project_includes=['OtherModule.h'],
        defines={'PI': 3.14159, 'BUFLEN': 32},
        types=[
            '''typedef struct {
    float x;
    float y;
} point2'''],
        exported_funcs=[
            'point2 point2_add(point2 p1, point2 p2)',
            'float point2_length(point2 p)',
            'void fill_point2(point2 *p, float x, float y)',
            'void noop(void)',
            'void *something(void *thing)'])
    check_generated_file_matches('Filled.h', '/tmp/Filled.h')


def test_generate_empty_source():
    embody.generate_source(
        "/tmp/Empty.c",
        module_name='EmptyTest',
        author="Spencer Russell", year=2015)
    check_generated_file_matches('Empty.c', '/tmp/Empty.c')


def test_generate_filled_source():
    embody.generate_source(
        "/tmp/Filled.c",
        module_name='FilledTest',
        author="Spencer Russell", year=2015,
        sys_includes=['stdio.h', 'stdbool.h'],
        project_includes=['OtherModule.h'],
        defines={'PI': 3.14159, 'BUFLEN': 32},
        types=[
            '''typedef struct {
    float x;
    float y;
} point2'''],
        exported_funcs=[
            'point2 point2_add(point2 p1, point2 p2)',
            'float point2_length(point2 p)',
            'void fill_point2(point2 *p, float x, float y)',
            'void noop(void)',
            'void *something(void *thing)'],
        static_funcs=[
            'static void process(void)',
            'static int *intfunc(float x)'])
    check_generated_file_matches('Filled.c', '/tmp/Filled.c')


# def test_generate_fake():
#     out_dir = path.abspath(path.join(os.sep, 'tmp'))
#     embody.generate_fake(get_pkg_filepath(['test', 'data', 'FakeSpec.h']),
#                          out_dir=out_dir)
#     os.rm(path.join('out_dir', 'FakeFakeSpec.c'))
#     os.rm(path.join('out_dir', 'FakeFakeSpec.h'))


# def test_output_name_has_right_extension():
#     outname = embody.make_output_name('hello.c', None, None, '', '.txt')
#     assert outname == 'hello.txt'
#
#
# def test_output_name_has_right_prefix():
#     outname = embody.make_output_name('hello.c', None, None, 'Test', '.txt')
#     assert outname == 'Testhello.txt'
#
#
# def test_output_name_has_same_path_if_none_given():
#     outname = embody.make_output_name(
#         '/usr/local/src/hello.c', None, None, 'Test', '.txt')
#     assert outname == '/usr/local/src/Testhello.txt'
#
#
# def test_output_name_returns_outfile():
#     outname = embody.make_output_name(
#         '/usr/local/src/hello.c', '/test/file.txt')
#     assert outname == '/test/file.txt'
#
#
# def test_output_name_outfile_overrides_outdir():
#     outname = embody.make_output_name(
#         '/usr/local/src/hello.c', '/test/file.txt', '/tmp')
#     assert outname == '/test/file.txt'
#
#
# def test_output_name_uses_outdir():
#     outname = embody.make_output_name(
#         '/usr/local/src/hello.c', None, '/tmp', 'Test', '.txt')
#     assert outname == '/tmp/Testhello.txt'
#
#
# def test_output_name_uses_outdir_with_trailing_slash():
#     outname = embody.make_output_name(
#         '/usr/local/src/hello.c', None, '/tmp/', 'Test', '.txt')
#     assert outname == '/tmp/Testhello.txt'
