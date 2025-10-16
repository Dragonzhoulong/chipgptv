# CLAUDE_CN.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供中文指导。

---

# ChipGPTV - 代码库架构与命令

## 项目概述

**ChipGPTV** 是一个基于多模态大语言模型的 Verilog 硬件代码生成框架，用于评估和基准测试大型语言模型（如 GPT-4、GPT-4V 以及微调模型如 Llama3.1、RTLcoder）从自然语言描述和电路图生成硬件描述语言（Verilog）代码的能力。

该项目有两个主要研究方向：
1. **多模态生成式 AI 基准测试**：从图表和描述生成 Verilog 代码
2. **多模态数据合成与投影**：用于基于 LLM 的硬件代码生成

## 快速开始

### 前置要求
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装测试所需的外部工具
# 从 https://bleyer.org/icarus/ 下载并安装 iverilog
# （用于 Verilog 代码验证，必需）

# 可选：用于 Verilog 解析功能
# 安装 yosys - verilog_parse 模块使用
```

### 核心命令

#### 1. 代码生成（主要接口）
```bash
# 使用不同配置运行主基准测试
python benchmark_exp/main.py \
  --model_name=<模型名> \
  --prompt_type=<类型> \
  --method=<方法>

# 参数说明：
#   --model_name: gpt-4.1 | gpt-4 (聊天模型)
#   --prompt_type: simple | medium | complex (设计描述的复杂度)
#   --method: default | complete | predict
#     - default: 从头生成完整的 Verilog 代码
#     - complete: 基于代码片段上下文补全 Verilog 代码
#     - predict: 预测 Verilog 代码中的下一个 token
```

#### 2. 验证与测试
```bash
# 检查生成代码的功能正确性
python benchmark_exp/function_correctness.py

# 检查下一个 token 预测的正确性
python benchmark_exp/next_token_correctness.py

# 详细的 Verilog 代码验证
python verilog_check/code_check.py \
  --generated_code_dir <生成代码路径> \
  --test_mode design  # 或 'testbench'
```

#### 3. 芯片绘图工具
```bash
python chip_draw_tool/chip_graph.py
```

#### 4. Verilog 解析与多模态数据生成
```bash
# 从现有 Verilog 生成多模态中间表示
python verilog_parse/mmdata_generation.py \
  --input <指令-verilog配对数据> \
  --output <多模态IR输出>
```

#### 5. 测试基准（高级模型）
```bash
# 使用微调后的 Llama3.1 进行基准测试
python test_benchmark/llama_finetune_benchmark.py \
  --model_name <模型名> \
  --peft_model <peft模型路径> \
  --output_dir <输出目录> \
  --use_projector

# 使用 DPO 优化模型进行基准测试
python test_benchmark/dpo_benchmark.py \
  --model_name <模型名> \
  --output_dir <输出目录> \
  --use_projector

# 使用 RTLcoder 进行基准测试
python test_benchmark/rtlcoder_benchmark.py \
  --model_path <模型路径> \
  --output_dir <输出目录> \
  --use_projector

# 使用微调后的 RTLcoder 进行基准测试
python test_benchmark/rtlcoder_finetune_benchmark.py \
  --model <模型> \
  --output_dir <输出目录> \
  --use_projector

# 使用 GPT-4 进行基准测试（来自 test_benchmark）
python test_benchmark/gpt4_benchmark.py \
  --api_key <api密钥> \
  --output_dir <输出目录> \
  --use_projector
