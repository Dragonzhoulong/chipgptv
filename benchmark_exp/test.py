#!/usr/bin/env python3
"""
简单测试脚本：使用LLM生成adder_8bit.v并用iverilog验证
"""

import os
import re
import subprocess
import time
from openai import OpenAI

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv 未安装，使用其他方式

# 获取API密钥 - 支持多种方式
api_key = os.getenv("OPENAI_API_KEY")

# 如果环境变量中没有，尝试从配置文件读取
if not api_key:
    api_keys = os.getenv("OPENAI_API_KEYS", "")
    if api_keys:
        api_key = api_keys.split(",")[0].strip()

if not api_key:
    print("[ERROR] 未找到OpenAI API密钥!")
    print("       请设置环境变量: export OPENAI_API_KEY=your-key")
    print("       或创建 .env 文件并添加: OPENAI_API_KEY=your-key")
    exit(1)

# 初始化OpenAI客户端
client = OpenAI(api_key=api_key)


def extract_verilog_code(text):
    """
    从LLM响应中提取Verilog代码
    支持 ```verilog ... ``` 或 ```systemverilog ... ``` 格式
    """
    # 尝试匹配 ```verilog 或 ```systemverilog 代码块
    pattern = r'```(?:verilog|systemverilog)\s*\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    if matches:
        return matches[0].strip()

    # 如果没有找到,尝试匹配普通的 ``` 代码块
    pattern = r'```\s*\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL)

    if matches:
        # 检查是否包含module关键字
        for match in matches:
            if 'module' in match:
                return match.strip()

    # 如果都没找到,返回原文本
    return text.strip()


def llm_generate_verilog(model_name, design_description, module_name):
    """
    调用LLM生成Verilog代码

    Args:
        model_name: 模型名称,如 "gpt-4o-mini"
        design_description: 设计描述文本
        module_name: 模块名称

    Returns:
        生成的Verilog代码字符串,如果失败返回None
    """
    prompt = f"""{design_description}

Please generate complete Verilog code for this module. Include all necessary logic.
Only output the Verilog code, wrapped in ```verilog ``` code block."""

    print(f"[LLM] 调用 {model_name} 生成 {module_name} 模块...")

    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            timeout=30
        )

        full_response = response.choices[0].message.content
        duration = time.time() - start_time

        print(f"[LLM] 响应接收完成,耗时 {duration:.2f}s")

        # 提取Verilog代码
        verilog_code = extract_verilog_code(full_response)

        return verilog_code, full_response

    except Exception as e:
        print(f"[ERROR] LLM调用失败: {e}")
        return None, None


def verify_with_iverilog(verilog_file, testbench_file, timeout=5):
    """
    使用iverilog编译并运行测试

    Args:
        verilog_file: 生成的Verilog文件路径
        testbench_file: testbench文件路径
        timeout: 仿真超时时间(秒)

    Returns:
        (success, output): success为True表示测试通过,output为测试输出
    """
    print(f"[VERIFY] 使用iverilog验证代码...")

    # 临时输出文件
    output_file = "test_output.vvp"

    try:
        # 步骤1: 编译
        print(f"[VERIFY] 编译 {verilog_file} 和 {testbench_file}...")
        compile_result = subprocess.run(
            ["iverilog", "-o", output_file, verilog_file, testbench_file],
            capture_output=True,
            text=True,
            timeout=10
        )

        if compile_result.returncode != 0:
            print(f"[FAIL] 编译失败:")
            print(compile_result.stderr)
            return False, compile_result.stderr

        print(f"[VERIFY] 编译成功")

        # 步骤2: 运行仿真
        print(f"[VERIFY] 运行仿真...")
        sim_result = subprocess.run(
            ["vvp", output_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = sim_result.stdout
        print(f"[VERIFY] 仿真输出:")
        print(output)

        # 检查是否通过测试
        if "Your Design passed" in output:
            print(f"[PASS] ✓ 测试通过!")
            return True, output
        else:
            print(f"[FAIL] ✗ 测试失败")
            return False, output

    except subprocess.TimeoutExpired:
        print(f"[FAIL] 仿真超时")
        return False, "Timeout"

    except FileNotFoundError as e:
        print(f"[ERROR] 找不到iverilog/vvp工具: {e}")
        print(f"       请确保已安装Icarus Verilog: https://bleyer.org/icarus/")
        return False, str(e)

    except Exception as e:
        print(f"[ERROR] 验证过程出错: {e}")
        return False, str(e)

    finally:
        # 清理临时文件
        if os.path.exists(output_file):
            os.remove(output_file)


def main():
    """主函数"""
    # 配置参数
    model_name = "gpt-4o-mini"
    module_name = "adder_8bit"

    # 文件路径
    description_file = f"../benchmark/arithmetic/{module_name}/simple_design_description.txt"
    testbench_file = f"../benchmark/arithmetic/{module_name}/testbench.v"
    output_dir = f"./test_output/{model_name}"
    output_verilog = f"{output_dir}/{module_name}.v"
    output_response = f"{output_dir}/{module_name}_response.txt"

    print("=" * 60)
    print(f"ChipGPTV - 简单测试脚本")
    print(f"模型: {model_name}")
    print(f"模块: {module_name}")
    print("=" * 60)
    print()

    # 读取设计描述
    if not os.path.exists(description_file):
        print(f"[ERROR] 找不到设计描述文件: {description_file}")
        return

    with open(description_file, 'r', encoding='utf-8') as f:
        design_description = f.read()

    print(f"[INFO] 设计描述:")
    print(design_description)
    print()

    # 调用LLM生成代码
    verilog_code, full_response = llm_generate_verilog(
        model_name, design_description, module_name
    )

    if verilog_code is None:
        print(f"[ERROR] 代码生成失败")
        return

    # 保存生成的代码
    os.makedirs(output_dir, exist_ok=True)

    with open(output_verilog, 'w', encoding='utf-8') as f:
        f.write(verilog_code)
    print(f"[SAVE] Verilog代码已保存到: {output_verilog}")

    with open(output_response, 'w', encoding='utf-8') as f:
        f.write(f"Model: {model_name}\n")
        f.write(f"Module: {module_name}\n")
        f.write(f"\n{'='*60}\n")
        f.write(f"Full Response:\n")
        f.write(f"{'='*60}\n\n")
        f.write(full_response)
    print(f"[SAVE] 完整响应已保存到: {output_response}")
    print()

    # 使用iverilog验证
    if not os.path.exists(testbench_file):
        print(f"[ERROR] 找不到testbench文件: {testbench_file}")
        return

    success, output = verify_with_iverilog(output_verilog, testbench_file)

    print()
    print("=" * 60)
    if success:
        print(f"✓ 测试成功! {module_name}模块功能正确")
    else:
        print(f"✗ 测试失败! 请检查生成的代码")
    print("=" * 60)


if __name__ == "__main__":
    main()
