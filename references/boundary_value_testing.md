# Boundary Value Testing Guide

## Overview

Boundary Value Testing (BVT) is a critical testing technique that focuses on testing values at the boundaries of input domains. This guide ensures comprehensive coverage of edge cases that are often missed when only testing explicitly mentioned conditions.

## Why Boundary Value Testing Matters

**Common Problem**: Requirements often describe conditions using comparison operators (>, <, ≥, ≤, =), but test cases only cover the explicitly mentioned scenarios, missing critical boundary values.

**Example Issue**:
- Requirement: "剩余时间大于1小时显示小时，小于1小时显示分钟"
- Incomplete Test: Only tests "2小时" and "30分钟"
- **Missing**: What happens at exactly 1 hour? What about < 1 minute?

## Core Principle

**For every comparison condition in requirements, test ALL boundary values:**
- Values **above** the threshold
- Values **at** the threshold (equal to)
- Values **below** the threshold

## Boundary Value Analysis Patterns

### Pattern 1: Greater Than / Less Than (>, <)

**Requirement Pattern**: "If X > threshold, do A; if X < threshold, do B"

**Required Test Cases**:
1. X > threshold (typical value)
2. X = threshold (boundary value)
3. X < threshold (typical value)

**Example**:
```markdown
Requirement: "剩余时间大于1小时显示小时单位，小于1小时显示分钟单位"

Test Cases:
#### 剩余时间大于1小时
- 剩余时间为2小时
- 显示"2 hours"

#### 剩余时间等于1小时
- 剩余时间为1小时
- 显示"1 hour"或"60 minutes"（需明确实现）

#### 剩余时间小于1小时
- 剩余时间为30分钟
- 显示"30 minutes"
```

### Pattern 2: Range Boundaries (min-max)

**Requirement Pattern**: "Value must be between min and max"

**Required Test Cases**:
1. min - 1 (below minimum)
2. min (minimum boundary)
3. min + 1 (just above minimum)
4. max - 1 (just below maximum)
5. max (maximum boundary)
6. max + 1 (above maximum)

**Example**:
```markdown
Requirement: "输入长度限制为1-50字符"

Test Cases:
#### 输入0字符（空）
- 输入框为空
- 提示"不能为空"

#### 输入1字符（最小值）
- 输入"A"
- 校验通过

#### 输入2字符
- 输入"AB"
- 校验通过

#### 输入49字符
- 输入49个字符
- 校验通过

#### 输入50字符（最大值）
- 输入50个字符
- 校验通过

#### 输入51字符（超出最大值）
- 尝试输入51个字符
- 前端阻止输入或提示"超出最大长度"
```

### Pattern 3: Count/Frequency Thresholds

**Requirement Pattern**: "After N attempts, trigger action"

**Required Test Cases**:
1. N - 1 attempts (just before threshold)
2. N attempts (at threshold)
3. N + 1 attempts (after threshold)

**Example**:
```markdown
Requirement: "24小时内失败5次锁定20分钟，失败10次锁定24小时"

Test Cases:
#### 失败4次
- 24小时内累计失败4次
- 未触发锁定，允许继续尝试

#### 失败5次（第一次锁定阈值）
- 24小时内累计失败5次
- 触发锁定20分钟

#### 失败6次
- 24小时内累计失败6次
- 保持锁定20分钟状态

#### 失败9次
- 24小时内累计失败9次
- 保持锁定状态

#### 失败10次（第二次锁定阈值）
- 24小时内累计失败10次
- 触发锁定24小时

#### 失败11次
- 24小时内累计失败11次
- 保持锁定24小时状态
```

### Pattern 4: Time-Based Boundaries

**Requirement Pattern**: "Display format changes based on time units"

**Required Test Cases**: Test all unit boundaries (hours, minutes, seconds)

**Example**:
```markdown
Requirement: "剩余时间大于1小时显示小时，小于1小时显示分钟"

Complete Test Cases:
#### 剩余时间大于1小时
- 剩余时间为2小时30分钟
- 显示"2 hours"或"2.5 hours"

#### 剩余时间等于1小时
- 剩余时间为1小时
- 显示"1 hour"或"60 minutes"（需确认）

#### 剩余时间小于1小时大于1分钟
- 剩余时间为30分钟
- 显示"30 minutes"

#### 剩余时间等于1分钟
- 剩余时间为1分钟
- 显示"1 minute"或"60 seconds"（需确认）

#### 剩余时间小于1分钟
- 剩余时间为30秒
- 显示"30 seconds"或"1 minute"（需确认）

#### 剩余时间等于0
- 剩余时间为0秒
- 显示"0 seconds"或立即解锁（需确认）
```

### Pattern 5: Amount/Price Thresholds

**Requirement Pattern**: "If amount ≥ threshold, apply discount"

**Required Test Cases**:
1. amount < threshold (just below)
2. amount = threshold (exactly at)
3. amount > threshold (just above)

**Example**:
```markdown
Requirement: "订单金额≥100元显示优惠券入口"

Test Cases:
#### 订单金额99.99元
- 订单金额为99.99元
- 不显示优惠券入口

#### 订单金额100元
- 订单金额为100元
- 显示优惠券入口

#### 订单金额100.01元
- 订单金额为100.01元
- 显示优惠券入口
```