```

## 项目结构与组件

### 核心目录

#### `/benchmark` - 基准测试数据集（5 个设计类别）
```
benchmark/
├── arithmetic/          # 算术电路（加法器、乘法器、累加器）
├── digital_circuit/     # 数字组件（ALU、移位器、计数器、多路复用器）
├── fsm/                 # 有限状态机
├── multimodule/         # 多模块设计
└── testbench/           # 测试平台生成基准
```

每个设计包含：
- `reference.v` - 黄金标准 Verilog 代码
- `testbench.v` - 验证测试平台
- `[design_name].png` - 电路图
- `design_description.txt`、`medium_design_description.txt`、`simple_design_description.txt` - 多模态描述
- `gpt4_design_description.txt` 等 - 纯文本版本（用于纯语言模型）
- `code_completion_[1-3].txt` - 代码补全提示
- `gptv_next_token_[1-3].txt`、`gpt4_next_token_[1-3].txt` - token 预测提示

#### `/benchmark_exp` - 快速基准测试与实验
```
benchmark_exp/
├── main.py                          # 基准测试主入口
├── llm_generate_code.py             # 从描述生成完整 Verilog 代码
├── llm_complete_code.py             # 从代码片段补全代码
├── llm_predict_token.py             # 下一个 token 预测
├── function_correctness.py          # 基于测试的正确性验证
├── next_token_correctness.py        # token 预测评估
├── generate_design_description.py   # 提示生成工具
├── generate_code_completion.py      # 代码补全提示生成
├── generate_next_token_prediction.py # token 预测提示生成
└── vlmql.py                         # VLMQL 集成（实验性）
```

**关键模块：**

1. **llm_generate_code.py**（131 行）
   - 处理对 GPT-4 和 GPT-4V 的 LLM API 调用
   - 加载设计描述（simple/medium/complex）
   - 管理 API 密钥轮换以应对速率限制
   - 从 LLM 响应中提取 Verilog 代码（```verilog...``` 块）
   - 保存完整的 LLM 响应和提取的 Verilog 代码

2. **llm_complete_code.py**（90 行）
   - 使用 LLM 进行代码补全任务
   - 接收部分代码片段并补全它们
   - 类似的 API 处理和 Verilog 提取

3. **llm_predict_token.py**（90 行）
   - 从部分代码预测下一个 token
   - 用于评估 LLM 对代码连续性的理解
   - 与代码补全模块结构类似

4. **main.py**（98 行）
   - 协调基准测试运行
   - 可配置的模型、提示类型和方法选择
   - 创建输出目录结构
   - 遍历设计实例并运行指定方法

#### `/test_benchmark` - 高级模型基准测试
```
test_benchmark/
├── llama_finetune_benchmark.py      # 评估微调后的 Llama3.1
├── dpo_benchmark.py                 # 评估 DPO 优化模型
├── rtlcoder_benchmark.py            # 评估基础 RTLcoder
├── rtlcoder_finetune_benchmark.py   # 评估微调后的 RTLcoder
└── gpt4_benchmark.py                # 评估 GPT-4（替代实现）
```

这些模块支持：
- 在基准数据集上进行模型推理
- 可选的投影器描述（CV 提取的电路信息）
- 测试平台生成
- 测试平台的时间序列数据投影

#### `/verilog_check` - 代码验证与结果处理
```
verilog_check/
├── code_check.py       # 使用 iverilog 的主验证脚本
└── result_process.py   # 测试结果的后处理
```

使用以下工具验证生成的 Verilog：
- `iverilog` 用于编译/语法检查
- `vvp`（Icarus Verilog）测试平台仿真
- 从仿真输出检测通过/失败

#### `/verilog_parse` - 多模态数据合成
```
verilog_parse/
├── mmdata_generation.py  # 从 Verilog 数据集生成多模态 IR
├── verilog_parser.py     # 解析 Verilog 并提取结构
├── yosys_script.py       # 与 Yosys 集成进行综合
└── dot2png.py            # 将 graphviz DOT 转换为 PNG
```

通过以下方式生成多模态表示：
- 解析现有 Verilog 数据集（RTLcoder 等）
- 提取电路结构和依赖关系
- 创建包含文本 + 图表的中间表示（IR）

#### `/chip_draw_tool` - 交互式芯片图表设计器
```
chip_draw_tool/
└── chip_graph.py  # 用于设计芯片图表的交互式菜单驱动工具
```

允许通过定义以下内容手动创建芯片图表：
1. 子模块
2. 子模块之间的连接
3. 端口信号映射
自动生成图表可视化

#### `/generated_code` - 生成代码的输出目录
按模型和配置组织：
```
generated_code/
├── gpt-4-vision-preview-complex/
├── gpt-4-complex/
├── gpt-4.1-complex/
├── gpt-4.1-complete-code/
├── gpt-4.1-predict/
└── [其他模型配置]
```

每个包含：
- 生成的 `.v` 文件（Verilog 代码）
- `.txt` 文件（完整的 LLM 响应）
- 按设计类型组织（arithmetic/digital_circuit/advanced 等）

#### `/img` - 图片与图表
包含提示中使用的电路图和视觉资源

### 数据流与交互

```
┌─────────────────────────────────────────────────────────┐
│                    benchmark_exp/main.py                 │
│              (协调器 - 协调所有任务)                      │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   llm_generate_code  llm_complete  llm_predict_token
   (完整生成)          _code         (token 预测)
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
         /generated_code (输出文件)
         (.v 文件 + .txt 响应)
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
 function_correctness.py      verilog_check/code_check.py
 (基于测试的验证)              (编译 + 仿真)
        │                             │
        └──────────────┬──────────────┘
                       ▼
          结果与性能指标
