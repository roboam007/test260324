---
name: test-case-generator
description: Generate structured test points from requirement documents with appropriate hierarchical levels. Use when users need to create test points (测试点) from functional requirement documents (PRD, functional specifications, requirement lists), or when users ask for "测试点", "测试用例", "用例生成", converting test cases to "xmind" / "脑图", or uploading to Tyr / case.atomecorp.net. Supports direct PRD input - automatically performs requirement analysis before generating test cases. Generates markdown test points, converts the same markdown to XMind without changing the markdown, then uploads the XMind to Tyr. Key features include requirement pre-analysis, test point validation, hierarchy optimization, boundary value testing, markdown-to-xmind conversion, and Tyr upload.
---

# Test Case Generator

Generate well-structured **test points** from requirement documents. Test points focus on "what to verify", not detailed execution steps.

Accepts PRD/requirement documents directly — performs requirement pre-analysis internally before generating test cases. Final output is markdown test cases, an XMind file converted from that markdown (markdown format is not changed), and an upload to the Tyr platform.

## Core Principles

### 1. Test Points vs Feature Descriptions - Critical

**⚠️ IMPORTANT**: Every test point must be a **verification point**, NOT a feature description.

**Test Point** = Describes what to **verify/validate**
**Feature Description** = Describes what the system **does** (NOT a test point)

#### How to Identify

| Type | Pattern | Example |
|------|---------|---------|
| ❌ Feature Description | "系统做X" / "支持Y" | "注册场景需要通过EMAIL_OTP验证" |
| ✅ Test Point | "验证X时Y" / "X时应Y" | "注册场景触发身份验证时，系统发起EMAIL_OTP验证" |

#### Transformation Rules

When requirement says "场景A使用验证方式B":

❌ **Wrong** (Feature Description):
```markdown
#### 注册场景
- 用户进行注册操作
- 需要通过AIX侧EMAIL_OTP验证
```

✅ **Correct** (Test Point):
```markdown
#### 注册场景 - 触发EMAIL_OTP验证
- 用户在注册流程触发身份验证
- 系统发起EMAIL_OTP验证（非OTP/Login_PASSCODE）

#### 注册场景 - 不提供其他验证方式
- 用户在注册流程的身份验证页面
- 仅显示EMAIL_OTP选项，无其他验证方式可选
```

When requirement says "优先级规则A > B > C":

❌ **Wrong** (Rule Description):
```markdown
#### 优先级1 - Biometric可用
- 用户设备支持Biometric，前端未清除本地生物识别凭证
- 系统优先使用Biometric验证
```

✅ **Correct** (Test Point):
```markdown
#### 优先级1 - Biometric可用时优先触发
- 多种验证方式均可用（Biometric/Passcode/OTP）
- 系统优先触发Biometric验证，不显示其他选项

#### 优先级自动降级 - Biometric不可用时跳过
- Biometric不可用（凭证已清除），其他方式可用
- 系统自动跳过Biometric，触发Login Passcode验证
```

#### Self-Check Questions

Before writing each test point, ask:
1. **"这是在描述系统做什么，还是在验证系统行为？"**
2. **"执行这个测试点后，能得出 PASS/FAIL 结论吗？"**
3. **"这个测试点有明确的预期结果吗？"**

If any answer is "No", rewrite as a verification point.

### 2. Appropriate Hierarchy - No Redundancy

Choose hierarchy depth based on feature complexity:
- **2 levels**: Simple features (< 10 test cases, no scenario grouping needed)
- **3 levels**: Standard features (clear scenarios, most common)
- **4 levels**: Complex features (multiple sub-modules, multi-step workflows)

**Golden Rule**: Use the simplest structure that clearly organizes test cases.

For detailed patterns and decision tree, see **[references/hierarchy_patterns.md](references/hierarchy_patterns.md)**.

### 3. Simplified Checkpoint Format

Each test checkpoint uses a simplified, natural format:

```markdown
#### Checkpoint Name
- [Validation point combining context, action, and expected result]
```

**For complex tests** - Use multiple bullet points:
```markdown
#### Checkpoint Name
- [Step 1 with context]
- [Step 2 and what happens]
- [Step 3 and expected result]
```

**Do NOT use explicit labels** like "Precondition:", "Action:", "Expected:". Just describe what to verify naturally.

For detailed format guidelines, see **[references/checkpoint_format.md](references/checkpoint_format.md)**.

