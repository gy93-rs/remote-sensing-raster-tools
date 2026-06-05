"""Backward-compatible image rotation helpers.

New code should import from ``data_process.augmentation`` or use
``data-process rotate``.
"""

from data_process.augmentation import file_name, rotate


if __name__ == "__main__":
    print("Use `data-process rotate --help` for image rotation.")
