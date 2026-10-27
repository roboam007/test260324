# Test Case Examples

This document provides complete examples of well-structured test cases for different types of features.

## Example 1: Simple Feature (2-Level Structure)

**Feature**: Language Settings

```markdown
# AIX App Settings - Test Cases

## Document Information
- Based on requirement: AIX Settings V1.0
- Test scope: Language selection and switching
- Structure: Feature → Checkpoint

---

## Language Settings

### Supported languages list
- Precondition: User is on Language Selection page
- Action: View available language options
- Expected: Two languages displayed
  - English
  - Tiếng Việt (Vietnamese)

### Default language - system matches app
- Precondition: First time app launch
  - System language is English
- Action: Open app
- Expected: App displays in English

### Default language - system matches app (Vietnamese)
- Precondition: First time app launch
  - System language is Vietnamese
- Action: Open app
- Expected: App displays in Vietnamese

### Default language - system doesn't match
- Precondition: First time app launch
  - System language is Chinese (not supported)
- Action: Open app
- Expected: App defaults to English

### Region variants ignored
- Precondition: First time app launch
  - System language is English (UK) or English (US)
- Action: Open app
- Expected: App displays in English (no region distinction)

### Change language to English
- Precondition: Current app language is Vietnamese
  - User is on Language Selection page
- Action: Select "English" from language list
- Expected: Language switches immediately
  - All UI text changes to English
  - Selection persists after app restart

### Change language to Vietnamese
- Precondition: Current app language is English
  - User is on Language Selection page
- Action: Select "Tiếng Việt" from language list
- Expected: Language switches immediately
  - All UI text changes to Vietnamese
  - Selection persists after app restart

### Language persistence
- Precondition: User has selected Vietnamese
- Action: Close app completely and reopen
- Expected: App opens in Vietnamese (user preference remembered)

### Language applies globally
- Precondition: User changes language to Vietnamese
- Action: Navigate through different app sections
  - ME page
  - Settings page
  - Card page
- Expected: All pages display in Vietnamese
```

## Example 2: Standard Feature (3-Level Structure)

**Feature**: User Profile Management

