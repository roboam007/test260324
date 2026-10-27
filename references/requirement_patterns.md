# Common Requirement Patterns

This document provides detailed examples of common patterns for organizing functional requirements. Use these patterns as templates when analyzing similar types of requirements.

---

## Pattern 1: Validation Function Points

Use this pattern for input validation, format checking, and data quality requirements.

**Characteristics:**
- Focus on input correctness
- Multiple validation rules (format, length, uniqueness, etc.)
- Clear error messages for each validation failure

**Example:**

```markdown
### 邮箱格式校验
- 输入标准邮箱格式（user@example.com）
  - 预期：格式校验通过，允许提交
- 输入缺少@符号（userexample.com）
  - 预期：提示"邮箱格式不正确"
- 输入缺少域名（user@）
  - 预期：提示"邮箱格式不正确"
- 输入为空
  - 预期：提示"邮箱不能为空"

### 邮箱长度限制
- 输入254字符的邮箱
  - 预期：校验通过，正常保存
- 输入255字符的邮箱
  - 预期：前端限制输入或后端返回"邮箱长度超过限制"

### 邮箱唯一性校验
- 输入未注册的邮箱
  - 预期：校验通过，继续注册流程
- 输入已注册的邮箱
  - 预期：提示"该邮箱已被注册"
```

**When to use:**
- Form input validation
- Data format requirements
- Business rule validation
- Uniqueness checks

---

## Pattern 2: State-based Function Points

Use this pattern for conditional logic that depends on system state, user status, or data conditions.

**Characteristics:**
- Multiple states or conditions
- Different behaviors for each state
- State transitions and rules

**Example:**

```markdown
### 申卡入口展示逻辑
- 卡数<5且无审核中卡片
  - 预期：显示申卡入口，入口高亮可点击
- 卡数<5且有审核中卡片
  - 预期：显示申卡入口，但置灰不可点击
- 卡数=5
  - 预期：不显示任何申卡入口

### 按钮状态控制
- 用户已完成KYC且余额>0
  - 预期：按钮可点击，显示正常样式
- 用户已完成KYC但余额=0
  - 预期：按钮置灰，显示"余额不足"提示
- 用户未完成KYC
  - 预期：按钮隐藏，显示"请先完成身份验证"引导
```

**When to use:**
- UI element visibility/state control
- Feature access control based on user status
- Workflow step conditions
- Permission-based behaviors

---

## Pattern 3: Configuration-based Function Points

Use this pattern for features that behave differently based on configuration, feature flags, or settings.

**Characteristics:**
- Same feature with different configurations
- Clearly separate scenarios for each configuration
- Configuration name in the function point title

**Example:**

```markdown
### 余额校验（开启余额不能为0的配置）
- 所有币种余额均为0
  - 预期：提示"余额不能为零"，跳转充值页面
- 至少一个币种余额大于0
  - 预期：通过余额校验，继续流程

### 余额校验（关闭余额不能为0的配置）
- 所有币种余额均为0
  - 预期：跳过余额校验，直接执行下一步
- 至少一个币种余额大于0
  - 预期：通过余额校验，继续流程

### 实名认证（PH地区配置）
- 用户输入菲律宾身份证号
  - 预期：调用PH身份验证接口
- 用户输入护照号
  - 预期：调用国际护照验证接口

### 实名认证（TH地区配置）
- 用户输入泰国身份证号
  - 预期：调用TH身份验证接口
- 用户输入护照号
  - 预期：调用国际护照验证接口
```

**When to use:**
- Feature flags and toggles
- Regional variations
- A/B testing scenarios
- Environment-specific behaviors
- Multi-tenant configurations

---

## Pattern 4: Boundary and Limit Testing

Use this pattern for testing limits, boundaries, and edge cases of numeric or length constraints.

**Characteristics:**
- Test values at boundaries (min, max, min-1, max+1)
- Clear distinction between frontend and backend validation
- Cover both valid and invalid boundary cases

**Example:**

```markdown
### 输入长度限制
- 输入50字符
  - 预期：可以正常输入
- 输入51字符
  - 预期：前端限制无法继续输入
- 输入254字符
  - 预期：达到最大长度，正常保存
- 输入255字符
  - 预期：超过限制，后端返回错误

### 转账金额限制
- 输入0.01（最小金额）
  - 预期：校验通过，可以提交
- 输入0.001（小于最小金额）
  - 预期：提示"最小转账金额为0.01"
- 输入10000（最大金额）
  - 预期：校验通过，可以提交
- 输入10000.01（超过最大金额）
  - 预期：提示"单笔转账不能超过10000"

### 昵称字符限制
- 输入1个字符
  - 预期：提示"昵称至少2个字符"
- 输入2个字符
  - 预期：校验通过
- 输入10个字符
  - 预期：校验通过
- 输入11个字符
  - 预期：前端限制无法继续输入
```

**When to use:**
- Length constraints (min/max)
- Numeric ranges (amount, quantity, age, etc.)
- Date/time boundaries
- File size limits
- Rate limits

---

## Pattern 5: Multi-step Process Flow

Use this pattern for workflows that involve multiple sequential steps with dependencies.

**Characteristics:**
- Clear step sequence
- Prerequisites for each step
- Success and failure paths
- Step transitions

**Example:**

