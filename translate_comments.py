#!/usr/bin/env python3
"""
自动翻译Python文件中的英文注释为中文注释的脚本

此脚本会：
1. 扫描指定目录下的所有Python文件
2. 识别英文注释（包括单行注释和文档字符串）
3. 使用AI模型将英文注释翻译为中文
4. 为代码添加详细的中文注释
5. 保持代码结构和格式不变
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# 导入OpenAI客户端用于翻译
from openai import OpenAI


class CommentTranslator:
    """Python注释翻译器类"""
    
    def __init__(self, base_url: str = "http://localhost:8000/v1", 
                 model: str = "autoglm-phone-9b",
                 api_key: str = "EMPTY"):
        """
        初始化翻译器
        
        参数:
            base_url: AI模型API的基础URL
            model: 使用的模型名称
            api_key: API密钥
        """
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        
    def translate_text(self, text: str, context: str = "comment") -> str:
        """
        使用AI模型翻译文本
        
        参数:
            text: 要翻译的英文文本
            context: 文本的上下文类型（comment/docstring/code）
            
        返回:
            翻译后的中文文本
        """
        # 如果文本已经包含中文，直接返回
        if self._contains_chinese(text):
            return text
            
        # 如果文本太短或只是符号，不翻译
        if len(text.strip()) < 3 or not any(c.isalpha() for c in text):
            return text
        
        # 构建翻译提示
        if context == "docstring":
            prompt = f"""请将以下Python文档字符串从英文翻译为中文，保持格式和结构：

{text}

只返回翻译后的中文文本，不要添加任何解释。"""
        else:
            prompt = f"""请将以下Python注释从英文翻译为中文：

{text}

只返回翻译后的中文文本，不要添加#符号或其他前缀。"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3,
            )
            
            if response.choices and len(response.choices) > 0:
                translated = response.choices[0].message.content.strip()
                # 清理可能的引号
                translated = translated.strip('"\'')
                return translated
            else:
                return text
                
        except Exception as e:
            print(f"翻译错误: {e}")
            return text
    
    def _contains_chinese(self, text: str) -> bool:
        """检查文本是否包含中文字符"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def translate_file(self, file_path: str, dry_run: bool = False) -> bool:
        """
        翻译单个Python文件中的注释
        
        参数:
            file_path: Python文件路径
            dry_run: 如果为True，只显示将要进行的更改，不实际修改文件
            
        返回:
            成功返回True，失败返回False
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            lines = content.split('\n')
            translated_lines = []
            
            in_docstring = False
            docstring_delimiter = None
            docstring_lines = []
            docstring_start_idx = 0
            
            for i, line in enumerate(lines):
                # 检查是否是文档字符串的开始或结束
                stripped = line.strip()
                
                # 处理文档字符串
                if not in_docstring:
                    # 检查是否是文档字符串的开始
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        delimiter = '"""' if '"""' in line else "'''"
                        
                        # 单行文档字符串
                        if stripped.count(delimiter) >= 2 and len(stripped) > 6:
                            # 提取文档字符串内容
                            doc_content = stripped.strip(delimiter)
                            if doc_content and not self._contains_chinese(doc_content):
                                translated = self.translate_text(doc_content, "docstring")
                                indent = len(line) - len(line.lstrip())
                                translated_lines.append(' ' * indent + delimiter + translated + delimiter)
                            else:
                                translated_lines.append(line)
                        else:
                            # 多行文档字符串开始
                            in_docstring = True
                            docstring_delimiter = delimiter
                            docstring_lines = [line]
                            docstring_start_idx = i
                    # 处理单行注释
                    elif '#' in line:
                        # 分离代码和注释
                        code_part, comment_part = self._split_code_comment(line)
                        
                        if comment_part and not self._contains_chinese(comment_part):
                            translated_comment = self.translate_text(comment_part, "comment")
                            translated_lines.append(code_part + '  # ' + translated_comment)
                        else:
                            translated_lines.append(line)
                    else:
                        translated_lines.append(line)
                else:
                    # 在文档字符串内部
                    docstring_lines.append(line)
                    
                    if docstring_delimiter in stripped:
                        # 文档字符串结束
                        in_docstring = False
                        
                        # 提取并翻译文档字符串
                        full_docstring = '\n'.join(docstring_lines)
                        indent = len(docstring_lines[0]) - len(docstring_lines[0].lstrip())
                        
                        # 提取文档字符串内容（去除分隔符）
                        doc_content_lines = []
                        for j, dline in enumerate(docstring_lines):
                            if j == 0:
                                # 第一行，去除开始的分隔符
                                content = dline.strip().lstrip(docstring_delimiter)
                                if content:
                                    doc_content_lines.append(content)
                            elif j == len(docstring_lines) - 1:
                                # 最后一行，去除结束的分隔符
                                content = dline.strip().rstrip(docstring_delimiter)
                                if content:
                                    doc_content_lines.append(content)
                            else:
                                # 中间行
                                doc_content_lines.append(dline.strip())
                        
                        doc_content = '\n'.join(doc_content_lines)
                        
                        if doc_content and not self._contains_chinese(doc_content):
                            # 翻译文档字符串
                            translated_doc = self.translate_text(doc_content, "docstring")
                            
                            # 重新构建文档字符串
                            translated_lines.append(' ' * indent + docstring_delimiter)
                            for trans_line in translated_doc.split('\n'):
                                if trans_line.strip():
                                    translated_lines.append(' ' * indent + trans_line)
                            translated_lines.append(' ' * indent + docstring_delimiter)
                        else:
                            # 保持原样
                            translated_lines.extend(docstring_lines)
                        
                        docstring_lines = []
            
            # 合并翻译后的内容
            translated_content = '\n'.join(translated_lines)
            
            # 如果是dry run模式，只显示差异
            if dry_run:
                if translated_content != original_content:
                    print(f"\n{'='*60}")
                    print(f"文件: {file_path}")
                    print(f"{'='*60}")
                    print("将进行翻译...")
                    return True
                else:
                    print(f"跳过（无需翻译）: {file_path}")
                    return True
            
            # 写入翻译后的内容
            if translated_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(translated_content)
                print(f"✓ 已翻译: {file_path}")
                return True
            else:
                print(f"- 跳过（无需翻译）: {file_path}")
                return True
                
        except Exception as e:
            print(f"✗ 处理文件失败 {file_path}: {e}")
            return False
    
    def _split_code_comment(self, line: str) -> Tuple[str, str]:
        """
        分离代码行中的代码部分和注释部分
        
        参数:
            line: 代码行
            
        返回:
            (代码部分, 注释部分) 的元组
        """
        # 简单的分割，不处理字符串中的#
        if '#' not in line:
            return line, ''
        
        # 查找第一个不在字符串中的#
        in_string = False
        string_char = None
        
        for i, char in enumerate(line):
            if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
            elif char == '#' and not in_string:
                code_part = line[:i].rstrip()
                comment_part = line[i+1:].strip()
                return code_part, comment_part
        
        return line, ''


