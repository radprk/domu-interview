"""
Exploratory Data Analysis (EDA) for Domubank Report
This script helps understand the structure, columns, and patterns in the call data.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Load the data
data_file = Path("data/domubank_report_11272025 - Domubankreport.csv")
print("=" * 80)
print("DOMUBANK REPORT - EXPLORATORY DATA ANALYSIS")
print("=" * 80)
print(f"\nLoading data from: {data_file}")

df = pd.read_csv(data_file)

# Remove unnamed columns (empty columns at the end)
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

print(f"\n[OK] Data loaded successfully!")
print(f"\n{'='*80}")
print("1. BASIC INFORMATION")
print("="*80)

print(f"\nDataset Shape:")
print(f"  - Rows: {len(df):,}")
print(f"  - Columns: {len(df.columns)}")

print(f"\nColumn Names:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col}")

print(f"\nData Types:")
print(df.dtypes)

print(f"\n{'='*80}")
print("2. MISSING VALUES ANALYSIS")
print("="*80)

missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)

missing_df = pd.DataFrame({
    'Column': missing.index,
    'Missing Count': missing.values,
    'Missing %': missing_pct.values
})
missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)

if len(missing_df) > 0:
    print("\nColumns with Missing Values:")
    print(missing_df.to_string(index=False))
else:
    print("\n[OK] No missing values found!")

print(f"\n{'='*80}")
print("3. NUMERIC COLUMNS - SUMMARY STATISTICS")
print("="*80)

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if numeric_cols:
    print(f"\nNumeric columns: {', '.join(numeric_cols)}")
    print("\nSummary Statistics:")
    print(df[numeric_cols].describe().round(2))
else:
    print("\nNo numeric columns found.")

print(f"\n{'='*80}")
print("4. CATEGORICAL COLUMNS - VALUE COUNTS")
print("="*80)

categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

for col in categorical_cols:
    unique_count = df[col].nunique()
    print(f"\n{col}:")
    print(f"  - Unique values: {unique_count}")
    
    if unique_count <= 20:
        print(f"  - Value counts:")
        value_counts = df[col].value_counts()
        for val, count in value_counts.items():
            pct = (count / len(df) * 100)
            print(f"    • {val}: {count:,} ({pct:.1f}%)")
    else:
        print(f"  - Top 10 values:")
        value_counts = df[col].value_counts().head(10)
        for val, count in value_counts.items():
            pct = (count / len(df) * 100)
            print(f"    • {val}: {count:,} ({pct:.1f}%)")
        print(f"  - (Showing top 10 of {unique_count} unique values)")

print(f"\n{'='*80}")
print("5. SAMPLE ROWS")
print("="*80)

print("\nFirst 5 rows:")
print(df.head().to_string())

print(f"\n{'='*80}")
print("6. DATA INSIGHTS & INTERPRETATION")
print("="*80)

print("\nWhat Each Row Represents:")
print("  Each row represents a single CALL ATTEMPT to a customer.")
print("  Multiple rows with the same target_id/external_id indicate multiple attempts to reach the same customer.")

print("\nKey Columns Explained:")
print("\n  • loan_number: Unique identifier for each call")
print("  • created_at: When the call was created/scheduled")
print("  • started_at: When the call actually started")
print("  • target_id: Unique identifier for the target/customer")
print("  • external_id: External system identifier for the customer")
print("  • phone_number: Customer's phone number")
print("  • category: Outcome category of the call (e.g., NO_ANSWER, VOICEMAIL, PROMISE_TO_PAY)")
print("  • end_reason: Reason the call ended (e.g., customer-ended-call, silence-timed-out)")
print("  • status: Call status (e.g., picked_up, answered, voicemailed, failed)")
print("  • duration: Call duration in minutes")
print("  • attempt: Attempt number for this target (1st, 2nd, 3rd call, etc.)")
print("  • state: US state where the customer is located")
print("  • recording_url: URL to the call recording")
print("  • transcript: Full text transcript of the call")
print("  • summary: AI-generated summary of the call")

print("\nKey Patterns to Note:")

# Analyze attempt distribution
if 'attempt' in df.columns:
    print(f"\n  Attempt Distribution:")
    attempt_dist = df['attempt'].value_counts().sort_index()
    for attempt, count in attempt_dist.items():
        pct = (count / len(df) * 100)
        print(f"    Attempt #{attempt}: {count:,} calls ({pct:.1f}%)")

# Analyze status distribution
if 'status' in df.columns:
    print(f"\n  Call Status Distribution:")
    status_dist = df['status'].value_counts()
    for status, count in status_dist.items():
        pct = (count / len(df) * 100)
        print(f"    {status}: {count:,} ({pct:.1f}%)")

# Analyze category distribution
if 'category' in df.columns:
    print(f"\n  Call Category Distribution:")
    category_dist = df['category'].value_counts()
    for category, count in category_dist.items():
        pct = (count / len(df) * 100)
        print(f"    {category}: {count:,} ({pct:.1f}%)")

# Analyze promise-related categories
if 'category' in df.columns:
    promise_categories = ['PARTIAL_PAYMENT_ACCEPTED', 'WILLING_TO_PAY', 'PROMISE_TO_PAY']
    promise_calls = df[df['category'].isin(promise_categories)]
    print(f"\n  Promise-Related Calls:")
    print(f"    Total promise calls: {len(promise_calls):,} ({len(promise_calls)/len(df)*100:.2f}%)")
    if len(promise_calls) > 0:
        print(f"    Average attempts to promise: {promise_calls['attempt'].mean():.2f}")
        print(f"    Average duration for promise calls: {promise_calls['duration'].mean():.2f} minutes")

# Analyze duration patterns
if 'duration' in df.columns:
    print(f"\n  Duration Analysis:")
    print(f"    Mean duration: {df['duration'].mean():.2f} minutes")
    print(f"    Median duration: {df['duration'].median():.2f} minutes")
    print(f"    Min duration: {df['duration'].min():.2f} minutes")
    print(f"    Max duration: {df['duration'].max():.2f} minutes")

# Analyze time patterns
if 'started_at' in df.columns:
    df['started_at_dt'] = pd.to_datetime(df['started_at'], errors='coerce')
    df['hour'] = df['started_at_dt'].dt.hour
    df['day_of_week'] = df['started_at_dt'].dt.day_name()
    
    print(f"\n  Time Patterns:")
    print(f"    Date range: {df['started_at_dt'].min()} to {df['started_at_dt'].max()}")
    print(f"    Most active hour: {df['hour'].mode()[0] if len(df['hour'].mode()) > 0 else 'N/A'}")
    print(f"    Most active day: {df['day_of_week'].mode()[0] if len(df['day_of_week'].mode()) > 0 else 'N/A'}")

# Analyze state distribution
if 'state' in df.columns:
    print(f"\n  Top 10 States by Call Volume:")
    state_dist = df['state'].value_counts().head(10)
    for state, count in state_dist.items():
        pct = (count / len(df) * 100)
        print(f"    {state}: {count:,} ({pct:.1f}%)")

# Analyze multiple attempts per target
if 'target_id' in df.columns:
    attempts_per_target = df.groupby('target_id')['attempt'].max()
    print(f"\n  Attempts per Target:")
    print(f"    Unique targets: {df['target_id'].nunique():,}")
    print(f"    Average attempts per target: {attempts_per_target.mean():.2f}")
    print(f"    Max attempts for a single target: {attempts_per_target.max()}")
    print(f"    Targets with 1 attempt: {(attempts_per_target == 1).sum():,}")
    print(f"    Targets with 2+ attempts: {(attempts_per_target > 1).sum():,}")

print(f"\n{'='*80}")
print("7. DATA QUALITY CHECKS")
print("="*80)

# Check for duplicates
duplicate_loan_numbers = df['loan_number'].duplicated().sum()
print(f"\n  Duplicate loan_numbers: {duplicate_loan_numbers}")
if duplicate_loan_numbers > 0:
    print(f"    ⚠️  Warning: Found {duplicate_loan_numbers} duplicate loan numbers!")

# Check for invalid durations
if 'duration' in df.columns:
    invalid_durations = (df['duration'] <= 0).sum()
    print(f"\n  Invalid durations (<= 0): {invalid_durations}")
    if invalid_durations > 0:
        print(f"    ⚠️  Warning: Found {invalid_durations} calls with invalid duration!")

# Check for invalid attempts
if 'attempt' in df.columns:
    invalid_attempts = (df['attempt'] <= 0).sum()
    print(f"\n  Invalid attempts (<= 0): {invalid_attempts}")
    if invalid_attempts > 0:
        print(f"    ⚠️  Warning: Found {invalid_attempts} calls with invalid attempt number!")

# Check date consistency
if 'created_at' in df.columns and 'started_at' in df.columns:
    df['created_at_dt'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['started_at_dt'] = pd.to_datetime(df['started_at'], errors='coerce')
    inconsistent_dates = (df['started_at_dt'] < df['created_at_dt']).sum()
    print(f"\n  Inconsistent dates (started_at < created_at): {inconsistent_dates}")
    if inconsistent_dates > 0:
        print(f"    ⚠️  Warning: Found {inconsistent_dates} calls where started_at is before created_at!")

print(f"\n{'='*80}")
print("8. RECOMMENDATIONS FOR ANALYSIS")
print("="*80)

print("\n  [*] Use 'target_id' or 'external_id' to group calls by customer")
print("  [*] Use 'attempt' to analyze how many attempts it takes to reach a customer")
print("  [*] Use 'category' to identify successful outcomes (promises, payments)")
print("  [*] Use 'duration' to analyze call efficiency and cost")
print("  [*] Use 'started_at' for time-based analysis (hourly, daily patterns)")
print("  [*] Use 'state' for geographic analysis")
print("  [*] Combine 'category' and 'attempt' to calculate 'attempts-to-promise' metric")
print("  [*] Use 'duration' and promise categories to calculate cost savings")

print(f"\n{'='*80}")
print("EDA COMPLETE!")
print("="*80)
print("\nYou can now use this information to build your analysis and visualizations.")

