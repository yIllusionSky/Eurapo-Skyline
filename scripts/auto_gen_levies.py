#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from pathlib import Path

def process_levies_files(input_folder, coefficient):
    """
    扫描输入文件夹中的文件，添加TRY_REPLACE:前缀，将size乘以系数，打印到stdout

    Args:
        input_folder: 输入文件夹路径
        coefficient: 系数，用来乘以size值
    """
    # 确保输入路径存在
    if not os.path.isdir(input_folder):
        print(f"错误：输入路径不存在 - {input_folder}", flush=True)
        return

    file_count = 0
    total_levies = 0

    # 遍历输入文件夹中的所有文件
    for filename in sorted(os.listdir(input_folder)):
        input_filepath = os.path.join(input_folder, filename)

        # 只处理文件，跳过文件夹和README.md
        if not os.path.isfile(input_filepath) or filename == "README.md":
            continue

        try:
            # 读取原文件（处理 UTF-8 with BOM）
            with open(input_filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            # 处理文件内容
            modified_content = ""
            in_levy_block = False
            levy_name = ""

            lines = content.split('\n')
            for i, line in enumerate(lines):
                # 检测levy定义的开始（例如：levy_tribal_cavalry = {）
                match = re.match(r'^(\w+)\s*=\s*{', line)
                if match:
                    in_levy_block = True
                    levy_name = match.group(1)
                    # 添加TRY_REPLACE:前缀
                    modified_content += f"TRY_REPLACE:{line}\n"
                    total_levies += 1
                elif in_levy_block and line.strip().startswith("size"):
                    # 处理size行
                    size_match = re.match(r'^(\s*)size\s*=\s*([\d.]+)', line)
                    if size_match:
                        indent = size_match.group(1)
                        original_size = float(size_match.group(2))
                        new_size = original_size * coefficient
                        modified_content += f"{indent}size = {new_size}\n"
                    else:
                        modified_content += line + "\n"
                elif in_levy_block and line.strip() == "}":
                    # levy块结束
                    modified_content += line + "\n"
                    in_levy_block = False
                else:
                    modified_content += line + "\n"

            # 打印处理后的内容
            print(modified_content, end='', flush=True)
            file_count += 1

        except Exception as e:
            print(f"错误处理文件 {filename}：{e}", flush=True)
            continue

    print(f"\n# 处理完成！共处理 {file_count} 个文件，{total_levies} 个levy定义", flush=True)

def main():
    # ========== 配置部分 ==========

    # 输入文件夹路径（要扫描的文件夹）
    input_folder = "in_game/common/levies"

    # 系数
    coefficient = 2.0

    # ========== 执行部分 ==========

    # 转换为绝对路径
    if not os.path.isabs(input_folder):
        input_folder = os.path.join(os.getcwd(), input_folder)

    print(f"# 输入文件夹：{input_folder}", flush=True)
    print(f"# 系数：{coefficient}", flush=True)
    print("-" * 80, flush=True)

    # 执行处理
    process_levies_files(input_folder, coefficient)

if __name__ == "__main__":
    main()
