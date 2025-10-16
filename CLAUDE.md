# ChipGPTV - Codebase Architecture and Commands

## Project Overview

**ChipGPTV** is a multi-modal LLM-based Verilog hardware code generation framework that evaluates and benchmarks the capabilities of large language models (like GPT-4, GPT-4V, and fine-tuned models like Llama3.1, RTLcoder) in generating hardware description language (Verilog) code from natural language descriptions and circuit diagrams.

The project has two main research focuses:
1. **Benchmarking multi-modal generative AI** for Verilog generation from diagrams and descriptions
2. **Multi-modal data synthesis and projection** for LLM-based hardware code generation

## Quick Start

### Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install external tools for testing
# Download and install iverilog from https://bleyer.org/icarus/
# (required for Verilog code verification)

# Optional: For Verilog parsing features
# Install yosys - used by verilog_parse module
```

### Essential Commands

#### 1. Code Generation (Primary Interface)
```bash
# Run main benchmark with different configurations
python benchmark_exp/main.py \
  --model_name=<model> \
  --prompt_type=<type> \
  --method=<method>

# Arguments:
#   --model_name: gpt-4.1 | gpt-4 (chat models)
#   --prompt_type: simple | medium | complex (design description complexity)
#   --method: default | complete | predict
#     - default: Generate complete Verilog code from scratch
#     - complete: Complete Verilog code with code snippet context
#     - predict: Predict next token in Verilog code
```

#### 2. Verification & Testing
```bash
# Check function correctness of generated code
python benchmark_exp/function_correctness.py

# Check next token prediction correctness
python benchmark_exp/next_token_correctness.py

# Detailed Verilog code validation
python verilog_check/code_check.py \
  --generated_code_dir <path_to_generated_code> \
  --test_mode design  # or 'testbench'
```

#### 3. Chip Drawing Tool
```bash
python chip_draw_tool/chip_graph.py
```

#### 4. Verilog Parsing & Multi-Modal Data Generation
```bash
# Generate multi-modal intermediate representation from existing Verilog
python verilog_parse/mmdata_generation.py \
  --input <instruction-verilog-pair-data> \
  --output <multi-modal-IR-output>
```

#### 5. Test Benchmark (Advanced Models)
```bash
# Benchmark with fine-tuned Llama3.1
python test_benchmark/llama_finetune_benchmark.py \
  --model_name <model_name> \
  --peft_model <peft_model_path> \
  --output_dir <output_directory> \
  --use_projector

# Benchmark with DPO-optimized model
python test_benchmark/dpo_benchmark.py \
  --model_name <model_name> \
  --output_dir <output_directory> \
  --use_projector

# Benchmark with RTLcoder
python test_benchmark/rtlcoder_benchmark.py \
  --model_path <model_path> \
  --output_dir <output_directory> \
  --use_projector

# Benchmark with fine-tuned RTLcoder
python test_benchmark/rtlcoder_finetune_benchmark.py \
  --model <model> \
  --output_dir <output_directory> \
  --use_projector

# Benchmark with GPT-4 (from test_benchmark)
python test_benchmark/gpt4_benchmark.py \
  --api_key <api_key> \
  --output_dir <output_directory> \
  --use_projector
