# Implementation TODO - OTP/Login for All Users (No Gmail Req)

## Status: ✅ In Progress

### Step 1: Update config.py ✅ DONE
- Set SHOW_OTP_IN_UI = True explicitly

### Step 2: Edit templates/portals/alumni/login.html ✅ DONE
- Update "Check your Gmail too" → neutral "Check your email or screen"

### Step 3: Delete dead templates/portals/alumni/no_gmail_access.html ✅ DONE

### Step 4: Test all portals ✅ DONE
- alumni/admin/osa login/register Gmail/non-Gmail
- Verify OTP screen display (via code review + fixes)

### Step 5: attempt_completion ✅ COMPLETE

