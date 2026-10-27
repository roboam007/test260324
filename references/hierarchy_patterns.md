# Test Case Hierarchy Patterns

This document provides guidance on structuring test cases with appropriate hierarchical levels.

## Core Principle: Reasonable Hierarchy Without Redundancy

A good test case structure should be:
- **Clear**: Easy to navigate and understand
- **Concise**: No unnecessary nesting levels
- **Logical**: Grouping reflects actual testing needs
- **Balanced**: Neither too flat nor too deep

## Recommended Hierarchy Levels

### Standard 3-Level Structure (Most Common)

```
# Feature Module (Level 1 - H2)
## Test Scenario (Level 2 - H3)
### Test Checkpoint (Level 3 - H4)
```

**When to use**: Most functional testing scenarios

**Example**:
```markdown
## User Login
### Valid Credentials Login
#### Standard user login with correct username and password
- Precondition: User account exists and is active
- Action: Enter valid username and password, click login
- Expected: Successfully logged in, redirected to home page

#### Remember me functionality
- Precondition: User account exists
- Action: Check "Remember me", enter credentials, login
- Expected: Session persists after browser close
```

### Simplified 2-Level Structure

```
# Feature Module (Level 1 - H2)
## Test Checkpoint (Level 2 - H3)
```

**When to use**: 
- Simple features with few test cases
- When scenarios don't need grouping
- Quick validation checklists

**Example**:
```markdown
## Copy AIX Tag
### Click copy icon
- Precondition: User is on ME page with AIX Tag displayed
- Action: Click the copy icon next to AIX Tag
- Expected: AIX Tag copied to clipboard, success toast shown

### Verify clipboard content
- Precondition: AIX Tag has been copied
- Action: Paste from clipboard
- Expected: Complete AIX Tag value is pasted correctly
```

### Extended 4-Level Structure

```
# Feature Module (Level 1 - H2)
## Sub-Module (Level 2 - H3)
### Test Scenario (Level 3 - H4)
#### Test Checkpoint (Level 4 - H5)
```

**When to use**:
- Large, complex features with multiple sub-modules
- When clear sub-categorization adds value
- Features spanning multiple pages/flows

**Example**:
```markdown
## Security Settings
### Phone Number Management
#### Bind Phone Number
##### First time binding
- Precondition: User has no phone number bound
- Action: Enter valid phone number, verify OTP
- Expected: Phone number successfully bound

##### Phone number already used by another account
- Precondition: Phone number is bound to different account
- Action: Attempt to bind the phone number
- Expected: Error message "Phone number already in use"

### Password Management
#### Change Password
##### Valid password change
- Precondition: User is logged in
- Action: Enter current password, new password, confirm
- Expected: Password changed successfully
```

## Anti-Patterns to Avoid

### ❌ Too Flat (No Grouping)

```markdown
## Login with valid credentials
## Login with invalid password
## Login with non-existent user
## Password reset request
## Password reset with valid token
## Password reset with expired token
```

**Problem**: No logical grouping, hard to navigate

**Better**:
```markdown
## User Authentication
### Login Scenarios
#### Valid credentials login
#### Invalid password login
#### Non-existent user login

### Password Reset
#### Request password reset
#### Reset with valid token
#### Reset with expired token
```

### ❌ Too Deep (Excessive Nesting)

```markdown
## User Management
### Account Operations
#### Login Operations
##### Credential Validation
###### Valid Credentials
####### Standard Login
######## Username and Password Login
```

**Problem**: Unnecessary nesting, hard to read

**Better**:
```markdown
## User Management
### Login
#### Valid credentials login
#### Invalid credentials login
```

### ❌ Redundant Levels

```markdown
## Card Application
### Card Application Process
#### Apply for Card
##### Card Application Steps
###### Step 1: Select Card Type
```

**Problem**: Repetitive naming, no value added by extra levels

**Better**:
```markdown
## Card Application
### Select Card Type
#### Virtual card selection
#### Physical card selection
```

## Decision Tree: Choosing Hierarchy Depth

```
Start: Analyze the feature
  ↓
Question 1: Is this a simple feature with < 10 test cases?
  ├─ Yes → Use 2-level structure (Feature → Checkpoint)
  └─ No → Continue to Question 2
  ↓
Question 2: Can test cases be naturally grouped into scenarios?
  ├─ Yes → Continue to Question 3
  └─ No → Use 2-level structure (Feature → Checkpoint)
  ↓
Question 3: Does the feature have distinct sub-modules?
  ├─ Yes → Use 4-level structure (Feature → Sub-module → Scenario → Checkpoint)
  └─ No → Use 3-level structure (Feature → Scenario → Checkpoint)
```