```

## Project Structure & Components

### Core Directories

#### `/benchmark` - Benchmark Dataset (5 design categories)
```
benchmark/
├── arithmetic/          # Arithmetic circuits (adders, multipliers, accumulators)
├── digital_circuit/     # Digital components (ALU, shifters, counters, mux)
├── fsm/                 # Finite state machines
├── multimodule/         # Multi-module designs
└── testbench/           # Testbench generation benchmarks
```

Each design includes:
- `reference.v` - Gold standard Verilog code
- `testbench.v` - Test harness for verification
- `[design_name].png` - Circuit diagram
- `design_description.txt`, `medium_design_description.txt`, `simple_design_description.txt` - Multi-modal descriptions
- `gpt4_design_description.txt`, etc. - Text-only versions for language-only models
- `code_completion_[1-3].txt` - Code completion prompts
- `gptv_next_token_[1-3].txt`, `gpt4_next_token_[1-3].txt` - Token prediction prompts

#### `/benchmark_exp` - Quick Benchmarking & Experiments
```
benchmark_exp/
├── main.py                          # Main entry point for benchmarking
├── llm_generate_code.py             # Full Verilog generation from descriptions
├── llm_complete_code.py             # Code completion from code snippets
├── llm_predict_token.py             # Next token prediction
├── function_correctness.py          # Test-based correctness verification
├── next_token_correctness.py        # Token prediction evaluation
├── generate_design_description.py   # Prompt generation utilities
├── generate_code_completion.py      # Code completion prompt generation
├── generate_next_token_prediction.py # Token prediction prompt generation
└── vlmql.py                         # VLMQL integration (experimental)
```

**Key Modules:**

1. **llm_generate_code.py** (131 lines)
   - Handles LLM API calls to GPT-4 and GPT-4V
   - Loads design descriptions (simple/medium/complex)
   - Manages API key rotation for rate limiting
   - Extracts Verilog code from LLM responses (```verilog...``` blocks)
   - Saves both full LLM response and extracted Verilog code

2. **llm_complete_code.py** (90 lines)
   - Code completion task using LLM
   - Takes partial code snippets and completes them
   - Similar API handling and Verilog extraction

3. **llm_predict_token.py** (90 lines)
   - Next token prediction from partial code
   - Used to evaluate LLM's understanding of code continuity
   - Similar structure to code completion module

4. **main.py** (98 lines)
   - Orchestrates benchmark runs
   - Configurable model, prompt type, and method selection
   - Creates output directory structure
   - Iterates through design instances and runs specified method

#### `/test_benchmark` - Advanced Model Benchmarking
```
test_benchmark/
├── llama_finetune_benchmark.py      # Evaluate fine-tuned Llama3.1
├── dpo_benchmark.py                 # Evaluate DPO-optimized models
├── rtlcoder_benchmark.py            # Evaluate base RTLcoder
├── rtlcoder_finetune_benchmark.py   # Evaluate fine-tuned RTLcoder
└── gpt4_benchmark.py                # Evaluate GPT-4 (alternative implementation)
```

These modules support:
- Model inference on benchmark datasets
- Optional projector descriptions (CV-extracted circuit information)
- Testbench generation
- Time-series data projection for testbenches

#### `/verilog_check` - Code Validation & Results Processing
```
verilog_check/
├── code_check.py       # Main validation script using iverilog
└── result_process.py   # Post-processing of test results
```

Validates generated Verilog using:
- `iverilog` for compilation/syntax checking
- `vvp` (Icarus Verilog) testbench simulation
- Pass/fail detection from simulation output

#### `/verilog_parse` - Multi-Modal Data Synthesis
```
verilog_parse/
├── mmdata_generation.py  # Generate multi-modal IR from Verilog datasets
├── verilog_parser.py     # Parse Verilog and extract structure
├── yosys_script.py       # Integration with Yosys for synthesis
└── dot2png.py            # Convert graphviz DOT to PNG
```

Generates multi-modal representations by:
- Parsing existing Verilog datasets (RTLcoder, etc.)
- Extracting circuit structure and dependencies
- Creating intermediate representations (IR) with text + diagram

#### `/chip_draw_tool` - Interactive Chip Diagram Designer
```
chip_draw_tool/
└── chip_graph.py  # Interactive menu-driven tool for designing chip diagrams
```

Allows manual chip diagram creation by defining:
1. Submodules
2. Connections between submodules
3. Port signal mappings
Auto-generates diagram visualizations

#### `/generated_code` - Output Directory for Generated Code
Organized by model and configuration:
```
generated_code/
├── gpt-4-vision-preview-complex/
├── gpt-4-complex/
├── gpt-4.1-complex/
├── gpt-4.1-complete-code/
├── gpt-4.1-predict/
└── [other model configurations]
```

Each contains:
- Generated `.v` files (Verilog code)
- `.txt` files (full LLM responses)
- Organized by design type (arithmetic/digital_circuit/advanced/etc.)

#### `/img` - Images & Diagrams
Contains circuit diagrams and visual assets used in prompts

### Data Flow & Interaction

```
┌─────────────────────────────────────────────────────────┐
│                    benchmark_exp/main.py                 │
│         (Orchestrator - coordinates all tasks)           │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   llm_generate_code  llm_complete  llm_predict_token
   (Full generation)  _code         (Token prediction)
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
         /generated_code (output files)
         (.v files + .txt responses)
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
 function_correctness.py      verilog_check/code_check.py
 (Test-based validation)      (Compilation + simulation)
        │                             │
        └──────────────┬──────────────┘
                       ▼
          Results & Performance Metrics
