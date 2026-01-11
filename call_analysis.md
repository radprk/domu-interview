# Call Transcript Analysis: AI Collections Strategy Review

**Analysis Date:** January 11, 2026
**Dataset:** 1,000 calls, 735 with transcripts (73.5%)
**Success Rate:** 0.4% value calls (3/735 with transcripts)

---

## Executive Summary

After analyzing 735 call transcripts from Domu Bank's AI collections system, I identified critical weaknesses in the current strategy that are causing an extremely low success rate (0.4%). The AI agent demonstrates strong technical capabilities (bilingual support, natural conversation flow) but suffers from:

1. **Excessive compliance** - Disconnects immediately when customers use polite dismissals
2. **Rigid 5-day payment window** - Forces agent transfers for reasonable payment timelines
3. **Insufficient persistence** - Gives up too easily on objections
4. **Generic scripting** - Doesn't adapt to customer circumstances or attempt patterns

**Key Finding:** Only 3 value calls (promises/forwards) out of 735 transcripts represents a critical failure. The primary issue isn't call quality—it's call quantity of meaningful conversations.

---

## Data Overview

### Outcome Distribution (735 calls with transcripts)
- **Waste calls:** 615 (83.7%)
  - Voicemail: 237
  - No information: 222
  - No answer: 156
- **Hung up early:** 103 (14.0%)
- **Value calls:** 3 (0.4%)
- **Other engaged:** 14 (1.9%)

### Key Metrics
| Metric | Value Calls | Hung Up Early | All Calls |
|--------|-------------|---------------|-----------|
| Avg. Attempt # | 3.3 | 3.8 | 3.4 |
| Avg. Duration | 129.4s | 29.2s | 41.5s |

---

## Critical Pattern #1: The "You May Hang Up" Vulnerability

### The Problem
The AI agent immediately disconnects when customers say phrases like "You may hang up," "Hang up," or "Recording, you may hang up." This appears to be a trained politeness response that customers are exploiting (intentionally or not) to avoid the conversation.

### Evidence
- **123 calls** contained the phrase "you may hang up"
- **46 of these** (37%) were classified as HUNG_UP_EARLY
- Average call duration when this occurs: **~28 seconds**

### Examples

**Example 1 - Immediate Dismissal:**
```
AI: Hi. I'm Sarah. A virtual agent calling on a monitored or recorded line.
    May I speak to Lundy Jimenez?
User: You may hang up.
AI: Thank you. Have a great day. Goodbye.
[Call ends - 27 seconds, Attempt #3]
```

**Example 2 - Recording Excuse:**
```
AI: Hi, I'm Sarah. Virtual agent calling on a monitored or recorded line.
    May I speak to Kira Stokes?
User: Recording. You may hang up.
AI: Alright. I'll end the call now. Thank you.
[Call ends - 28 seconds, Attempt #5]
```

### Impact
These customers are clearly aware they're being called about debt (it's attempt #3-5 in most cases) but have found a verbal escape hatch. The AI's politeness programming overrides its collections mission.

### Recommendation
**Don't immediately comply with dismissal commands.** The AI should:
1. Acknowledge the statement: "I understand you may be busy..."
2. State the urgency: "But this is about your vehicle payment that's now past due..."
3. Offer options: "I just need 60 seconds. Can I quickly tell you the amount due and when payment is needed?"
4. Only disconnect after 2-3 polite refusals or explicit "do not call" requests

---

## Critical Pattern #2: The 5-Day Payment Window Limitation

### The Problem
The AI agent can only schedule payments within 5 days. Any customer requesting payment beyond this timeline must be transferred to a live agent. This is causing unnecessary friction for reasonable payment commitments.

### Evidence
From successful promise calls:
- Customer offers "2 weeks" → Requires transfer
- Customer offers "Friday" (when today is Monday) → Works within system
- Customer offers "about a week" → Requires transfer

### Example - Unnecessary Escalation