### 4. Strictly Follow Requirements

- Only generate test cases for features explicitly mentioned in requirements
- Do NOT add test cases for features not in the document
- Do NOT assume additional functionality
- When requirements are unclear, note it in the output

### 5. Comprehensive Coverage

Cover all aspects mentioned in requirements:
- Positive scenarios (happy path)
- Negative scenarios (error handling, validation failures)
- Boundary conditions (limits, edge cases)
- State transitions (if applicable)
- Different user roles/permissions (if applicable)

## Workflow

### Step 0: Requirement Pre-Analysis (from PRD)

**When input is a raw PRD/requirement document** (not a pre-analyzed func_list), perform this pre-analysis first. If input is already a structured func_list.md, skip to Step 1.

#### 0.1 Understand Document Structure

Read the requirement document and identify:
1. **Main functional modules**: High-level features or business processes
2. **Sub-features**: Components within each module
3. **Specific function points**: Detailed behaviors, validations, operations
4. **Scenarios and conditions**: Different states, inputs, user actions
5. **Expected behaviors**: What should happen in each scenario

**CRITICAL: Preserve the original document's heading hierarchy.** The output structure must match the original document's headings to maintain traceability. For detailed guidance, see **[references/structure_preservation.md](references/structure_preservation.md)**.

#### 0.2 Identify Core Flows

Before diving into detailed test points, identify core business flows:

- **What are core flows?** End-to-end paths representing key business objectives or user journeys
- **Separate by business objective**: Each distinct goal = separate flow (e.g., "Complete KYC" vs "Join Waitlist")
- **Detail level**: Medium (10-15 steps) — not too abstract, not button-level granularity
- **Format**: Tree-indented Markdown lists showing hierarchy and branches

**Flow separation criteria** — separate into different flows when:
- Different business objectives
- Different user intents or entry points
- Different end states
- Mutually exclusive paths

**Keep in same flow** when: minor variations, error handling within a step, optional steps.

For comprehensive guidance with examples and anti-patterns, see **[references/core_flows.md](references/core_flows.md)**.

#### 0.3 Extract Functional Points with Conditions + Expected Results

For each function point, document scenarios using:
```markdown
- [Condition/Input/State description]
  - 预期：[Expected behavior/result]
```

Key principles:
- Be specific with concrete values
- Cover normal, error, and edge cases
- Extract all numeric thresholds explicitly (大于/小于/最大/最小/范围/N次)
- Mark ambiguous requirements with "（待澄清）" or "（需确认）"

For common requirement patterns (validation, state-based, configuration-based, boundary, multi-step, permission, error handling), see **[references/requirement_patterns.md](references/requirement_patterns.md)**.

#### 0.4 Pre-Analysis Self-Check

Before proceeding to test case generation:
- All PRD sections covered? Add any missing modules/function points
- Every function point has clear "预期" result? Add or clarify
- All thresholds explicitly documented? Extract from PRD text
- Core flows complete and properly separated? Adjust detail level
- Original document structure preserved? Correct any deviations

---

### Step 1: Analyze Requirements

Read the requirement document (or pre-analysis output from Step 0) and identify:
1. **Core flows**: Does the document have a "核心流程" (Core Flows) section?
2. **Feature complexity**: Simple, standard, or complex?
3. **Main functional modules**: What are the major features?
4. **Test scenarios**: Can tests be grouped into scenarios?

### Step 2: Generate Core Flow Test Cases (if exists)

**⚠️ IMPORTANT**: If the requirement document contains a "核心流程" section, generate core flow test cases FIRST.

**Key Rule: One flow = One test case, preserve original structure**

Core flow test cases should:
- **Keep the exact same tree-indented structure** as the original flow in func_list.md
- **Each flow becomes ONE test case** (not multiple separate scenarios)
- Use `### 流程N: [Flow Name]` as the test case title

For detailed guidance, see **[references/core_flow_testing.md](references/core_flow_testing.md)**.

### Step 3: Determine Hierarchy

Based on analysis, choose structure:

| Feature Type | Structure | Heading Levels |
|-------------|-----------|----------------|
| Simple (< 10 tests) | Feature → Checkpoint | H2 → H3 |
| Standard (clear scenarios) | Feature → Scenario → Checkpoint | H2 → H3 → H4 |
| Complex (sub-modules) | Feature → Sub-Module → Scenario → Checkpoint | H2 → H3 → H4 → H5 |

