import hashlib
import os
import shutil
from pathlib import Path

COPY_ACTION = 'COPY'
MOVE_ACTION = 'MOVE'
DELETE_ACTION = 'DELETE'


def sync_explicit_dependencies(reader, filesystem, source_root, dest_root):
    source_hashes = reader(source_root)
    dest_hashes = reader(dest_root)

    actions = determine_actions(source_hashes, dest_hashes, source_root, dest_root)

    for action, *paths in actions:
        if action == COPY_ACTION:
            filesystem.copy(*paths)
        if action == MOVE_ACTION:
            filesystem.move(*paths)
        if action == DELETE_ACTION:
            filesystem.delete(paths[0])


def sync(source, dest):
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)
    actions = determine_actions(source_hashes, dest_hashes, source, dest)
    for action, *paths in actions:
        if action == COPY_ACTION:
            shutil.copyfile(*paths)
        if action == MOVE_ACTION:
            shutil.move(*paths)
        if action == DELETE_ACTION:
            os.remove(paths[0])


BLOCKSIZE = 65536


def hash_file(path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()


def determine_actions(src_hashes, dst_hashes, src_folder, dst_folder):
    for sha, filename in src_hashes.items():
        if sha not in dst_hashes:
            sourcepath = f"{src_folder}/{filename}"
            destpath = f"{dst_folder}/{filename}"
            yield COPY_ACTION, sourcepath, destpath

        elif dst_hashes[sha] != filename:
            olddestpath = f"{dst_folder}/{dst_hashes[sha]}"
            newdestpath = f"{dst_folder}/{filename}"
            yield MOVE_ACTION, olddestpath, newdestpath

    for sha, filename in dst_hashes.items():
        if sha not in src_hashes:
            yield DELETE_ACTION, f"{dst_folder}/{filename}"


def read_paths_and_hashes(root):
    hashes = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            hashes[hash_file(Path(folder) / fn)] = fn
    return hashes
