import os


def delete_file(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def delete_recursive(path: str, expected_files_tree: list[str] | None = None):
    deleted_folders = []

    for current_dir, _, files in os.walk(path, topdown=False):
        if not files:
            if expected_files_tree and len(deleted_folders) == len(expected_files_tree):
                break

            if not expected_files_tree or (
                expected_files_tree
                and current_dir.endswith(
                    os.path.join(*expected_files_tree[0 : len(expected_files_tree) - len(deleted_folders)])
                )
            ):
                print(f"Deleting {current_dir}")
                os.rmdir(current_dir)
                deleted_folders.append(current_dir)

        else:
            break

    return deleted_folders
