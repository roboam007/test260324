# Test Checkpoint Format Guide

This document defines the simplified format for writing test checkpoints.

## Simplified Checkpoint Structure

**Key Principle**: Write test checkpoints in natural, flowing language without explicit structure labels.

### Simple Test (Single Bullet)

```markdown
#### Checkpoint Name
- [Describe validation point naturally, combining context, action, and expected result]
```

### Complex Test (Multiple Bullets)

```markdown
#### Checkpoint Name
- [Step 1 with context]
- [Step 2 and what happens]
- [Step 3 and expected result]
```

**Do NOT use** explicit labels like "Precondition:", "Action:", "Expected:"

## Component Breakdown

### 1. Checkpoint Name (H4 or H5 Heading)

**Purpose**: Concise summary of what is being tested

**Guidelines**:
- Use clear, descriptive names
- Focus on the test objective
- Keep it concise (5-10 words)
- Use action-oriented language when appropriate

**Good Examples**:
- ✅ `#### Valid phone number input`
- ✅ `#### Login with correct credentials`
- ✅ `#### Nickname exceeds maximum length`
- ✅ `#### Copy AIX Tag to clipboard`

**Bad Examples**:
- ❌ `#### Test 1` (Not descriptive)
- ❌ `#### User enters a valid phone number and the system validates it correctly` (Too verbose)
- ❌ `#### Phone` (Too vague)

### 2. Validation Points (Bullet Points)

**Purpose**: Describe what to verify in natural language

**Guidelines for Simple Tests**:
- Combine context, action, and expected result in one flowing sentence
- Be specific about data values and UI behavior
- Keep it concise but complete

**Examples**:
```markdown
- 用户已设置昵称"TestUser",ME页面显示"Hi TestUser"

- 输入有效手机号"09171234567",格式校验通过,"下一步"按钮可用

- 点击AIX Tag旁的复制图标,显示"已复制"提示,剪贴板包含完整AIX Tag值
```

**Guidelines for Complex Tests**:
- Use multiple bullet points for multi-step scenarios
- Each bullet describes one step and its result
- Maintain logical flow from step to step

**Examples**:
```markdown
- Face ID当前关闭,设备支持生物识别,点击开关至开启位置
- 完成身份认证验证
- 完成设备生物识别验证
- Face ID开启成功,显示成功提示

---

- 用户已绑定手机号,点击"开始换绑"
- 进入身份验证页面,完成验证
- 输入新手机号"09171234567",接收并输入OTP
- 手机号换绑成功,返回安全设置页面显示新手机号(脱敏)
```

## Format Variations

### Compact Format (Simple Tests)

For simple tests, you can use a more compact format:

```markdown
#### Test name
- Precondition: [condition]
- Action: [action]
- Expected: [result]
```

**Example**:
```markdown
#### Display default language
- Precondition: First time app launch, system language is Chinese
- Action: Open app
- Expected: App displays in English (default language)
```

### Extended Format (Complex Tests)

For complex tests, add more detail:

```markdown
#### Test name
- Precondition: [main condition]
  - [Detail 1]
  - [Detail 2]
  - [Detail 3]
- Action: [main action]
  - Step 1: [detail]
  - Step 2: [detail]
  - Step 3: [detail]
- Expected: [main result]
  - UI change: [detail]
  - Data change: [detail]
  - System state: [detail]
- Verification:
  - [How to verify 1]
  - [How to verify 2]
```

**Example**:
```markdown
#### Change phone number - complete flow
- Precondition: User has phone bound
  - Current phone: +63 917 123 4567
  - User is logged in
  - OTP service is available
- Action: Complete phone change process
  - Step 1: Navigate to Security Settings > Update Phone Number
  - Step 2: Click "Start Change" button
  - Step 3: Enter OTP sent to current phone (123456)
  - Step 4: Enter new phone number (+63 917 999 8888)
  - Step 5: Enter OTP sent to new phone (654321)
  - Step 6: Click "Confirm" button
- Expected: Phone number updated successfully
  - UI change: Success page displayed with "OK" button
  - Data change: User's phone number in database updated to new number
  - System state: Old phone number no longer associated with account
- Verification:
  - Check user profile shows new phone number
  - Verify OTP sent to new phone number for future operations
  - Confirm old phone number can be used by other accounts
```

## Special Cases

### State Transition Tests

For tests involving state changes:

```markdown
#### State transition name
- Initial state: [starting state]
  - [State details]
- Trigger: [what causes the change]
  - [Action details]
- Final state: [ending state]
  - [State details]
- Verification: [how to confirm state changed]
```

**Example**:
```markdown
#### Card state: Active → Suspended
- Initial state: Card is Active
  - Card can be used for transactions
  - Card shows "Active" status in app
- Trigger: User clicks "Freeze Card" button
  - Confirm freeze in dialog
- Final state: Card is Suspended
  - Card cannot be used for transactions
  - Card shows "Frozen" status in app
  - "Unfreeze" button is available
- Verification: Attempt transaction with card fails
```

