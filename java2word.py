import os
from docx import Document

# 扫描指定目录下的所有Java文件
def scan_java_files(directory):
    java_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files

# 读取Java文件的内容
def read_java_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# 将代码插入到Word文档中
def add_code_to_word(doc, code):
    # 将Java代码作为文本插入，使用Code格式（可以适当修改样式）
    doc.add_paragraph(code, style='Normal')

# 主函数
def main(directory, output_word):
    # 创建一个Word文档
    doc = Document()

    # 获取所有Java文件
    java_files = scan_java_files(directory)

    # 遍历所有Java文件并将其内容添加到Word文档
    for java_file in java_files:
        code = read_java_file(java_file)
        add_code_to_word(doc, code)

    # 保存Word文档
    doc.save(output_word)
    print(f"Java代码已经整理到 {output_word}")

if __name__ == "__main__":
    # 设置扫描的目录路径和输出Word文档的文件名
    directory = input("请输入要扫描的目录路径: ")
    output_word = input("请输入输出的Word文档名称（例如 output.docx）: ")

    main(directory, output_word)
