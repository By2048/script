from pattern import *


def get_markdown_files(file_path):
    # md渲染顺序

    index = 0
    result = []

    def get_files(index, file):

        with open(file, 'r+', encoding='utf-8') as md:
            markdown = ''.join(md.readlines())
            if file.endswith('.md'):
                index += 1
                result.append([index, os.path.abspath(file)])

        for pattern in patterns:

            data = re.findall(pattern.match, markdown)
            if not data:
                continue
            for item in data:
                index_file = pattern.get_arg_index('file')
                file = item[index_file] if index_file >= 0 else ''
                if file:
                    get_files(index, file)

    get_files(index, file_path)

    result = sorted(result, key=lambda x: -x[0])

    result = [item[1] for item in result]

    return result
