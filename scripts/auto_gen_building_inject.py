#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from pathlib import Path

def parse_building_files(folder_path, search_keys):
    """
    遍历文件夹中的所有文件，查找指定的键值对

    Args:
        folder_path: 要遍历的文件夹路径
        search_keys: 要查找的键值对列表，例如 ["city = yes", "super_metropolis = yes"]

    Returns:
        包含找到的building和对应键值对的列表
    """
    results = []

    # 确保路径存在
    if not os.path.isdir(folder_path):
        print(f"错误：路径不存在 - {folder_path}")
        return results

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)

        # 只处理文件，跳过文件夹
        if not os.path.isfile(filepath):
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取所有building定义
            # 模式：building_name = { ... }
            building_pattern = r'(\w+)\s*=\s*\{'

            current_pos = 0
            for match in re.finditer(building_pattern, content):
                building_name = match.group(1)
                start_pos = match.start()

                # 找到这个building的范围
                # 从 { 开始，找对应的 }
                brace_count = 1
                pos = match.end()
                building_end = -1

                while pos < len(content) and brace_count > 0:
                    if content[pos] == '{':
                        brace_count += 1
                    elif content[pos] == '}':
                        brace_count -= 1
                    pos += 1

                if brace_count == 0:
                    building_end = pos
                    building_content = content[match.start():building_end]

                    # 检查这个building中是否存在任何search_keys
                    found_keys = []
                    for key in search_keys:
                        # 使用正则表达式查找键值对
                        # 支持前后有空白字符
                        key_pattern = re.escape(key)
                        if re.search(key_pattern, building_content):
                            found_keys.append(key)

                    if found_keys:
                        results.append({
                            'building_name': building_name,
                            'filename': filename,
                            'found_keys': found_keys
                        })

        except Exception as e:
            print(f"警告：处理文件 {filename} 时出错 - {e}")
            continue

    return results

def generate_inject_statements(results, inject_content_list):
    """
    生成TRY_INJECT语句

    Args:
        results: parse_building_files的返回结果
        inject_content_list: 要注入的内容数组，例如 ["city = yes", "super_tag = yes"]

    Returns:
        TRY_INJECT语句列表
    """
    inject_statements = []

    for item in results:
        building_name = item['building_name']
        # 将数组中的每一项用制表符分隔
        content_lines = "\n\t".join(inject_content_list)
        inject_stmt = f"TRY_INJECT:{building_name} = {{\n\t{content_lines}\n}}"
        inject_statements.append(inject_stmt)

    return inject_statements

def main():
    # ========== 配置部分 ==========

    # 要遍历的文件夹路径
    folder_to_scan = r"C:\My\Program\Steam\steamapps\common\Europa Universalis V\game\in_game\common\building_types"  # 修改为你要扫描的文件夹

    # 要查找的键值对列表
    # 例如：找所有包含 "city = yes" 的building
    search_keys = [
        "city = yes",
    ]

    # 要注入的内容数组
    inject_content = [
        "super_metropolis = yes"
    ]  # 修改为你要注入的内容

    # ========== 执行部分 ==========

    # 转换为绝对路径
    if not os.path.isabs(folder_to_scan):
        folder_to_scan = os.path.join(os.getcwd(), folder_to_scan)

    print(f"扫描文件夹：{folder_to_scan}")
    print(f"查找键值对：{search_keys}")
    print(f"注入内容：{inject_content}")
    print("-" * 80)

    # 查找符合条件的buildings
    results = parse_building_files(folder_to_scan, search_keys)

    if not results:
        print("未找到任何符合条件的building")
        return

    print(f"找到 {len(results)} 个符合条件的building\n")

    # 生成TRY_INJECT语句
    inject_statements = generate_inject_statements(results, inject_content)

    # 输出结果
    for i, stmt in enumerate(inject_statements, 1):
        print(stmt)
        if i < len(inject_statements):
            print()  # 在语句之间添加空行

if __name__ == "__main__":
    main()
