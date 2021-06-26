import os
import sys

from markdown import *


def main():
    file_path = sys.argv[-1]

    folder = os.path.dirname(file_path)
    file = os.path.basename(file_path)

    os.chdir(folder)

    os.environ.setdefault('work_folder', folder)

    files = get_markdown_files(file)

    for file in files:
        file_preview = get_new_file_path(file)
        if os.path.isfile(file_preview):
            print(f'remove {file_preview}')
            os.remove(file_preview)

    print()

    for file in files:
        with open(file, 'r+', encoding='utf-8') as md:
            markdown = ''.join(md.readlines())

        markdown = '\n' + markdown if not markdown.startswith('\n') else markdown
        markdown = markdown + '\n' if not markdown.endswith('\n') else markdown

        pattern: MarkdownPattern
        for pattern in patterns:
            markdown = re.sub(pattern.match, pattern.get_match_replace, markdown)

        file_path = get_new_file_path(file)
        with open(file_path, 'w+', encoding='utf-8') as md:
            md.write(markdown)
        print(f'create {file_path}')


if __name__ == '__main__':
    main()
