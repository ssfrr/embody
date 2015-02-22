import embody


def test_output_name_has_right_extension():
    outname = embody.make_output_name('hello.c', None, None, '', '.txt')
    assert outname == 'hello.txt'


def test_output_name_has_right_prefix():
    outname = embody.make_output_name('hello.c', None, None, 'Test', '.txt')
    assert outname == 'Testhello.txt'


def test_output_name_has_same_path_if_none_given():
    outname = embody.make_output_name(
        '/usr/local/src/hello.c', None, None, 'Test', '.txt')
    assert outname == '/usr/local/src/Testhello.txt'


def test_output_name_returns_outfile():
    outname = embody.make_output_name(
        '/usr/local/src/hello.c', '/test/file.txt')
    assert outname == '/test/file.txt'


def test_output_name_outfile_overrides_outdir():
    outname = embody.make_output_name(
        '/usr/local/src/hello.c', '/test/file.txt', '/tmp')
    assert outname == '/test/file.txt'


def test_output_name_uses_outdir():
    outname = embody.make_output_name(
        '/usr/local/src/hello.c', None, '/tmp', 'Test', '.txt')
    assert outname == '/tmp/Testhello.txt'


def test_output_name_uses_outdir_with_trailing_slash():
    outname = embody.make_output_name(
        '/usr/local/src/hello.c', None, '/tmp/', 'Test', '.txt')
    assert outname == '/tmp/Testhello.txt'