```markdown
# AIX ME Module - Test Cases

## Document Information
- Based on requirement: AIX ME Module V1.0
- Test scope: Personal information management
- Structure: Feature → Scenario → Checkpoint

---

## Personal Information

### Nickname Display

#### User has set nickname
- Precondition: User has configured nickname "TestUser"
  - User is logged in
- Action: Navigate to ME page
- Expected: Nickname displayed as "Hi TestUser"
  - Format: "Hi " + nickname
  - Displayed at top of ME page

#### User has not set nickname
- Precondition: User has never set a nickname
  - User is logged in
- Action: Navigate to ME page
- Expected: Default nickname displayed
  - (Note: Specific default behavior to be clarified)

### Nickname Modification

#### Valid nickname - Chinese characters
- Precondition: User is on Personal Info page
  - Current nickname: "OldName"
- Action: Modify nickname
  - Enter "测试用户" (Chinese characters)
  - Click "Save"
- Expected: Nickname updated successfully
  - Success message appears
  - ME page shows "Hi 测试用户"

#### Valid nickname - English characters
- Precondition: User is on Personal Info page
- Action: Enter "TestUser" (English characters), click "Save"
- Expected: Nickname updated successfully
  - ME page shows "Hi TestUser"

#### Valid nickname - Numbers
- Precondition: User is on Personal Info page
- Action: Enter "User123" (alphanumeric), click "Save"
- Expected: Nickname updated successfully
  - ME page shows "Hi User123"

#### Valid nickname - Mixed characters
- Precondition: User is on Personal Info page
- Action: Enter "测试User123" (Chinese + English + numbers), click "Save"
- Expected: Nickname updated successfully
  - All character types supported

#### Invalid nickname - Special characters
- Precondition: User is on Personal Info page
- Action: Enter "Test@User#" (contains special characters), click "Save"
- Expected: Validation fails
  - Error message: "Only Chinese, English, and numbers are allowed"
  - Nickname not saved

#### Valid nickname - Maximum length (10 characters)
- Precondition: User is on Personal Info page
- Action: Enter "1234567890" (exactly 10 characters), click "Save"
- Expected: Nickname saved successfully
  - All 10 characters accepted

#### Invalid nickname - Exceeds maximum length
- Precondition: User is on Personal Info page
- Action: Attempt to enter "12345678901" (11 characters)
- Expected: Input prevented
  - Frontend blocks input after 10th character
  - Cannot type 11th character

#### Nickname uniqueness not required
- Precondition: Another user has nickname "CommonName"
  - Current user is on Personal Info page
- Action: Enter "CommonName", click "Save"
- Expected: Nickname saved successfully
  - Duplicate nicknames allowed across users

#### Nickname takes effect immediately
- Precondition: User is on Personal Info page
  - Current nickname: "OldName"
- Action: Change nickname to "NewName", click "Save"
- Expected: Update takes effect immediately
  - ME page shows "Hi NewName" without app restart
  - All pages reflect new nickname

### AIX ID Display and Copy

#### AIX ID displayed
- Precondition: User account has AIX ID "AIX123456789"
  - User is on Personal Info page
- Action: View AIX ID section
- Expected: Complete AIX ID displayed
  - Shows "AIX123456789"
  - Displayed in read-only format

#### Copy AIX ID
- Precondition: User is on Personal Info page
  - AIX ID "AIX123456789" is displayed
- Action: Click copy icon next to AIX ID
- Expected: AIX ID copied to clipboard
  - Complete value "AIX123456789" in clipboard
  - Success feedback provided (toast or icon change)

#### Verify copied AIX ID
- Precondition: AIX ID has been copied
- Action: Paste from clipboard into text field
- Expected: Exact AIX ID value pasted
  - Value matches displayed AIX ID
  - No formatting or extra characters added
```

## Example 3: Complex Feature (4-Level Structure)

**Feature**: Security Settings - Phone Number Management