### Pattern 6: Age/Date Ranges

**Requirement Pattern**: "Age must be between X and Y"

**Required Test Cases**: Test X-1, X, X+1, Y-1, Y, Y+1

**Example**:
```markdown
Requirement: "申请人年龄必须在18-65岁之间"

Test Cases:
#### 年龄17岁（未满最小值）
- 输入出生日期对应年龄17岁
- 提示"年龄必须满18岁"

#### 年龄18岁（最小值）
- 输入出生日期对应年龄18岁
- 校验通过

#### 年龄19岁
- 输入出生日期对应年龄19岁
- 校验通过

#### 年龄64岁
- 输入出生日期对应年龄64岁
- 校验通过

#### 年龄65岁（最大值）
- 输入出生日期对应年龄65岁
- 校验通过

#### 年龄66岁（超过最大值）
- 输入出生日期对应年龄66岁
- 提示"年龄不能超过65岁"
```

## Quick Reference Table

| Requirement Type | Boundary Values to Test |
|-----------------|------------------------|
| X > N | X = N+1, X = N, X = N-1 |
| X < N | X = N-1, X = N, X = N+1 |
| X ≥ N | X = N-1, X = N, X = N+1 |
| X ≤ N | X = N-1, X = N, X = N+1 |
| min ≤ X ≤ max | X = min-1, min, min+1, max-1, max, max+1 |
| After N times | N-1, N, N+1 times |
| Time > 1 hour | > 1h, = 1h, < 1h, = 1min, < 1min, = 0 |
| Length max N | N-1, N, N+1 characters |

## Common Boundary Scenarios in Requirements

### Scenario 1: Input Length Limits

```markdown
Requirement: "邮箱最长103字符"

Test Cases:
- 102字符（最大值-1）
- 103字符（最大值）
- 104字符（超出最大值）
```

### Scenario 2: Retry Limits

```markdown
Requirement: "AAI同一个signatureId最多重试3次"

Test Cases:
- 重试2次
- 重试3次（达到限制）
- 尝试第4次重试（超出限制）
```

### Scenario 3: Timeout Thresholds

```markdown
Requirement: "等待超过30秒跳转失败页面"

Test Cases:
- 等待29秒
- 等待30秒（边界值）
- 等待31秒
```

### Scenario 4: File Size Limits

```markdown
Requirement: "文件大小上限16MB"

Test Cases:
- 上传15.9MB文件
- 上传16MB文件（边界值）
- 上传16.1MB文件
```

### Scenario 5: Display Format Switching

```markdown
Requirement: "大于1小时显示小时，小于1小时显示分钟"

Test Cases:
- 2小时（大于1小时）
- 1小时（边界值）
- 59分钟（小于1小时）
- 1分钟（边界值）
- 30秒（小于1分钟）
- 0秒（边界值）
```

## Boundary Value Testing Checklist

When reviewing requirements, look for these keywords and add boundary tests:

- [ ] **"大于" (greater than)** → Test >, =, <
- [ ] **"小于" (less than)** → Test <, =, >
- [ ] **"最大" (maximum)** → Test max-1, max, max+1
- [ ] **"最小" (minimum)** → Test min-1, min, min+1
- [ ] **"范围" (range)** → Test both boundaries and outside
- [ ] **"次数" (count)** → Test limit-1, limit, limit+1
- [ ] **"时间" (time)** → Test all unit boundaries
- [ ] **"长度" (length)** → Test max-1, max, max+1
- [ ] **"金额" (amount)** → Test threshold-0.01, threshold, threshold+0.01
- [ ] **"年龄" (age)** → Test min-1, min, max, max+1

## Best Practices

### 1. Always Test the Boundary Itself

❌ **Wrong**: Only test values clearly above or below
```markdown
- 剩余时间2小时 → 显示小时
- 剩余时间30分钟 → 显示分钟
```

✅ **Correct**: Test the boundary value
```markdown
- 剩余时间2小时 → 显示小时
- 剩余时间1小时 → 显示？（需确认）
- 剩余时间30分钟 → 显示分钟
```

### 2. Consider Multiple Unit Boundaries

For time-based requirements, consider all relevant units:
- Hours (1h, 2h, 24h)
- Minutes (1min, 30min, 59min, 60min)
- Seconds (1s, 30s, 59s, 60s)

### 3. Test Zero and Negative Values

Where applicable:
- Zero (0)
- Negative values (-1)
- Empty/null

### 4. Document Ambiguities

When boundary behavior is unclear, note it:
```markdown
#### 剩余时间等于1小时
- 剩余时间为1小时
- 显示"1 hour"或"60 minutes"（待确认具体实现）
```

## Integration with Test Case Generation

When generating test cases:

1. **Scan requirements** for comparison operators and thresholds
2. **Identify all boundaries** (>, <, =, min, max)
3. **Generate test cases** for each boundary value
4. **Add notes** for ambiguous boundary behavior
5. **Verify coverage** using the checklist above

## Summary

**Key Takeaway**: When you see comparison conditions in requirements, don't just test the obvious cases. Always test the boundary values (equal to threshold) and edge cases (just above/below threshold).

This ensures:
- ✅ Complete test coverage
- ✅ Early detection of off-by-one errors
- ✅ Clear specification of boundary behavior
- ✅ Better quality assurance