```

### 高级特性（框架设计）

README 表明支持：

1. **微调**：`finetune/` 目录（当前状态下不存在）
   - 使用 `llama-recipes` 进行 Llama3.1 微调
   - RTLcoder 微调

2. **直接偏好优化（DPO）**：`dpo/` 目录（README 中引用）
   - 用于偏好对齐的进一步训练优化

3. **投影器**：`projector/` 目录（README 中引用）
   - 基于 CV 的电路图理解
   - OCR、边缘检测、节点检测
   - 将图表/表格/波形转换为文本

## 配置与依赖

### requirements.txt
```
openai           # OpenAI API 客户端
tqdm            # 进度条
pandas          # 数据处理
graphviz        # 图表生成
```

### 关键配置文件
- `.gitignore` - 排除生成的代码和临时文件
  - `src/__pycache__`、`generated_code/*`、`temp.py`

### API 配置
- OpenAI API 密钥在模块文件中管理：
  - `benchmark_exp/llm_generate_code.py`
  - `benchmark_exp/llm_complete_code.py`
  - `benchmark_exp/llm_predict_token.py`
- 支持密钥轮换以管理速率限制

### 需要的外部工具
- **iverilog** & **vvp**：Verilog 编译和仿真
- **yosys**：Verilog 综合（用于 verilog_parse）

## 代码质量与开发

### Python 文件统计
- benchmark_exp 模块：总计约 994 行代码
- 模块化设计，关注点清晰分离
- 每个模块处理一个方面：
  - 提示生成
  - LLM API 交互
  - 代码提取
  - 验证/测试
  - 结果处理

### 错误处理
- 失败时 API 密钥轮换
- 子进程调用的异常处理
- API 调用的超时保护（20 秒）
- 文件 I/O 错误处理

### 测试方法
- **单元级别**：使用测试平台进行 Verilog 编译/仿真
- **集成**：从设计描述到验证的完整流水线
- **正确性标准**：
  - 语法正确性（iverilog 编译）
  - 功能正确性（测试平台通过/失败）

## 数据组织原则

1. **按设计复杂度**：simple → medium → complex 描述
2. **按模型类型**：多模态（GPT-4V）与纯文本（GPT-4）的独立提示
3. **按任务**：生成 vs 补全 vs 预测
4. **按配置**：组织输出目录以确保可重现性

## 性能考虑

- **多个设计的基准测试**：使用可配置的重复次数遍历 instance_list
  - 默认：生成 5 次迭代，补全/预测 3 次
- **API 速率限制**：实现密钥轮换策略
- **超时保护**：API 调用 20 秒超时，仿真 2 秒超时
- **子进程管理**：`start_new_session=True` 用于进程隔离

## 扩展点

代码库设计用于：
1. **新 LLM 模型**：向现有模块添加配置
2. **新设计类别**：添加到 benchmark 目录结构
3. **自定义评估指标**：扩展 verilog_check 模块
4. **新提示类型**：通过相应的工具脚本生成
5. **高级技术**：与微调和 DPO 模块集成

## 开发工作流

1. **准备基准**：在 `/benchmark` 中创建带有描述和测试平台的设计
2. **生成提示**：使用 `generate_*.py` 工具创建提示
3. **运行实验**：通过 `benchmark_exp/main.py` 使用所需配置执行
4. **评估结果**：使用正确性检查和 verilog_check 模块
5. **分析**：使用 result_process.py 工具处理结果
6. **迭代**：根据发现微调模型或优化提示