def find_python_files(directory: str, exclude_dirs: List[str] = None) -> List[str]:
    """
    递归查找目录下的所有Python文件
    
    参数:
        directory: 要搜索的目录
        exclude_dirs: 要排除的目录列表
        
    返回:
        Python文件路径列表
    """
    if exclude_dirs is None:
        exclude_dirs = ['venv', '.venv', '__pycache__', '.git', '.idea', 'build', 'dist', 'node_modules']
    
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        # 排除指定的目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='自动翻译Python文件中的英文注释为中文',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 翻译当前目录下的所有Python文件
    python translate_comments.py .
    
    # 翻译指定目录
    python translate_comments.py /path/to/project
    
    # 只显示将要翻译的文件，不实际修改
    python translate_comments.py . --dry-run
    
    # 使用自定义模型API
    python translate_comments.py . --base-url http://localhost:8000/v1 --model gpt-4
        """
    )
    
    parser.add_argument(
        'directory',
        type=str,
        help='要处理的目录路径'
    )
    
    parser.add_argument(
        '--base-url',
        type=str,
        default=os.getenv('PHONE_AGENT_BASE_URL', 'http://localhost:8000/v1'),
        help='模型API基础URL'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default=os.getenv('PHONE_AGENT_MODEL', 'autoglm-phone-9b'),
        help='模型名称'
    )
    
    parser.add_argument(
        '--apikey',
        type=str,
        default=os.getenv('PHONE_AGENT_API_KEY', 'EMPTY'),
        help='API密钥'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='只显示将要进行的更改，不实际修改文件'
    )
    
    parser.add_argument(
        '--exclude',
        type=str,
        nargs='+',
        default=['venv', '.venv', '__pycache__', '.git', '.idea'],
        help='要排除的目录列表'
    )
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    if not os.path.isdir(args.directory):
        print(f"错误: 目录不存在: {args.directory}")
        sys.exit(1)
    
    # 查找所有Python文件
    print(f"正在扫描目录: {args.directory}")
    python_files = find_python_files(args.directory, args.exclude)
    
    if not python_files:
        print("未找到Python文件")
        sys.exit(0)
    
    print(f"找到 {len(python_files)} 个Python文件")
    
    if args.dry_run:
        print("\n【DRY RUN模式 - 不会实际修改文件】\n")
    
    # 创建翻译器
    translator = CommentTranslator(
        base_url=args.base_url,
        model=args.model,
        api_key=args.apikey
    )
    
    # 翻译每个文件
    success_count = 0
    fail_count = 0
    
    for i, file_path in enumerate(python_files, 1):
        print(f"\n[{i}/{len(python_files)}] 处理: {file_path}")
        
        if translator.translate_file(file_path, dry_run=args.dry_run):
            success_count += 1
        else:
            fail_count += 1
    
    # 显示总结
    print(f"\n{'='*60}")
    print(f"翻译完成!")
    print(f"成功: {success_count} 个文件")
    print(f"失败: {fail_count} 个文件")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