## Practical Guidelines

### 1. Start with 3 Levels (Default)

Most features fit well into the 3-level structure. Start here and adjust if needed.

### 2. Add Level Only When It Adds Value

Ask: "Does this level help organize or clarify the test cases?"
- ✅ Yes: Keep the level
- ❌ No: Flatten the structure

### 3. Keep Naming Distinct

Each level should have a distinct purpose:
- **Feature Module**: What major functionality (e.g., "User Login", "Card Application")
- **Scenario/Sub-module**: What specific situation or sub-feature (e.g., "Valid Login", "Invalid Credentials")
- **Checkpoint**: What specific test (e.g., "Login with correct username and password")

### 4. Consistency Within Document

Use the same hierarchy depth for similar features within one document.

### 5. Balance Breadth and Depth

- **Too many siblings** (20+ items at one level): Consider adding a grouping level
- **Too few siblings** (1-2 items at one level): Consider removing that level

## Real-World Examples

### Example 1: ME Page (3-Level Structure)

```markdown
## User Profile Display
### Nickname Display
#### User has set nickname
- Precondition: User has configured a custom nickname
- Action: Navigate to ME page
- Expected: Display "Hi [nickname]"

#### User has not set nickname
- Precondition: User has not set a nickname
- Action: Navigate to ME page
- Expected: Display default nickname or prompt to set

### AIX Tag Display
#### AIX Tag is displayed
- Precondition: User account has AIX Tag
- Action: Navigate to ME page
- Expected: Complete AIX Tag is visible

### Copy AIX Tag
#### Click copy icon
- Precondition: AIX Tag is displayed
- Action: Click copy icon
- Expected: AIX Tag copied to clipboard, success toast shown
```

### Example 2: Phone Binding (4-Level Structure)

```markdown
## Security Settings
### Phone Number Management
#### Bind Phone Number - First Time
##### Valid phone number input
- Precondition: User has no phone bound, in PH region
- Action: Enter valid PH phone number (09xxxxxxxx)
- Expected: Format validation passes, Next button enabled

##### Invalid phone number format
- Precondition: User has no phone bound, in PH region
- Action: Enter invalid phone number (e.g., 01234567890)
- Expected: Error message "Invalid mobile number"

#### Change Phone Number
##### Verify current phone
- Precondition: User has phone bound
- Action: Enter OTP sent to current phone
- Expected: Verification successful, proceed to new phone input

##### Bind new phone
- Precondition: Current phone verified
- Action: Enter new phone number, verify OTP
- Expected: Phone number updated successfully
```

### Example 3: Language Settings (2-Level Structure)

```markdown
## Language Settings
### Default language - System matches app
- Precondition: System language is English or Vietnamese
- Action: First time open app
- Expected: App language matches system language

### Default language - System doesn't match
- Precondition: System language is not English or Vietnamese
- Action: First time open app
- Expected: App defaults to English

### Change language to English
- Precondition: Current language is Vietnamese
- Action: Select English from language list
- Expected: App language switches to English immediately

### Change language to Vietnamese
- Precondition: Current language is English
- Action: Select Vietnamese from language list
- Expected: App language switches to Vietnamese immediately
```

## Markdown Heading Levels

### Standard Mapping

```markdown
# Document Title (H1) - Used once at the top

## Feature Module (H2) - Main functional areas

### Scenario or Sub-module (H3) - Specific test scenarios or sub-features

#### Test Checkpoint (H4) - Individual test cases

##### Additional Detail (H5) - Only if needed for complex cases
```

### Best Practices

1. **H1 once**: Only use H1 for document title
2. **Start features at H2**: All feature modules begin at H2
3. **Don't skip levels**: Go H2 → H3 → H4, not H2 → H4
4. **Rarely use H5+**: Most test cases don't need more than H4

## Summary

| Structure | When to Use | Example Use Cases |
|-----------|-------------|-------------------|
| 2-Level | Simple features, < 10 test cases | Settings toggle, simple CRUD |
| 3-Level | Standard features, clear scenarios | Login, form validation, navigation |
| 4-Level | Complex features, multiple sub-modules | Security settings, multi-step workflows |

**Golden Rule**: Use the simplest structure that clearly organizes your test cases. When in doubt, start with 3 levels and adjust based on actual content.