```markdown
# AIX Security Settings - Test Cases

## Document Information
- Based on requirement: AIX Security V1.0
- Test scope: Phone number binding and management
- Structure: Feature → Sub-module → Scenario → Checkpoint

---

## Security Settings

### Phone Number Management

#### Entry and Status Display

##### No phone number bound
- Precondition: User account has no phone number
  - User is on Security Settings page
- Action: View "Update Phone Number" section
- Expected: Shows "Not bound" status
  - "Bind Now" button displayed

##### Phone number already bound
- Precondition: User has phone "+63 917 123 4567" bound
  - User is on Security Settings page
- Action: View "Update Phone Number" section
- Expected: Shows masked phone number
  - Format: "+63 ***1234567" (first 3 digits after country code masked)
  - "Change" button displayed

#### First Time Binding - Guide Page

##### Display guide page for unbound user
- Precondition: User has no phone bound
- Action: Click "Bind Now" button
- Expected: Navigate to Phone Binding Guide page
  - Title: "Bind Phone Number"
  - Shows guide text explaining benefits
  - "Start Binding" button displayed

##### Start binding flow
- Precondition: User is on Phone Binding Guide page
- Action: Click "Start Binding" button
- Expected: Navigate to Phone Number Input page
  - Country code selector displayed
  - Phone number input field displayed

#### Phone Number Input - Philippines (PH)

##### Valid format - 09 prefix, 11 digits
- Precondition: User is on Phone Number Input page
  - Country code: +63 (Philippines)
- Action: Enter "09171234567"
- Expected: Validation passes
  - No error message
  - "Next" button enabled

##### Valid format - 8 prefix, 10 digits
- Precondition: Country code +63 selected
- Action: Enter "8123456789"
- Expected: Validation passes
  - "Next" button enabled

##### Valid format - 9 prefix, 10 digits
- Precondition: Country code +63 selected
- Action: Enter "9123456789"
- Expected: Validation passes
  - "Next" button enabled

##### Invalid format - wrong prefix
- Precondition: Country code +63 selected
- Action: Enter "01234567890"
- Expected: Validation fails
  - Error message: "Invalid mobile number"
  - "Next" button disabled

##### Invalid format - 09 prefix, 12 digits
- Precondition: Country code +63 selected
- Action: Attempt to enter "091712345678" (12 digits)
- Expected: Input blocked
  - Cannot enter 12th digit
  - Frontend prevents input beyond 11 digits

##### Invalid format - 8 prefix, 11 digits
- Precondition: Country code +63 selected
- Action: Attempt to enter "81234567890" (11 digits with 8 prefix)
- Expected: Input blocked
  - Cannot enter 11th digit
  - Maximum 10 digits for 8/9 prefix

#### Phone Number Input - Vietnam (VN)

##### Valid format - 03 prefix, 10 digits
- Precondition: Country code +84 (Vietnam) selected
- Action: Enter "0312345678"
- Expected: Validation passes
  - "Next" button enabled

##### Valid format - 05 prefix
- Precondition: Country code +84 selected
- Action: Enter "0512345678"
- Expected: Validation passes

##### Valid format - 07 prefix
- Precondition: Country code +84 selected
- Action: Enter "0712345678"
- Expected: Validation passes

##### Valid format - 08 prefix
- Precondition: Country code +84 selected
- Action: Enter "0812345678"
- Expected: Validation passes

##### Valid format - 09 prefix
- Precondition: Country code +84 selected
- Action: Enter "0912345678"
- Expected: Validation passes

##### Invalid format - wrong prefix
- Precondition: Country code +84 selected
- Action: Enter "0212345678"
- Expected: Validation fails
  - Error message: "Invalid mobile number"
  - "Next" button disabled

##### Invalid format - 11 digits
- Precondition: Country code +84 selected
- Action: Attempt to enter "03123456789" (11 digits)
- Expected: Input blocked
  - Cannot enter 11th digit
  - Maximum 10 digits for VN

#### Phone Number Input - Australia (AU)

##### Valid format - 04 prefix, 10 digits
- Precondition: Country code +61 (Australia) selected
- Action: Enter "0412345678"
- Expected: Validation passes
  - "Next" button enabled

##### Invalid format - wrong prefix
- Precondition: Country code +61 selected
- Action: Enter "0512345678"
- Expected: Validation fails
  - Error message: "Invalid mobile number"
  - "Next" button disabled

##### Invalid format - 11 digits
- Precondition: Country code +61 selected
- Action: Attempt to enter "04123456789" (11 digits)
- Expected: Input blocked
  - Cannot enter 11th digit

#### Phone Number Availability Check

##### Phone number available
- Precondition: User entered valid phone "+63 917 123 4567"
  - This phone is not bound to any account
- Action: Click "Next" button
- Expected: Proceed to OTP verification
  - OTP sent to entered phone number
  - Navigate to OTP input page

##### Phone number already used
- Precondition: User entered phone "+63 917 999 8888"
  - This phone is already bound to another account
- Action: Click "Next" button
- Expected: Error displayed
  - Error message: "This phone number is already in use"
  - Remain on phone input page
  - User can modify input

#### OTP Verification

##### Valid OTP entered
- Precondition: User is on OTP verification page
  - OTP "123456" sent to phone
- Action: Enter "123456", click "Verify"
- Expected: Verification successful
  - Phone number bound to account
  - Navigate to success page

##### Invalid OTP entered
- Precondition: User is on OTP verification page
  - Correct OTP is "123456"
- Action: Enter "999999", click "Verify"
- Expected: Verification fails
  - Error message: "Invalid verification code"
  - Remain on OTP page
  - User can retry

##### OTP expired
- Precondition: OTP sent 5 minutes ago (expired)
  - User is on OTP verification page
- Action: Enter expired OTP, click "Verify"
- Expected: Verification fails
  - Error message: "Verification code expired"
  - "Resend" button available

##### Resend OTP
- Precondition: User is on OTP verification page
- Action: Click "Resend" button
- Expected: New OTP sent
  - Success message: "Verification code sent"
  - Countdown timer starts (e.g., 60 seconds)
  - Cannot resend until timer expires

#### Binding Success

##### Success page display
- Precondition: OTP verification successful
- Action: View success page
- Expected: Success page displayed
  - Success icon/message shown
  - "OK" button displayed

##### Return to entry point
- Precondition: User is on binding success page
- Action: Click "OK" button
- Expected: Return to Security Settings page
  - Phone number now displayed (masked)
  - Status changed from "Not bound" to showing phone number

#### Change Phone Number - Guide Page

##### Display guide page for bound user
- Precondition: User has phone bound
  - User is on Security Settings page
- Action: Click "Change" button
- Expected: Navigate to Change Phone Guide page
  - Title: "Change Phone Number"
  - Shows guide text about verification requirement
  - "Start Change" button displayed

##### Start change flow
- Precondition: User is on Change Phone Guide page
- Action: Click "Start Change" button
- Expected: Navigate to Identity Verification page
  - (Verification flow details in separate requirement)

#### Change Phone Number - Complete Flow

##### Successful phone change
- Precondition: User completed identity verification
  - Current phone: +63 917 123 4567
- Action: Complete phone change process
  - Enter new phone: +63 917 999 8888
  - Verify OTP for new phone
  - Confirm change
- Expected: Phone number updated
  - Success page displayed
  - Security Settings shows new phone (masked)
  - Old phone number released (can be used by others)

### Face ID Management

#### Face ID Status Display

##### Face ID disabled
- Precondition: Face ID is not enabled for account
  - User is on Security Settings page
- Action: View Face ID section
- Expected: Toggle switch in OFF position
  - Status text: "Face ID is off"

##### Face ID enabled
- Precondition: Face ID is enabled for account
  - User is on Security Settings page
- Action: View Face ID section
- Expected: Toggle switch in ON position
  - Status text: "Face ID is on"

#### Enable Face ID

##### Enable Face ID - complete flow
- Precondition: Face ID is currently disabled
  - Device supports biometric authentication
  - User has registered biometrics on device
- Action: Toggle Face ID switch to ON
- Expected: Verification flow starts
  - Step 1: Identity verification prompt appears
  - Step 2: After identity verification, device biometric prompt appears
  - Step 3: User completes device biometric verification
  - Step 4: Face ID enabled successfully
  - Success toast: "Face ID enabled"

##### Enable Face ID - identity verification fails
- Precondition: Face ID is disabled
- Action: Toggle switch to ON, fail identity verification
- Expected: Face ID not enabled
  - Switch remains in OFF position
  - Error message shown

##### Enable Face ID - device biometric fails
- Precondition: Face ID is disabled
  - Identity verification passed
- Action: Fail device biometric verification
- Expected: Face ID not enabled
  - Switch remains in OFF position
  - User can retry

##### Enable Face ID - device not supported
- Precondition: Device does not support biometric authentication
- Action: Attempt to toggle Face ID switch
- Expected: Error message displayed
  - Message: "Biometric authentication not available on this device"
  - Switch remains disabled

#### Disable Face ID

##### Manual disable
- Precondition: Face ID is currently enabled
- Action: Toggle Face ID switch to OFF
- Expected: Face ID disabled immediately
  - No verification required
  - Success toast: "Face ID has turned off"
  - Switch in OFF position

##### Auto-disable on credential change
- Precondition: Face ID is enabled
  - User has biometric credentials registered on device
- Action: User modifies device biometric credentials
  - (e.g., adds new fingerprint, removes face data)
- Expected: Face ID automatically disabled
  - App detects credential invalidation
  - Switch shows OFF position
  - User must re-enable Face ID to use again

##### Re-enable after auto-disable
- Precondition: Face ID was auto-disabled due to credential change
- Action: Toggle switch to ON
- Expected: Complete enable flow required
  - Must complete identity verification again
  - Must complete device biometric verification again
  - Cannot skip verification steps
```