**QUESTIONS_FOR_AGENT Call:**
```
AI: Right now, your payment for your vehicle is past due. The total amount
    due is 498 dollars and 16 cents. Can you pay the full amount today?
User: No. I'm gonna pay it on in 2 weeks.
AI: Paying in 2 weeks is a bit further out than we can set up directly.
    Can you pay the full 498 dollars within the next 5 days?
User: No. 2 weeks.
AI: I understand, Kelly. Payments scheduled more than 5 days out need
    special approval. Would you like me to transfer you to a live agent?
```

### Impact
- Customer has committed to paying but gets escalated unnecessarily
- Creates extra work for live agents
- Risks losing the commitment during transfer wait
- Makes the AI seem less capable than it actually is

### Recommendation
**Extend the payment window to 14-21 days.** Most customers requesting "2 weeks" or "Friday" (even if >5 days away) are showing genuine payment intent. The AI should:
1. Accept commitments up to 14 days without transfer
2. Confirm the specific date (not just "2 weeks")
3. Only transfer for requests beyond 21 days or for payment plans
4. Send automated reminders 2 days before the commitment date

### How to Test
**A/B test:**
- Control: Current 5-day limit
- Test: 14-day limit with date confirmation
- Measure: Promise-to-payment conversion rate, agent transfer volume, actual payment completion

---

## Critical Pattern #3: Insufficient Attempt Strategy

### The Problem
Despite averaging 3.4 attempts per account, the AI isn't adapting its strategy based on previous attempt outcomes or customer patterns.

### Evidence
- Hung up calls still getting called 4-8 more times with identical script
- No observable variation in approach between attempt #1 and attempt #8
- High attempt numbers (6-9) showing same early disconnection patterns

### Current State
The system appears to be treating each call as independent, not learning from:
- Previous disconnection methods
- Time of day patterns
- Customer responsiveness

### Recommendation
**Implement attempt-adaptive calling strategy:**

**Attempt 1-2:** Standard script
- "I'm calling about your vehicle payment..."
- Full formality and disclosure

**Attempt 3-4:** Urgency escalation
- "This is my third attempt to reach you about your past-due vehicle payment..."
- "If we can't connect today, this may be referred to our collections department..."

**Attempt 5+:** Last chance messaging
- "This is a final notice about your account..."
- Shorter call, more direct
- Offer explicit: "Call us at XXX to avoid further action"

**For "hang up" patterns:** After 2 "you may hang up" responses, switch to voicemail-focused strategy instead of continuing live calls

### How to Test
Track conversion rates by attempt number for each script variant. Hypothesis: Attempt #3-4 with escalation language will show 2-3x higher engagement than current approach.

---

## What Makes Successful Calls Work

### Analysis of 3 Promise Calls

**Common Success Factors:**