```markdown
### Step 1: 手机号验证
- 输入有效的手机号
  - 预期：发送验证码，进入Step 2
- 输入无效的手机号
  - 预期：提示"手机号格式不正确"，停留在Step 1

### Step 2: 验证码确认
- 输入正确的验证码
  - 预期：验证通过，进入Step 3
- 输入错误的验证码（尝试<3次）
  - 预期：提示"验证码错误"，允许重试
- 输入错误的验证码（尝试≥3次）
  - 预期：提示"验证失败次数过多"，返回Step 1

### Step 3: 设置密码
- 输入符合规则的密码
  - 预期：密码设置成功，完成注册流程
- 输入不符合规则的密码
  - 预期：提示密码规则，停留在Step 3
```

**When to use:**
- Registration/onboarding flows
- Application submission processes
- Checkout/payment flows
- Multi-step forms
- Wizard-style interfaces

---

## Pattern 6: Permission and Role-based Access

Use this pattern for features with different behaviors based on user roles or permissions.

**Characteristics:**
- Different user roles or permission levels
- Access control for features/data
- Role-specific behaviors

**Example:**

```markdown
### 订单查看权限
- 普通用户访问自己的订单
  - 预期：显示订单详情
- 普通用户访问他人的订单
  - 预期：提示"无权查看"，返回403错误
- 客服人员访问任意订单
  - 预期：显示订单详情，包含客服操作按钮
- 管理员访问任意订单
  - 预期：显示订单详情，包含所有管理操作

### 数据导出功能
- 普通用户点击导出
  - 预期：功能不可见或置灰
- VIP用户点击导出
  - 预期：导出当前页数据（最多100条）
- 管理员点击导出
  - 预期：导出全部数据，无限制
```

**When to use:**
- Role-based access control (RBAC)
- Permission-based features
- User tier/subscription features
- Admin vs. user behaviors

---

## Pattern 7: Error Handling and Recovery

Use this pattern for error scenarios, exception handling, and recovery mechanisms.

**Characteristics:**
- Various error conditions
- Error messages and codes
- Recovery or retry mechanisms
- Fallback behaviors

**Example:**

```markdown
### API调用失败处理
- 网络超时（timeout）
  - 预期：显示"网络连接超时，请重试"，提供重试按钮
- 服务器错误（500）
  - 预期：显示"服务暂时不可用"，记录错误日志
- 未授权（401）
  - 预期：清除本地token，跳转到登录页
- 业务错误（400）
  - 预期：显示服务器返回的具体错误信息

### 支付失败处理
- 余额不足
  - 预期：提示"余额不足"，引导用户充值
- 支付密码错误（尝试<3次）
  - 预期：提示"密码错误"，允许重新输入
- 支付密码错误（尝试≥3次）
  - 预期：锁定支付功能30分钟，提示"密码错误次数过多"
- 银行系统维护
  - 预期：提示"银行系统维护中"，建议稍后重试
```

**When to use:**
- API error handling
- Network failure scenarios
- Payment/transaction failures
- System unavailability
- Data validation errors

---

## Combining Patterns

In real-world requirements, you often need to combine multiple patterns. Here's an example:

```markdown
### 转账功能（综合示例）

#### 权限校验（Pattern 6: Permission-based）
- 用户未完成KYC
  - 预期：提示"请先完成身份验证"，跳转到KYC页面
- 用户已完成KYC
  - 预期：可以访问转账功能

#### 金额校验（Pattern 1: Validation + Pattern 4: Boundary）
- 输入0.01（最小金额）
  - 预期：校验通过
- 输入0.001（小于最小金额）
  - 预期：提示"最小转账金额为0.01"
- 输入10000（最大金额）
  - 预期：校验通过
- 输入10000.01（超过最大金额）
  - 预期：提示"单笔转账不能超过10000"

#### 余额校验（Pattern 2: State-based）
- 余额充足（余额 ≥ 转账金额 + 手续费）
  - 预期：校验通过，允许提交
- 余额不足（余额 < 转账金额 + 手续费）
  - 预期：提示"余额不足"，显示当前余额和所需金额

#### 转账执行（Pattern 7: Error Handling）
- 转账成功
  - 预期：显示成功页面，更新余额，发送通知
- 网络超时
  - 预期：提示"请求超时"，提供查询转账状态按钮
- 对方账户异常
  - 预期：提示"对方账户状态异常，无法转账"，退回金额
```

---

## Tips for Using Patterns

1. **Identify the pattern first** - Before writing scenarios, identify which pattern(s) apply
2. **Adapt, don't copy** - Use patterns as templates, but adapt to your specific requirements
3. **Combine when needed** - Real features often require multiple patterns
4. **Keep it testable** - Every scenario should be independently verifiable
5. **Be specific** - Use concrete values and clear conditions

---

## When Patterns Don't Fit

If your requirement doesn't fit any of these patterns:

1. **Analyze the requirement type** - What makes it unique?
2. **Create a custom structure** - Follow the general principles (condition → expected result)
3. **Consider if it's a new pattern** - If you see it repeatedly, it might be worth documenting as a new pattern
4. **Focus on clarity** - The goal is clear, testable scenarios, not forcing a pattern

Remember: Patterns are tools to help you organize requirements more efficiently. They're not rigid rules that must always be followed.