## Example 4: State-Based Testing

**Feature**: Card State Management

```markdown
## Card State Management

### Card State Transitions

#### Active → Frozen (User-initiated)
- Initial state: Card is Active
  - Card can process transactions
  - Card status shows "Active" in app
- Trigger: User clicks "Freeze Card" button
  - Confirmation dialog appears
  - User confirms freeze action
- Final state: Card is Frozen
  - Card cannot process transactions
  - Card status shows "Frozen" in app
  - "Unfreeze Card" button available
- Verification:
  - Attempt transaction with card fails
  - Card list shows frozen icon
  - Push notification sent: "Card frozen"

#### Frozen → Active (User-initiated)
- Initial state: Card is Frozen
  - Card cannot process transactions
- Trigger: User clicks "Unfreeze Card" button
  - Confirmation dialog appears
  - User confirms unfreeze action
- Final state: Card is Active
  - Card can process transactions
  - Card status shows "Active"
  - "Freeze Card" button available
- Verification:
  - Transaction with card succeeds
  - Card list shows active icon
  - Push notification sent: "Card activated"

#### Active → Blocked (System-initiated)
- Initial state: Card is Active
- Trigger: System detects suspicious activity
  - Multiple failed PIN attempts
  - Or fraud detection triggered
- Final state: Card is Blocked
  - Card cannot process transactions
  - Card status shows "Blocked"
  - User cannot unblock (must contact support)
- Verification:
  - Transaction with card fails
  - User sees "Contact Support" message
  - Support ticket auto-created
```

