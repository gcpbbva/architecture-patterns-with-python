from app.start_sync import sync_explicit


class FakeFileSystem(list):

    def copy(self, src, dest):
        self.append(('COPY', src, dest))

    def move(self, src, dest):
        self.append(('MOVE', src, dest))

    def delete(self, dest):
        self.append(('DELETE', dest))


def test_when_a_file_exists_in_the_source_but_not_the_destination():
    source = {"sha1": "my-file"}
    dest = {}
    filesystem = FakeFileSystem()

    reader = {"/source": source, "/dest": dest}
    sync_explicit(reader.pop, filesystem, "/source", "/dest")

    assert filesystem == [("COPY", "/source/my-file", "/dest/my-file")]


def test_when_a_file_has_been_renamed_in_the_source():
    source = {"sha1": "renamed-file" }
    dest = {"sha1": "original-file" }
    filesystem = FakeFileSystem()

    reader = {"/source": source, "/dest": dest}

    sync_explicit(reader.pop, filesystem, "/source", "/dest")

    assert filesystem == [("MOVE", "/dest/original-file", "/dest/renamed-file")]


def test_when_several_use_cases_should_return_all_the_actions():
    source = {"hash1": "fn1", "hash2": "fn2", "hash3": "fn3"}
    dest = {"hash0": "fn0", "hash3": "fn44"}

    filesystem = FakeFileSystem()
    reader = {"/src": source, "/dst": dest}

    sync_explicit(reader.pop, filesystem, "/src", "/dst")

    assert filesystem == [
        ("COPY", "/src/fn1", "/dst/fn1"),
        ("COPY", "/src/fn2", "/dst/fn2"),
        ("MOVE", "/dst/fn44", "/dst/fn3"),
        ("DELETE", "/dst/fn0")
    ]