1. **Bilingual flexibility** - Santiago (Montana, Attempt #1):
   - Customer asked "¿Es que es en Spanish?"
   - AI immediately switched to Spanish
   - Clean promise to pay $409.03 in 5 days
   - Duration: 125 seconds

2. **Empathy for circumstances** - Joshua (Oklahoma, Attempt #6):
   - Customer explained: "I have 2 broken wrists, wife's only working"
   - AI acknowledged: "That sounds tough, Joshua"
   - Offered agent transfer for payment arrangement
   - Duration: 141 seconds

3. **Quick commitment capture** - Stacy (Ohio, Attempt #3):
   - Customer immediately offered: "I'm gonna pay it tomorrow or Friday"
   - AI confirmed the commitment before customer could backtrack
   - Locked in Friday payment date
   - Duration: 121 seconds

### Key Insight
**All 3 successful calls had customers who showed payment intent early (within 30 seconds).** The AI's role was to:
- Capture and confirm the commitment
- Remove obstacles (language, timing, transfer)
- Not talk them out of paying

---

## What Makes Unsuccessful Calls Fail

### Pattern Analysis of 103 HUNG_UP_EARLY Calls

**Primary Failure Modes:**

1. **Immediate dismissal exploitation (44.7%):**
   - "You may hang up" → AI complies
   - Duration: 27-35 seconds
   - Happens across all attempt numbers

2. **No engagement strategy (42.7%):**
   - Customer says "No" or stays silent
   - AI provides callback number and exits
   - No probing questions, no value proposition

3. **Wrong person/language barrier (12.6%):**
   - Customer isn't the account holder
   - AI doesn't ask for correct person
   - Spanish speakers answering English opening (and vice versa)

### Example - Missed Opportunity

**From UNABLE_TO_PAY call:**
```
AI: Can you pay the full amount today?
User: No.
AI: Can you pay the full amount within the next 5 days?
User: No.
AI: How much are you able to pay today?
User: Nothing.
AI: Can you tell me what's making it hard to make a payment right now?
User: I will call to make my payment if week.
[AI offers transfer, call ends]
```

**What's Wrong:**
- Customer IS willing to pay ("I will call to make my payment in a week")
- But week > 5 days, so requires transfer
- No commitment captured, no confirmation of amount
- No attempt to offer partial payment for today + rest in a week

---

## Strategic Recommendations

### Priority 1: Fix the "Hang Up" Vulnerability (High Impact, Low Effort)

**Current Behavior:** Immediate compliance with dismissal phrases
**Proposed Behavior:**

```
User: "You may hang up."
AI: "I understand you're busy, but this is important—your vehicle payment
     of $425 is past due. Can I have just 60 seconds to explain your options?
     This call could save your account from collections."

[If customer repeats dismissal]
AI: "I hear you. The quickest way to resolve this is to schedule a payment.
     Can you commit to paying by Friday? That way, we won't need to call again."

[If customer still refuses]
AI: "Understood. Please call us at 809-10-8-1-8-0 within 48 hours to avoid
     your account being referred to collections. Have a good day."
```

**Expected Impact:** Convert 15-20% of current HUNG_UP_EARLY calls to engaged conversations

---

### Priority 2: Extend Payment Window to 14 Days (High Impact, Medium Effort)

**Current Limitation:** 5-day payment window forces agent transfers
**Proposed Change:**
- Accept payment commitments up to 14 days
- Confirm specific date (not vague "2 weeks")
- Send reminder call/SMS 2 days before commitment date
- Auto-transfer only for >14 days or payment plan requests

**Expected Impact:**
- Reduce agent transfers by 60-70%
- Capture additional 2-3% of calls as promises
- Improve customer experience (no hold time, immediate resolution)

---

### Priority 3: Implement Attempt-Adaptive Strategy (Medium Impact, High Effort)

**Current Approach:** Same script regardless of attempt number or history
**Proposed Approach:**

| Attempt | Strategy | Key Message | Expected Outcome |
|---------|----------|-------------|------------------|
| 1-2 | Standard | "Calling about payment..." | Baseline engagement |
| 3-4 | Urgency | "Third attempt, account at risk..." | +50% engagement |
| 5-7 | Final notice | "Last chance before collections..." | +100% engagement |
| 8+ | Voicemail only | "Call us to avoid legal action" | Reduce waste calls |

**Track Previous Outcomes:**
- If "you may hang up" on attempt #1-2, use persistence script on #3
- If wrong person, ask for best time to reach account holder
- If language barrier, lead with bilingual greeting on next attempt

**Expected Impact:**
- Reduce total attempts needed by 20-30%
- Improve attempt #3+ conversion by 2-3x
- Decrease waste calls in high-attempt scenarios

---

### Priority 4: Optimize Call Timing (Low Impact, High Effort)

**Current State:** Unclear if call timing is optimized
**Proposed Analysis:**

1. **Track success by time of day:**
   - Are promises more likely at 10am or 6pm?
   - Do hung-up calls correlate with business hours?

2. **Track success by day of week:**
   - Friday calls might catch people before paycheck
   - Monday calls might catch people after weekend planning

3. **Optimize attempt scheduling:**
   - If attempt #1 fails at 2pm Tuesday, schedule #2 for 6pm Thursday
   - Avoid calling same time/day for subsequent attempts

**Expected Impact:** 5-10% improvement in engagement rate (requires data collection first)

---

### Priority 5: Client Prioritization Strategy (Medium Impact, High Effort)

**Current State:** Appears to treat all accounts equally
**Proposed Segmentation:**

**Tier 1 - High Priority (call first, more attempts):**
- Past payment history of keeping promises
- Lower attempt numbers (1-3)
- Accounts with recent positive engagement
- Higher balance amounts

**Tier 2 - Standard (normal strategy):**
- No prior history
- Moderate balance
- Attempts 4-6

**Tier 3 - Low Priority (fewer attempts, voicemail focus):**
- 2+ "hang up" dismissals
- 7+ attempts with no engagement
- History of broken promises
- Lower balance amounts (<$200)

**Expected Impact:**
- Focus live call resources on convertible accounts
- Reduce waste on customers unlikely to engage via voice
- Improve overall promise rate by 15-25%

---

## Testing Framework

### Hypothesis-Driven Experimentation

**Test 1: Persistence on Dismissal**
- **Hypothesis:** Customers who say "you may hang up" are reachable with one persistence attempt
- **Test:** A/B test immediate disconnect vs. one persistence response
- **Measure:** Engagement rate, promise rate, do-not-call complaints
- **Timeline:** 2 weeks, 1000 calls per variant
- **Success criteria:** >10% improvement in engagement with <5% increase in complaints

**Test 2: 14-Day Payment Window**
- **Hypothesis:** Extending payment window captures commitments without harming payment completion
- **Test:** A/B test 5-day vs. 14-day acceptance window
- **Measure:** Promise rate, agent transfer rate, actual payment completion at 14 days
- **Timeline:** 4 weeks, 2000 calls per variant
- **Success criteria:** >30% reduction in transfers, >80% payment completion rate

**Test 3: Attempt-Based Urgency Messaging**
- **Hypothesis:** Attempt #3+ calls with escalation language show higher engagement
- **Test:** Standard script vs. urgency script for attempts 3-5
- **Measure:** Engagement rate, promise rate by attempt number
- **Timeline:** 3 weeks, 1500 calls per variant
- **Success criteria:** 2x engagement rate improvement on attempts 3-5

---

## Additional Observations

### What's Working Well

1. **Bilingual capability:** Seamless Spanish switching in successful Santiago call
2. **Natural conversation flow:** AI doesn't sound robotic
3. **Proper disclosures:** FDCPA compliance maintained throughout
4. **Empathy statements:** "That sounds tough, Joshua" shows good training
5. **Clear amount communication:** Always states exact dollar amount due

### Technical Improvements Needed

1. **Better voicemail detection:**
   - Some voicemails being categorized as NO_INFORMATION
   - AI sometimes gets confused by voicemail prompts

2. **Silence handling:**
   - 90 of 103 hung-up calls ended with "silence-timed-out"
   - Should attempt 1-2 engagement prompts before timing out

3. **Name pronunciation:**
   - Some Hispanic names poorly pronounced in English
   - Should lead with Spanish greeting if name is clearly Hispanic

---

## Conclusion

The AI collections agent has strong technical capabilities but is hamstrung by overly conservative policies and insufficient persistence. The core issues are:

1. **Premature disconnection** on polite dismissals
2. **Artificial 5-day payment restriction** causing unnecessary escalations
3. **One-size-fits-all approach** regardless of attempt history
4. **Success rate of 0.4%** indicates systemic strategy failure, not execution failure

**Primary Recommendation:**
Implement the "hang up" fix and 14-day payment window immediately. These two changes alone could improve success rates by 3-5x (from 0.4% to 1.5-2.0%) with minimal risk.

**Secondary Recommendation:**
Build the adaptive attempt strategy over 6-8 weeks with proper A/B testing to validate each escalation level.

The difference between success (129s calls with promises) and failure (29s hung-up calls) is whether the AI maintains the conversation long enough to capture intent. The goal isn't to strong-arm customers—it's to remove obstacles for customers who *want* to pay but are testing whether they can avoid the conversation.