## Example 5: Permission-Based Testing

**Feature**: Card Management Permissions

```markdown
## Card Management Permissions

### Card Application Permission

#### Verified user
- User role: Identity verified user
- Permissions: Can apply for cards
- Action: Click "Apply Card" button
- Expected: Navigate to card application flow
  - Card type selection page displayed
  - User can proceed with application

#### Unverified user
- User role: Registered but not identity verified
- Permissions: Cannot apply for cards
- Action: Click "Apply Card" button
- Expected: Blocked with verification prompt
  - Dialog: "Identity Verification Required"
  - Message: "Please complete identity verification to apply for cards"
  - "Verify Now" button navigates to verification flow
  - "Cancel" button closes dialog

#### Suspended account
- User role: Account suspended due to policy violation
- Permissions: Cannot apply for cards
- Action: Attempt to access card application
- Expected: Blocked with account status message
  - Dialog: "Account Suspended"
  - Message: "Your account is temporarily suspended. Please contact support."
  - "Contact Support" button opens support chat
```

## Key Takeaways from Examples

### Structure Selection
- **Example 1**: Simple feature with straightforward tests → 2-level structure
- **Example 2**: Standard feature with clear scenarios → 3-level structure
- **Example 3**: Complex feature with sub-modules → 4-level structure
- **Example 4**: State transitions → Specialized format
- **Example 5**: Permissions → Specialized format

### Common Patterns
1. **Always include preconditions**: Set up the test context clearly
2. **Be specific with data**: Use concrete values, not abstractions
3. **Describe expected results in detail**: UI changes, messages, state changes
4. **Include verification steps**: How to confirm the test passed
5. **Test both positive and negative cases**: Valid inputs and error conditions
6. **Cover edge cases mentioned in requirements**: Boundaries, limits, special states

### Formatting Consistency
- Use consistent heading levels throughout document
- Maintain consistent checkpoint structure (Precondition → Action → Expected)
- Use bullet points for sub-items
- Include document header with metadata
- Separate major sections with horizontal rules (---)