### Step 4: Generate Detailed Test Cases

For each feature/scenario, create test checkpoints:
1. **Identify test conditions**: What needs to be tested?
2. **Write checkpoint name**: Clear, concise description
3. **Write validation points**: Natural language describing what to verify
4. **Cover boundary values**: Test all thresholds and limits (see below)

### Step 5: Format Output

```markdown
# [Feature Name] Test Cases

## Document Information
- Based on requirement: [Source document reference]
- Generated time: [Document generation time, e.g., 2026-06-24 16:30]
- Test scope: [Brief description]
- Structure: [Hierarchy description]

---

## 核心流程测试 (if core flows exist)

### 流程1: [Flow Name]
[Copy the exact tree-indented structure from func_list.md]

---

## 详细功能点测试

[Detailed functional test cases organized by chosen hierarchy]
```

### Step 6: Self-Check and Fix (自检并修复)

**⚠️ IMPORTANT**: After generating test cases, perform self-check and **fix issues directly** (do not just report).

#### Check 1: Test Point Format Validation

Scan all test points for **feature description patterns**:

| Pattern | Example | Fix Action |
|---------|---------|------------|
| "需要通过X验证" | "注册场景需要EMAIL_OTP验证" | → 改为 "注册场景触发身份验证时，系统发起EMAIL_OTP" |
| "支持X类型" | "支持8-32位字符" | → 改为 "输入8位字符，验证通过" + "输入32位字符，验证通过" |
| "系统优先使用X" | "系统优先使用Biometric" | → 改为 "多方式可用时，系统优先触发Biometric验证" |
| "X场景使用Y方式" | "登录场景使用OTP" | → 改为 "登录场景触发验证时，系统发起OTP验证" |

**Fix**: Rewrite each identified issue as a proper verification point with trigger + expected result.

#### Check 2: Boundary Value Coverage

1. Scan func_list for threshold keywords: 大于/小于/最大/最小/范围/N次/N分钟
2. For each threshold, verify test_cases has:
   - Threshold - 1 test point
   - Threshold (boundary) test point
   - Threshold + 1 test point

**Fix**: Add missing boundary test points directly.

#### Check 3: Coverage Completeness

1. List all functional points from func_list (H3/H4/H5 headings)
2. Check each has corresponding test point(s) in test_cases

**Fix**: Add test points for uncovered functional points.

#### Check 4: Core Flow Structure

1. Compare core flow structure in test_cases with func_list
2. Verify exact match (same indentation, same content)

**Fix**: Correct any structural differences.

#### Self-Check Execution

```
For each test point in generated output:
  IF matches feature description pattern:
    Rewrite as verification point (trigger + expected result)
  
For each threshold in func_list:
  IF missing boundary test points:
    Add boundary-1, boundary, boundary+1 test points

For each functional point in func_list:
  IF no corresponding test point:
    Add test point(s)

For core flow section:
  IF structure differs from func_list:
    Correct to match exactly
```

### Step 7: Convert Markdown to XMind

**⚠️ IMPORTANT**: After the markdown test cases are finalized, convert them to XMind. Do **not** change the markdown format to fit XMind. Markdown is the source of truth; XMind is a derived export.

If the user only asks to convert an existing markdown test-case file, skip Steps 0–6 and run this step only.

1. Write/confirm the markdown file path (same file produced in Step 5).
2. Run the bundled converter (resolve `scripts/` relative to this skill directory):

```bash
python3 scripts/create_xmind_from_markdown.py "<path-to-test-cases.md>"
```

3. The script writes `<same-name>.xmind` next to the markdown file. Tell the user both output paths.

**Rules:**
- Do not rewrite headings, bullets, or hierarchy to make conversion easier
- Do not hand-build `.xmind` or substitute another converter
- Do not add image/attachment handling
- If conversion fails, keep the markdown and report the error

### Step 8: Upload XMind to Tyr

**⚠️ IMPORTANT**: After XMind is generated, upload it with the bundled script. Do not hand-write curl. Do not persist tokens.

If the user only asks to upload an existing `.xmind`, skip Steps 0–7 and run this step only.

