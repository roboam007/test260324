# Core Flows Guide

This document provides detailed guidance on identifying and documenting core flows in requirement analysis.

---

## What are Core Flows?

**Core flows** (核心流程) are end-to-end business paths that represent the primary user journeys or critical business scenarios in a requirement document.

### Core Flows vs. Detailed Function Points

| Aspect | Core Flows | Detailed Function Points |
|--------|-----------|-------------------------|
| **Purpose** | Show end-to-end business journeys | Describe specific feature implementations |
| **Granularity** | Medium (10-15 steps) | Fine-grained (every scenario) |
| **Perspective** | User journey view | Feature implementation view |
| **Structure** | Tree-indented, showing branches | Hierarchical headings + lists |
| **Usage** | Core scenario test cases, automation reference | Detailed test points, feature acceptance |

---

## When to Identify a Core Flow

A flow should be identified as "core" if it meets these criteria:

✅ **End-to-end completeness** - Has clear start and end points representing a complete business objective

✅ **Business criticality** - Represents a primary user goal or critical business scenario

✅ **Test significance** - Requires core scenario test cases (both manual and automated)

✅ **High frequency or importance** - Either commonly used by users OR critical for business operations

### Examples of Core Flows

**E-commerce System:**
- User registration and first purchase flow
- Product search to checkout flow
- Order return and refund flow

**KYC (Identity Verification) System:**
- First-time account opening and KYC flow
- Re-authentication after failure flow
- Non-supported country user flow

**Banking Application:**
- Account opening flow
- Money transfer flow
- Loan application flow

---

## How to Identify Core Flows

### Step 1: Understand Business Objectives

Ask yourself:
- What are the main things users need to accomplish?
- What are the critical business processes?
- What flows are essential for the system to function?

### Step 2: Look for End-to-End Paths

Identify complete journeys:
- **Start point**: Where does the user begin? (e.g., "User clicks 'Open Account'")
- **Key steps**: What are the major milestones? (e.g., "Enter info → Verify identity → Upload documents")
- **End point**: What is the completion state? (e.g., "Account successfully opened")

### Step 3: Identify Critical Branches

Not every branch needs to be a separate core flow. Focus on:
- **Major decision points** that significantly change the flow
- **Critical alternative paths** (e.g., "Verification failed" path)
- **Important variations** (e.g., "First-time user" vs. "Returning user")

### Step 4: Determine Flow Count

**There is no fixed number** - it depends on the requirement document:
- Simple feature: May have 1-2 core flows
- Complex system: May have 5-10 core flows
- Multiple modules: Each module may have its own core flows