### Data Validation Tests

For tests focused on input validation:

```markdown
#### Validation rule name
- Input: [test data]
- Validation rule: [rule being tested]
- Expected: [pass/fail and message]
```

**Example**:
```markdown
#### Phone number validation - PH format
- Input: "09171234567"
- Validation rule: PH phone must start with 09 or 8/9, length 10-11 digits
- Expected: Validation passes, "Next" button enabled

#### Phone number validation - invalid format
- Input: "01234567890"
- Validation rule: PH phone must start with 09 or 8/9
- Expected: Validation fails, error "Invalid mobile number" shown
```

### Permission Tests

For tests involving different user roles:

```markdown
#### Permission scenario name
- User role: [role name]
- Permissions: [what user can/cannot do]
- Action: [what user attempts]
- Expected: [allowed/denied with specific result]
```

**Example**:
```markdown
#### Non-verified user attempts card application
- User role: Registered user (not identity verified)
- Permissions: Can view card info, cannot apply for card
- Action: Click "Apply Card" button
- Expected: Blocked with message "Please complete identity verification first"
  - Dialog shows "Identity Verification Required"
  - "Verify Now" button navigates to verification flow
```

## Writing Tips

### Be Specific

❌ **Vague**: "Enter invalid data"
✅ **Specific**: "Enter '01234567890' (invalid PH phone format)"

❌ **Vague**: "System shows error"
✅ **Specific**: "Error message 'Invalid mobile number' appears below input field"

### Use Concrete Values

❌ **Abstract**: "Enter a long nickname"
✅ **Concrete**: "Enter 'ThisIsAVeryLongNickname' (23 characters, exceeds 10-char limit)"

❌ **Abstract**: "User has some cards"
✅ **Concrete**: "User has 4 cards: 2 Active, 1 Pending activation, 1 Suspended"

### Include UI Details

❌ **Generic**: "Click the button"
✅ **Specific**: "Click the 'Next' button at the bottom of the screen"

❌ **Generic**: "Message appears"
✅ **Specific**: "Success toast 'Copied' appears at the top of screen for 2 seconds"

### Specify Timing When Relevant

```markdown
- Expected: Success message appears
  - Toast displays immediately after click
  - Toast auto-dismisses after 2 seconds
  - User can manually dismiss by swiping
```

### Include Negative Cases

Don't just test happy paths:

```markdown
#### Network error during phone binding
- Precondition: User is on OTP verification page
  - Valid OTP has been sent
- Action: Turn off network, enter correct OTP, click "Verify"
- Expected: Network error handling
  - Error message "Network connection failed" appears
  - User can retry by clicking "Retry" button
  - OTP remains valid (not consumed)
```

## Common Mistakes to Avoid

### 1. Missing Preconditions

❌ **Bad**:
```markdown
#### Login test
- Action: Enter username and password
- Expected: User logged in
```

✅ **Good**:
```markdown
#### Login with valid credentials
- Precondition: User account exists and is active
  - Username: testuser@example.com
  - Password: Test@123
- Action: Enter username and password, click "Login"
- Expected: Successfully logged in, redirected to home page
```

### 2. Vague Expected Results

❌ **Bad**:
```markdown
- Expected: It works correctly
```

✅ **Good**:
```markdown
- Expected: Phone number successfully bound
  - Success page displays with message "Phone number bound successfully"
  - User profile shows new phone number
  - "OK" button returns to Security Settings page
```

### 3. Combining Multiple Tests

❌ **Bad**:
```markdown
#### Test login and profile update
- Action: Login, go to profile, update nickname, logout
- Expected: Everything works
```

✅ **Good**: Split into separate test checkpoints:
```markdown
#### Login with valid credentials
[separate test]

#### Update nickname
[separate test]

#### Logout
[separate test]
```

### 4. Missing Verification Steps

❌ **Bad**:
```markdown
- Expected: Data saved
```

✅ **Good**:
```markdown
- Expected: Data saved successfully
  - Success message "Changes saved" appears
  - Page refreshes showing new data
  - Database record updated (verify via API/database query)
```

## Template Summary

### Basic Template
```markdown
#### [Checkpoint Name]
- Precondition: [Starting state and conditions]
- Action: [What to do]
- Expected: [What should happen]
```

### Detailed Template
```markdown
#### [Checkpoint Name]
- Precondition: [Main condition]
  - [Specific detail 1]
  - [Specific detail 2]
- Action: [Main action]
  - [Step 1]
  - [Step 2]
- Expected: [Main expected result]
  - [Specific validation 1]
  - [Specific validation 2]
- Verification: [How to confirm]
```

Use the basic template for simple tests, and the detailed template for complex scenarios.