**Title**: `AIX` + space + PRD document name, with `[PRD]` prefix and date/time (e.g. `[2026-07-14]`) removed.  
Examples: `[PRD]Atome Oboss User Label` → `AIX Atome Oboss User Label`; `[2026-07-14] aixpay+oboss+user tag` → `AIX aixpay+oboss+user tag`.  
The script builds this from `--prd-name`.

**PRD URL**: Take it from the current conversation (the requirement doc link the user attached). If missing, ask once.

**Auth (never persist):**
Tyr needs `authorization = Test-Token`. Sending `Cookie: Test-Token=...; ADVSSO=...` as well is more compatible with Tyr APIs.

Resolve credentials in this order; do **not** write them to files, git, markdown, xmind, or skill config:
1. Env `TYR_TOKEN` / `TYR_ADVSSO` already provided **in this conversation**
2. Otherwise run the script and let it read live Chrome cookies for `case.atomecorp.net` via `browser_cookie3` (preferred on Cursor; no OpenClaw required)
3. If the script returns `AUTH_REQUIRED`, tell the user: 打开 https://case.atomecorp.net，按 F12 → Application → Cookies，复制 Test-Token 和 ADVSSO. Wait, then retry with `TYR_TOKEN` / `TYR_ADVSSO` for this command only