```

### Advanced Features (Framework Design)

The README indicates support for:

1. **Fine-tuning**: `finetune/` directory (not present in current state)
   - Llama3.1 fine-tuning with `llama-recipes`
   - RTLcoder fine-tuning

2. **Direct Preference Optimization (DPO)**: `dpo/` directory (referenced in README)
   - Further training optimization for preference alignment

3. **Projector**: `projector/` directory (referenced in README)
   - CV-based circuit diagram understanding
   - OCR, edge detection, node detection
   - Transforms diagrams/tables/waves to text

## Configuration & Dependencies

### requirements.txt
```
openai           # OpenAI API client
tqdm            # Progress bars
pandas          # Data manipulation
graphviz        # Diagram generation
```

### Key Configuration Files
- `.gitignore` - Excludes generated code and temporary files
  - `src/__pycache__`, `generated_code/*`, `temp.py`

### API Configuration
- OpenAI API keys managed in module files:
  - `benchmark_exp/llm_generate_code.py`
  - `benchmark_exp/llm_complete_code.py`
  - `benchmark_exp/llm_predict_token.py`
- Supports key rotation for rate limit management

### External Tools Required
- **iverilog** & **vvp**: Verilog compilation and simulation
- **yosys**: Verilog synthesis (for verilog_parse)

## Code Quality & Development

### Python Files Statistics
- benchmark_exp modules: ~994 LOC total
- Modular design with clear separation of concerns
- Each module handles one aspect:
  - Prompt generation
  - LLM API interaction
  - Code extraction
  - Validation/testing
  - Result processing

### Error Handling
- API key rotation on failure
- Exception handling for subprocess calls
- Timeout protection on API calls (20s)
- File I/O error handling

### Testing Approach
- **Unit level**: Verilog compilation/simulation with testbenches
- **Integration**: Full pipeline from design description to validation
- **Correctness criteria**:
  - Syntax correctness (iverilog compilation)
  - Functional correctness (testbench pass/fail)

## Data Organization Principles

1. **By Design Complexity**: simple → medium → complex descriptions
2. **By Model Type**: Separate prompts for multi-modal (GPT-4V) vs text-only (GPT-4)
3. **By Task**: generation vs completion vs prediction
4. **By Configuration**: Organized output directories for reproducibility

## Performance Considerations

- **Benchmarking multiple designs**: Iterates through instance_list with configurable repetitions
  - Default: 5 iterations for generation, 3 for completion/prediction
- **API rate limiting**: Implements key rotation strategy
- **Timeout protection**: 20 second timeout on API calls, 2 second timeout on simulations
- **Subprocess management**: `start_new_session=True` for process isolation

## Extension Points

The codebase is designed for:
1. **New LLM models**: Add configuration to existing modules
2. **New design categories**: Add to benchmark directory structure
3. **Custom evaluation metrics**: Extend verilog_check module
4. **New prompt types**: Generate via corresponding utility scripts
5. **Advanced techniques**: Integration with fine-tuning and DPO modules

## Development Workflow

1. **Prepare benchmarks**: Create designs in `/benchmark` with descriptions and testbenches
2. **Generate prompts**: Use `generate_*.py` utilities to create prompts
3. **Run experiments**: Execute via `benchmark_exp/main.py` with desired configuration
4. **Evaluate results**: Use correctness checking and verilog_check modules
5. **Analyze**: Process results with result_process.py utilities
6. **Iterate**: Fine-tune models or optimize prompts based on findings