**Rule of thumb**: If you have more than 10 core flows, consider whether some can be:
- Combined (if they're variations of the same flow)
- Demoted to detailed function points (if they're not truly "core")
- Organized hierarchically (main flow + sub-flows)

---

## When to Separate Flows: Decision Criteria

**CRITICAL**: Use these criteria to determine if branches should be separate flows or included in one flow.

### Separate into Different Flows When:

✅ **Different Business Objectives**
- Each path achieves a fundamentally different goal
- Example: "Complete KYC" vs. "Join Waitlist" vs. "Query KYC Status"

✅ **Different User Intents**
- Users enter with different purposes
- Example: "First-time registration" vs. "Re-authentication after failure"

✅ **Different Entry Points or Triggers**
- Flows start from different places in the system
- Example: "User initiates KYC" vs. "System detects expired KYC and prompts renewal"

✅ **Different End States**
- Flows conclude with fundamentally different outcomes
- Example: "Account activated" vs. "Added to waitlist" vs. "Account locked"

✅ **Independent Test Scenarios**
- Each path requires completely different test data and setup
- Example: "Success path with valid documents" vs. "Failure path with invalid documents"

✅ **Mutually Exclusive Paths**
- A user can only go through one path per session
- Example: "Supported country flow" vs. "Unsupported country flow"

### Keep in Same Flow When:

❌ **Minor Variations**
- Small differences in the same overall process
- Example: "Upload via camera" vs. "Upload via gallery" (both are upload methods)

❌ **Error Handling Within a Step**
- Validation errors or retries within the same operation
- Example: "Password format error → retry" (keep in login flow)

❌ **Optional Steps**
- Steps that may or may not occur but don't change the core objective
- Example: "Skip tutorial" option in onboarding

❌ **UI Variations**
- Different ways to display the same information
- Example: "List view" vs. "Grid view"

### Decision Tree

Use this decision tree when encountering a branch:

```
Does this branch have a different business objective?
├─ YES → Separate flow
└─ NO → Does it have a different end state?
   ├─ YES → Separate flow
   └─ NO → Does it require different test setup?
      ├─ YES → Separate flow
      └─ NO → Keep in same flow as a branch
```

### Examples of Correct Separation

**Example 1: E-commerce Checkout**

✅ **Separate flows**:
- Flow 1: Normal checkout with payment
- Flow 2: Checkout with coupon/discount
- Flow 3: Checkout with saved payment method
- Flow 4: Guest checkout (no account)

**Why**: Different user intents and different entry conditions

❌ **Don't separate**:
- Credit card payment vs. PayPal payment (keep as branches in Flow 1)
- Shipping address same as billing vs. different (keep as branches in Flow 1)

**Example 2: KYC System**

✅ **Separate flows**:
- Flow 1: First-time KYC success
- Flow 2: Waitlist registration
- Flow 3: Re-authentication after failure
- Flow 4: Status query for existing application
- Flow 5: Account unlock after security lockout

**Why**: Each has different business objective and end state

❌ **Don't separate**:
- Upload passport via camera vs. gallery (keep as branches in Flow 1)
- Face recognition retry 1st time vs. 2nd time (keep as branches in Flow 1)

**Example 3: User Registration**

✅ **Separate flows**:
- Flow 1: Email registration
- Flow 2: Phone registration
- Flow 3: Social media registration (OAuth)

**Why**: Different authentication methods and different integration points

❌ **Don't separate**:
- Password strength: weak vs. strong (keep as validation in Flow 1)
- Email verification: immediate vs. delayed (keep as branches in Flow 1)

---

## Detail Level: Medium (10-15 Steps)

### Too High-Level (Avoid)

```markdown
## 核心流程

### 用户注册流程
- 用户注册
- 验证身份
- 完成注册
```

**Problem**: Too abstract, doesn't provide useful information

### Too Detailed (Avoid)

```markdown
## 核心流程

### 用户注册流程
- 用户打开APP
- 用户点击"注册"按钮
- 系统显示注册页面
- 用户点击邮箱输入框
- 用户输入邮箱地址
- 系统验证邮箱格式
- 用户点击密码输入框
- 用户输入密码
- 系统检查密码强度
- 用户点击"确认密码"输入框
- 用户再次输入密码
- 系统比对两次密码
- 用户点击"获取验证码"按钮
- 系统发送验证码到邮箱
- 用户打开邮箱
- 用户复制验证码
- 用户粘贴验证码
- 用户点击"注册"按钮
- 系统创建账户
- 系统显示成功页面
```

**Problem**: Too granular, includes every click and system response

### Just Right (Recommended)

```markdown
## 核心流程

### 流程1: 用户首次注册流程
- 用户进入注册页面
  - 输入邮箱和密码
    - 邮箱格式校验通过
      - 密码强度校验通过
        - 获取并输入邮箱验证码
          - 验证码正确
            - 注册成功，进入首页
          - 验证码错误（3次以内）
            - 提示错误，允许重新输入
          - 验证码错误（超过3次）
            - 锁定注册，提示稍后重试
      - 密码强度不足
        - 提示密码要求，停留在注册页
    - 邮箱格式错误
      - 提示邮箱格式错误，停留在注册页
    - 邮箱已被注册
      - 提示邮箱已存在，引导用户登录
```

**Good because**:
- ~10-15 key steps
- Shows important decision points
- Includes critical branches
- Maintains readability
- Provides useful information for test case design

---

## Presentation Format: Tree-Indented Structure

### Basic Structure

Use Markdown list indentation to show hierarchy:

```markdown
## 核心流程

### 流程1: [Flow Name]
- [Step 1]
  - [Condition/Decision]
    - [Branch A]
      - [Sub-step A1]
      - [Sub-step A2]
    - [Branch B]
      - [Sub-step B1]
  - [Step 2]
```

### Indentation Guidelines

**Level 1 (-)**: Main steps in the flow
```markdown
- 用户进入注册页面
- 输入注册信息
- 提交注册
```

**Level 2 (  -)**: Conditions, decisions, or sub-steps
```markdown
- 用户进入注册页面
  - 是否已有账号
  - 选择注册方式
```

**Level 3 (    -)**: Branches or detailed sub-steps
```markdown
- 用户进入注册页面
  - 是否已有账号
    - 已有账号：跳转登录页
    - 无账号：继续注册流程
```

**Level 4+ (      -)**: Further nested details (use sparingly)
```markdown
- 提交注册信息
  - 验证码校验
    - 验证码正确
      - 创建账户成功
        - 发送欢迎邮件
        - 跳转首页
    - 验证码错误
      - 提示重新输入
```

### Naming Conventions

**Flow Names**: Clear and descriptive
- ✅ Good: "用户首次开户KYC流程"
- ✅ Good: "重新认证流程"
- ❌ Bad: "流程1"
- ❌ Bad: "KYC"

**Step Descriptions**: Action-oriented
- ✅ Good: "用户输入手机号并获取验证码"
- ✅ Good: "系统校验护照信息"
- ❌ Bad: "手机号"
- ❌ Bad: "验证"

**Conditions**: Clear decision points
- ✅ Good: "是否绑定手机号"
- ✅ Good: "选择国家是否在支持列表"
- ❌ Bad: "手机号判断"
- ❌ Bad: "国家"

---

## Real-World Example: KYC Flow

### ❌ Anti-Pattern: Merged Flow (DO NOT IMITATE)

**Problem**: The following example merges multiple independent business objectives into a single flow, making it difficult to test and understand:

```markdown
## 核心流程

### 流程1: 用户首次开户KYC流程
- 用户发起KYC流程，是否绑定手机号
  - 未绑定，进入绑定流程，绑定成功后跳转身份认证
  - 已绑定，进入身份认证
    - 选择国家是否在支持列表
      - 支持，continue后跳转passport上传流程
        - 上传passport成功，跳转liveness check页面
          - 人脸采集成功
            - 人脸、ID都成功，自动跳转POA流程  ← SUCCESS PATH
              - 通过文件上传poa
                - 上传成功，跳转提交成功页面，点击back to home回到AIX首页
                  - 审核通过，AIX首页展示卡片入口
                  - 审核失败，AIX首页展示未通过激活入口
                  - 审核拒绝，AIX首页展示拒绝页面
              - 通过相册上传poa
              - 通过相机拍照上传poa
            - ID失败，人脸成功，跳转sheet detected页面  ← RETRY FLOW (should be separate)
            - ID成功，人脸失败，跳转人脸失败页面      ← RETRY FLOW (should be separate)
            - ID失败，人脸失败，跳转ID 失败页面       ← RETRY FLOW (should be separate)
            - ID审核中，人脸失败，跳转人脸 失败页面   ← RETRY FLOW (should be separate)
            - ID审核中，人脸成功，loading page轮询结果
      - 不支持，跳转到Waitlist流程  ← WAITLIST FLOW (should be separate)
        - 完成后跳转AIX首页，开户入口屏蔽
```

**Why This is Wrong**:
- ❌ Combines 3+ different business objectives (success, retry, waitlist)
- ❌ Too complex (>20 steps with deep nesting)
- ❌ Difficult to write independent test cases
- ❌ Mixes happy path with failure recovery paths
- ❌ Hard to understand the primary user journey

### ✅ Correct Pattern: Separated Flows

**Solution**: Separate different business objectives into independent core flows:

```markdown
## 核心流程

### 流程1: 首次KYC认证成功流程
- 用户发起KYC流程
  - 手机号已绑定
  - 进入KYC Start Page
    - 选择支持国家（AU/PH/VN）
    - 勾选协议
  - 进入Identity Verify Page
    - 授权相机权限
    - 上传Passport成功
  - 进入Face Guide Page
    - 未被锁定
    - 完成人脸识别成功
  - 进入Address Upload Page
    - 上传POA文件成功
  - KYC Submission Success Page
    - 提交成功，等待审核

### 流程2: Waitlist加入流程
- 用户发起KYC流程
  - 进入KYC Start Page
    - 选择不支持国家（Phase 2 - Waitlist）
    - 点击立即认证
  - 弹窗拦截提示
    - 点击"Join waitlist"
  - 进入Waitlist Page
    - 输入邮箱
    - 提交成功
  - 返回首页
    - 开户入口被屏蔽

### 流程3: 认证失败重试流程
- 用户重新进入KYC流程
  - 系统检测已完成的认证环节
    - Passport已通过（永久有效）
      - 跳过Passport认证
      - 直接进入Face Guide Page
    - Passport未通过
      - 从Identity Verify Page重新开始
  - 根据失败环节重新认证
    - 认证成功，继续后续流程
    - 认证失败，显示失败原因

### 流程4: 已有认证状态查询流程
- 用户进入KYC流程
  - KYC Loading Page检测状态
    - 状态为Under review/Rejected/Approved
  - 显示"Verification unavailable"提示
  - 点击Back按钮
    - 返回业务流程发起页

### 流程5: 人脸识别锁定流程
- 用户多次人脸识别失败
  - 24小时内失败5次
    - 系统锁定20分钟
    - 弹窗提示剩余时间
  - 24小时内失败10次
    - 系统锁定24小时
  - 等待解锁后可重新尝试
```

**Why This is Better**:
- ✅ Each flow has a clear, single business objective
- ✅ Each flow is 10-15 steps (appropriate detail level)
- ✅ Easy to write independent test cases for each flow
- ✅ Clear separation between success, alternative, and failure paths
- ✅ Each flow can be tested and automated independently

### Key Takeaways from KYC Example

**What we learned**:
1. **Separate by business objective**: Success, Waitlist, Retry, Query, and Lockout are all different objectives
2. **Each flow is independently testable**: You can test the success flow without needing to test failure scenarios
3. **Appropriate detail level**: Each flow is 8-15 steps, making them readable and actionable
4. **Clear end states**: Each flow has a distinct conclusion that aligns with its objective

---

## Common Patterns

### Pattern 1: Linear Flow with Validation

Simple sequential flow with validation at each step.

```markdown
### 流程: 用户信息填写流程
- 进入信息填写页面
  - 填写基本信息（姓名、年龄、地址）
    - 信息格式校验通过
      - 上传身份证照片
        - 照片质量检查通过
          - 提交信息
            - 后端验证通过
              - 保存成功，跳转下一步
            - 后端验证失败
              - 提示错误信息，允许修改
        - 照片质量不合格
          - 提示重新上传
    - 信息格式校验失败
      - 标红错误字段，提示修改
```

### Pattern 2: Multi-Branch Decision Flow

Flow with significant branching based on conditions.

```markdown
### 流程: 用户身份类型判断流程
- 用户进入系统
  - 检测用户身份类型
    - 新用户
      - 引导完成注册
        - 注册成功，进入新手引导
        - 注册失败，返回登录页
    - 已注册但未认证
      - 引导完成身份认证
        - 认证成功，进入主页
        - 认证失败，提示重试
    - 已认证用户
      - 检查账户状态
        - 账户正常，直接进入主页
        - 账户冻结，显示冻结原因
        - 账户注销，提示重新注册
```

### Pattern 3: Iterative Flow with Retry Logic

Flow that allows retries with limits.

```markdown
### 流程: 支付流程
- 用户发起支付
  - 选择支付方式
    - 余额支付
      - 检查余额是否充足
        - 余额充足，输入支付密码
          - 密码正确，支付成功
          - 密码错误（尝试<3次）
            - 提示密码错误，允许重试
          - 密码错误（尝试≥3次）
            - 锁定支付功能30分钟
        - 余额不足
          - 提示充值，跳转充值页面
    - 银行卡支付
      - 跳转银行支付页面
        - 支付成功，返回订单页
        - 支付失败，提示失败原因
```

### Pattern 4: Parallel Processing Flow

Flow with parallel or independent steps.

```markdown
### 流程: 订单处理流程
- 用户提交订单
  - 系统创建订单记录
    - 并行处理：
      - 库存系统：扣减库存
        - 库存充足，扣减成功
        - 库存不足，订单失败
      - 支付系统：处理支付
        - 支付成功
        - 支付失败，订单失败
      - 物流系统：生成物流单
        - 物流单生成成功
    - 所有系统处理完成
      - 全部成功，订单确认
      - 任一失败，订单回滚
```

---

## Tips for Writing Effective Core Flows

### 1. Start with the Happy Path

Begin with the main success scenario, then add important branches:

```markdown
### 流程: 用户登录流程
- 用户输入账号密码
  - 账号密码正确
    - 登录成功，进入首页  ← Start here (happy path)
  - 账号密码错误  ← Then add important branches
    - 提示错误，允许重试
  - 账号被锁定
    - 显示锁定原因和解锁方式
```

### 2. Focus on Critical Branches

Not every edge case needs to be in the core flow:

**Include**:
- ✅ Common failure scenarios (password wrong, network timeout)
- ✅ Critical business logic (approval/rejection, status changes)
- ✅ Important alternative paths (different user types, different modes)

**Exclude**:
- ❌ Rare edge cases (unless business-critical)
- ❌ UI details (button colors, animation effects)
- ❌ Technical implementation details (API endpoints, database queries)

### 3. Use Consistent Terminology

Match the terminology used in the requirement document:

```markdown
✅ Good (matches requirement doc):
- 用户完成KYC Start Page的协议勾选
- 进入Identity Verify Page
- 上传Passport照片

❌ Bad (uses different terms):
- 用户同意服务条款
- 进入身份验证界面
- 上传护照图片
```

### 4. Show State Transitions Clearly

Make it clear how the system state changes:

```markdown
✅ Good:
- 用户提交KYC申请
  - KYC状态：进行中
    - Passport认证通过
      - Passport状态：永久有效
        - Face认证通过
          - Face状态：永久有效
            - POA上传成功
              - KYC状态：人工审核中

❌ Bad:
- 用户提交KYC申请
  - 认证通过
    - 上传成功
      - 进入审核
```

### 5. Balance Breadth and Depth

Don't go too deep into one branch while ignoring others:

```markdown
✅ Balanced:
- 支付方式选择
  - 余额支付
    - 余额充足，支付成功
    - 余额不足，提示充值
  - 银行卡支付
    - 支付成功
    - 支付失败
  - 第三方支付
    - 跳转第三方页面

❌ Unbalanced:
- 支付方式选择
  - 余额支付
    - 余额充足
      - 输入密码
        - 密码正确
          - 扣款成功
            - 更新余额
              - 发送通知
                - 记录日志
                  - 返回结果
    - 余额不足，提示充值
  - 银行卡支付
  - 第三方支付
```

---

## Core Flows Placement

### In the Output Document

Core flows should **always be placed at the beginning** of the requirement analysis output:

```markdown
# [Requirement Document Title]

## 核心流程

### 流程1: [Core Flow Name]
[Flow details]

### 流程2: [Core Flow Name]
[Flow details]

---

## 详细功能点

### [Page/Module Name]
[Detailed function points]
```

**Why at the beginning?**
- ✅ Provides immediate high-level understanding
- ✅ Serves as a roadmap for the detailed function points
- ✅ Helps readers understand the overall business logic first
- ✅ Makes it easy to reference when writing test cases

---

## Relationship to Test Cases

### Core Flows → Core Scenario Test Cases

Each core flow should map to one or more core scenario test cases:

**Core Flow**:
```markdown
### 流程1: 用户首次开户KYC流程
- 用户发起KYC流程，是否绑定手机号
  - 已绑定，进入身份认证
    - 选择支持国家
      - Passport认证成功
        - Face认证成功
          - POA上传成功
            - 审核通过
```

**Corresponding Test Case**:
```
测试用例: TC_KYC_001_首次开户成功路径
前置条件: 用户已注册，已绑定手机号
测试步骤:
1. 用户进入KYC Start Page
2. 选择支持国家（AU）
3. 上传有效Passport
4. 完成Face Liveness认证
5. 上传有效POA文件
6. 等待审核通过
预期结果: KYC成功，用户可以使用钱包功能
```

### Core Flows → Automation Test Design

Core flows serve as the foundation for automation test scenarios:

```python
# Automation test based on core flow
def test_kyc_first_time_success_path():
    # Step 1: User initiates KYC (phone already bound)
    user = create_test_user(phone_bound=True)
    
    # Step 2: Select supported country
    kyc_page.select_country("AU")
    
    # Step 3: Upload passport
    kyc_page.upload_passport(valid_passport_image)
    assert kyc_page.passport_status == "SUCCESS"
    
    # Step 4: Complete face liveness
    kyc_page.complete_face_liveness(valid_face_video)
    assert kyc_page.face_status == "SUCCESS"
    
    # Step 5: Upload POA
    kyc_page.upload_poa(valid_poa_document)
    assert kyc_page.poa_status == "SUBMITTED"
    
    # Step 6: Verify final state
    assert kyc_page.kyc_status == "UNDER_REVIEW"
```

---

## Common Mistakes to Avoid

### Mistake 1: Too Many Core Flows

**Problem**: Identifying every possible path as a "core" flow

```markdown
❌ Bad (too many):
### 流程1: 用户首次注册流程
### 流程2: 用户邮箱注册流程
### 流程3: 用户手机注册流程
### 流程4: 用户第三方注册流程
### 流程5: 用户注册失败流程
### 流程6: 用户注册后首次登录流程
### 流程7: 用户注册后修改密码流程
[... 20 more flows ...]
```

**Solution**: Combine related flows or demote less critical ones

```markdown
✅ Good:
### 流程1: 用户注册流程
- 选择注册方式
  - 邮箱注册
  - 手机注册
  - 第三方注册
- 完成注册信息填写
- 验证并创建账户

### 流程2: 注册失败重试流程
[Only if this is truly a critical scenario]
```

### Mistake 2: Mixing Core Flows with Detailed Function Points

**Problem**: Including UI details and edge cases in core flows

```markdown
❌ Bad:
### 流程1: 用户登录流程
- 用户打开APP，加载启动页
- 启动页显示3秒后自动跳转
- 用户看到登录按钮（蓝色，圆角，阴影效果）
- 用户点击登录按钮
- 系统检查网络连接
  - 网络正常
    - 显示登录页面（白色背景，顶部有logo）
    - 邮箱输入框默认为空
    - 密码输入框默认为空
    - 记住密码checkbox默认不勾选
    [... too much detail ...]
```

**Solution**: Keep core flows at medium granularity

```markdown
✅ Good:
### 流程1: 用户登录流程
- 用户进入登录页面
- 输入账号密码
  - 账号密码正确
    - 登录成功，进入首页
  - 账号密码错误
    - 提示错误，允许重试（最多5次）
  - 账号被锁定
    - 显示锁定原因，引导解锁
```

### Mistake 3: Incomplete Flows

**Problem**: Core flows that don't show the complete journey

```markdown
❌ Bad:
### 流程1: 用户购买流程
- 用户选择商品
- 用户加入购物车
- 用户点击结算
[... where's the payment? order confirmation? ...]
```

**Solution**: Ensure flows have clear end points

```markdown
✅ Good:
### 流程1: 用户购买流程
- 用户选择商品并加入购物车
- 用户点击结算，进入订单确认页
- 用户选择支付方式并完成支付
  - 支付成功
    - 订单创建成功，显示订单详情
    - 发送订单确认邮件
  - 支付失败
    - 提示失败原因，允许重新支付
```

### Mistake 4: Inconsistent Indentation

**Problem**: Random indentation that doesn't reflect logical hierarchy

```markdown
❌ Bad:
### 流程1: 用户注册流程
- 用户输入邮箱
- 邮箱格式正确
    - 输入密码
  - 密码强度足够
      - 点击注册
- 注册成功
```

**Solution**: Use consistent indentation to show hierarchy

```markdown
✅ Good:
### 流程1: 用户注册流程
- 用户输入邮箱
  - 邮箱格式正确
    - 输入密码
      - 密码强度足够
        - 点击注册
          - 注册成功
```

---

## Summary

### Key Takeaways

1. **Core flows are end-to-end business journeys**, not detailed feature specifications
2. **Number of core flows is not fixed** - depends on the requirement's complexity
3. **Medium detail level (10-15 steps)** - not too high, not too granular
4. **Tree-indented structure** - use Markdown lists to show hierarchy and branches
5. **Place at the beginning** - provides immediate understanding of the system
6. **Foundation for test cases** - both manual core scenarios and automation design

### Quick Checklist

Before finalizing core flows, verify:

- [ ] Each flow has a clear start and end point
- [ ] Each flow represents a complete business objective
- [ ] Detail level is medium (10-15 main steps)
- [ ] Critical branches are included
- [ ] Rare edge cases are excluded
- [ ] Terminology matches the requirement document
- [ ] Indentation correctly shows hierarchy
- [ ] Flows are placed at the beginning of the output
- [ ] Number of flows is reasonable (typically 1-10)

---

*This guide is part of the requirement-analyzer skill. For the main workflow, see SKILL.md.*