Do not prefer Network `authorization` copy as the first method. Do not use OpenClaw browser unless Chrome cookie extraction is unavailable and OpenClaw browser actually works. Cursor IDE browser cannot read these cookies (CDP cookie APIs are denied, and it does not share the user's Chrome login).

**Command** (resolve `scripts/` relative to this skill directory):

```bash
python3 scripts/upload_to_tyr.py --probe
python3 scripts/upload_to_tyr.py \
  --file "<path-to-test-cases.xmind>" \
  --prd-name "<PRD document name>" \
  --prd-url "<PRD URL from conversation>"
```

Fixed Tyr fields in the script: `projectId=40`, `folderId=-1`, `mindVersion=0`, `mindId` empty (create new).

**Success**: stdout `{"ok": true, "mindId": ..., "viewUrl": "https://case.atomecorp.net/brainmap/40"}`  
Tell the user the title, mindId, authSource, and view link. Do not print tokens.

**Failure**: keep local `.md` / `.xmind`. For `AUTH_REQUIRED`, ask for cookies and retry; otherwise report `message` and stop.

## Boundary Value Testing - Critical

**⚠️ IMPORTANT**: When requirements mention comparison conditions (>, <, ≥, ≤, =), you MUST test ALL boundary values.

### Quick Reference

| Requirement Pattern | Required Test Cases |
|---------------------|---------------------|
| X > N | X = N+1, X = N, X = N-1 |
| X < N | X = N-1, X = N, X = N+1 |
| min ≤ X ≤ max | min-1, min, min+1, max-1, max, max+1 |
| After N times | N-1, N, N+1 times |
| Time > 1 hour | > 1h, = 1h, < 1h, = 1min, < 1min |

### Boundary Keywords Checklist

When you see these patterns, always add boundary tests:
- ✅ "大于/小于" → Test >, =, <
- ✅ "最大/最小" → Test max-1, max, max+1 / min-1, min, min+1
- ✅ "范围X-Y" → Test X-1, X, X+1, Y-1, Y, Y+1
- ✅ "次数限制" → Test limit-1, limit, limit+1
- ✅ "时间阈值" → Test before, at, after threshold

For comprehensive boundary testing guidance, see **[references/boundary_value_testing.md](references/boundary_value_testing.md)**.

## Checkpoint Writing Guidelines

### Be Specific and Measurable

❌ **Vague**: "Enter invalid data"
✅ **Specific**: "输入无效手机号'01234567890',提示'Invalid mobile number'"

### Use Concrete Values

❌ **Abstract**: "Enter a long nickname"
✅ **Concrete**: "尝试输入11个字符'12345678901',前端在第10个字符后阻止继续输入"

### Include Key Details

- Use specific data values (phone numbers, text, etc.)
- Mention UI elements when relevant (buttons, messages, fields)
- Describe expected behavior clearly
- Keep it concise - combine related information in one bullet point

## Reference Files

Load reference files when needed:

| File | When to Load |
|------|--------------|
| **[test_point_validation.md](references/test_point_validation.md)** | ⭐ **Critical** - When converting requirements to test points, especially for "场景验证方式" or "优先级规则" |
| **[core_flow_testing.md](references/core_flow_testing.md)** | Requirement has "核心流程" section |
| **[hierarchy_patterns.md](references/hierarchy_patterns.md)** | Need guidance on hierarchy selection |
| **[checkpoint_format.md](references/checkpoint_format.md)** | Unsure about checkpoint format for complex scenarios |
| **[boundary_value_testing.md](references/boundary_value_testing.md)** | See comparison operators (>, <, ≥, ≤) or thresholds |
| **[examples.md](references/examples.md)** | Want complete examples of different feature types |
| **[core_flows.md](references/core_flows.md)** | Step 0 - Need guidance on identifying and separating core flows from PRD |
| **[requirement_patterns.md](references/requirement_patterns.md)** | Step 0 - Need common patterns for extracting functional scenarios from PRD |
| **[structure_preservation.md](references/structure_preservation.md)** | Step 0 - Need guidance on preserving original PRD document structure |
| **[create_xmind_from_markdown.py](scripts/create_xmind_from_markdown.py)** | Step 7 - After markdown is finalized, convert to XMind without changing the markdown |
| **[upload_to_tyr.py](scripts/upload_to_tyr.py)** | Step 8 - Upload generated XMind to Tyr; auth from Chrome cookies or env |

## Best Practices

### Do's
✓ Analyze requirements thoroughly before generating
✓ **Transform feature descriptions into verification points**
✓ Choose appropriate hierarchy based on complexity
✓ Use specific, measurable validation criteria
✓ Include both positive and negative test cases
✓ Test all boundary values for thresholds
✓ Write in natural, flowing language
✓ After markdown is finalized, convert it to XMind with the bundled script
✓ After XMind is generated, upload it to Tyr with the bundled script; never persist tokens

### Don'ts
✗ **Don't copy requirement text as test points** (transform to verification)
✗ **Don't write "系统支持X" style descriptions** (write "验证X时Y")
✗ Don't use excessive nesting (> 4 levels)
✗ Don't create redundant hierarchy levels
✗ Don't use vague or ambiguous language
✗ Don't add test cases for features not in requirements
✗ Don't use explicit labels like "Precondition:", "Action:", "Expected:"
✗ Don't change markdown format for XMind export; don't hand-build `.xmind`
✗ Don't persist Tyr tokens; don't hand-write the Tyr curl if the bundled script can run

## Quality Checklist

Before finalizing, verify:
- [ ] **Core flow test cases generated** (if requirement has 核心流程 section)
- [ ] **Core flow structure preserved** (same as func_list.md, one flow = one test case)
- [ ] **All test points are verification points** (not feature descriptions)
- [ ] All requirements covered
- [ ] Hierarchy is appropriate (not too flat or deep)
- [ ] Specific values used (not vague descriptions)
- [ ] Both positive and negative cases included
- [ ] **Boundary values tested** (>, <, =, min, max, thresholds)
- [ ] Document header is complete
- [ ] **XMind generated** from the finalized markdown (same name, `.xmind` next to the `.md`)
- [ ] **Uploaded to Tyr** (`code=0`); user received `https://case.atomecorp.net/brainmap/40`

### Test Point Validation Checklist

For each test point, verify:
- [ ] Has clear **trigger condition** (when/what triggers the test)
- [ ] Has clear **expected result** (what should happen)
- [ ] Can produce **PASS/FAIL** result
- [ ] Is NOT just restating the requirement

## Quick Example

```markdown
# AIX ME Module - Test Cases

## Document Information
- Based on requirement: AIX Card ME Module V1.0
- Generated time: 2026-06-24 16:30
- Test scope: User profile display and management
- Structure: Feature → Scenario → Checkpoint

---

## User Profile Display

### Nickname Display

#### User has set nickname
- 用户已设置昵称"TestUser",ME页面顶部显示"Hi TestUser"

#### User has not set nickname
- 用户未设置昵称,ME页面显示默认昵称或提示设置昵称

### Nickname Modification

#### Valid nickname - Maximum length (10 characters)
- 输入恰好10个字符"1234567890"并保存,昵称保存成功

#### Invalid nickname - Exceeds maximum length
- 尝试输入11个字符"12345678901",前端在第10个字符后阻止继续输入

#### Invalid nickname - Special characters
- 输入包含特殊字符的昵称"Test@User#"并保存,提示错误"仅支持中文、英文、数字"
```

For more complete examples, see **[references/examples.md](references/examples.md)**.
