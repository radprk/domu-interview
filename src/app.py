"""
Domu Bank Call Metrics Dashboard
Streamlit app for analyzing call data from domubank_report_11272025
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# Page config
st.set_page_config(page_title="Domu Bank Call Metrics", layout="wide")

# Constants
DATA_FILE = Path("data/domubank_report_11272025 - Domubankreport.csv")


def load_data(path):
    """Load and clean the CSV data."""
    df = pd.read_csv(path)
    
    # Parse datetimes
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['started_at'] = pd.to_datetime(df['started_at'], errors='coerce')
    
    # Clean duration: numeric seconds, fill NaN with 0
    df['duration'] = pd.to_numeric(df['duration'], errors='coerce').fillna(0)
    
    # Clean attempt: numeric, fill NaN with 1, cast to int
    df['attempt'] = pd.to_numeric(df['attempt'], errors='coerce').fillna(1).astype(int)
    
    # Lowercase string columns for case-insensitive comparisons
    if 'category' in df.columns:
        df['category_lower'] = df['category'].astype(str).str.lower()
    if 'end_reason' in df.columns:
        df['end_reason_lower'] = df['end_reason'].astype(str).str.lower()
    if 'status' in df.columns:
        df['status_lower'] = df['status'].astype(str).str.lower()
    
    return df


def define_events(df):
    """Define event flags based on category and end_reason."""
    # Promise category - includes all three promise types
    promise_categories = ['partial_payment_accepted', 'willing_to_pay', 'promise_to_pay']
    df['promise_category'] = df['category_lower'].isin(promise_categories)
    
    # Forward event (check for both variations)
    df['forward_event'] = df['end_reason_lower'].str.contains('assistant-forward', case=False, na=False)
    
    # Value event
    df['value_event'] = df['promise_category'] | df['forward_event']
    
    # Waste event
    df['waste_event'] = (df['end_reason_lower'] == 'silence-timed-out') | (~df['value_event'])
    
    return df


def apply_filters(df):
    """Apply filters to the dataframe (no sidebar - filters applied at bottom)."""
    # For now, return unfiltered data - filters will be applied at bottom of page
    return df.copy()


def compute_call_level_metrics(df):
    """Compute call-level metrics."""
    if len(df) == 0:
        return {
            'promise_rate': 0.0,
            'qualified_handoff_rate': 0.0,
            'waste_rate': 0.0,
            'total_calls': 0,
            'cost_saved_pct': 0.0,
            'cost_saved_minutes': 0.0
        }
    
    total_calls = len(df)
    
    promise_rate = (df['promise_category'].sum() / total_calls * 100) if total_calls > 0 else 0.0
    qualified_handoff_rate = (df['forward_event'].sum() / total_calls * 100) if total_calls > 0 else 0.0
    waste_rate = (df['waste_event'].sum() / total_calls * 100) if total_calls > 0 else 0.0
    
    # Cost saved: percentage of time NOT spent on waste calls
    # Formula: (total_minutes - waste_minutes) / total_minutes * 100
    total_minutes = df['duration'].sum() / 60.0  # Convert seconds to minutes
    waste_minutes = df[df['waste_event']]['duration'].sum() / 60.0
    cost_saved_pct = ((total_minutes - waste_minutes) / total_minutes * 100) if total_minutes > 0 else 0.0
    cost_saved_minutes = total_minutes - waste_minutes
    
    return {
        'promise_rate': promise_rate,
        'qualified_handoff_rate': qualified_handoff_rate,
        'waste_rate': waste_rate,
        'total_calls': total_calls,
        'cost_saved_pct': cost_saved_pct,
        'cost_saved_minutes': cost_saved_minutes,
        'total_minutes': total_minutes,
        'waste_minutes': waste_minutes
    }


def compute_loan_level_metrics(df):
    """Compute loan-level metrics (attempts-to-value and minutes-to-value)."""
    if len(df) == 0 or 'loan_number' not in df.columns:
        return pd.DataFrame(), {
            'median_attempts_to_value': 0,
            'mean_attempts_to_value': 0.0,
            'p90_attempts_to_value': 0,
            'median_minutes_to_value': 0.0,
            'mean_minutes_to_value': 0.0,
            'p90_minutes_to_value': 0.0
        }
    
    loan_metrics = []
    
    for loan_num, loan_df in df.groupby('loan_number'):
        # Sort by attempt asc, then started_at asc
        loan_df_sorted = loan_df.sort_values(['attempt', 'started_at'], na_position='last').reset_index(drop=True)
        
        # Find first value_event
        value_mask = loan_df_sorted['value_event']
        if value_mask.sum() == 0:
            continue  # Skip loans without value events
        
        # Get the index of the first True value
        first_value_idx = value_mask.idxmax()
        first_value_row = loan_df_sorted.iloc[first_value_idx]
        
        # Attempts to value
        attempts_to_value = first_value_row['attempt']
        
        # Minutes to value: sum duration from first call up to and including first value event
        rows_up_to_value = loan_df_sorted.iloc[:first_value_idx + 1]
        seconds_to_value = rows_up_to_value['duration'].sum()
        minutes_to_value = seconds_to_value / 60.0
        
        loan_metrics.append({
            'loan_number': loan_num,
            'attempts_to_value': attempts_to_value,
            'minutes_to_value': minutes_to_value
        })
    
    if len(loan_metrics) == 0:
        return pd.DataFrame(), {
            'median_attempts_to_value': 0,
            'mean_attempts_to_value': 0.0,
            'p90_attempts_to_value': 0,
            'median_minutes_to_value': 0.0,
            'mean_minutes_to_value': 0.0,
            'p90_minutes_to_value': 0.0
        }
    
    loan_metrics_df = pd.DataFrame(loan_metrics)
    
    stats = {
        'median_attempts_to_value': int(loan_metrics_df['attempts_to_value'].median()),
        'mean_attempts_to_value': loan_metrics_df['attempts_to_value'].mean(),
        'p90_attempts_to_value': int(loan_metrics_df['attempts_to_value'].quantile(0.9)),
        'median_minutes_to_value': loan_metrics_df['minutes_to_value'].median(),
        'mean_minutes_to_value': loan_metrics_df['minutes_to_value'].mean(),
        'p90_minutes_to_value': loan_metrics_df['minutes_to_value'].quantile(0.9)
    }
    
    return loan_metrics_df, stats


def plot_value_event_by_attempt(df):
    """Interactive bar chart: value_event rate by attempt number."""
    if len(df) == 0 or 'attempt' not in df.columns:
        return None
    
    attempt_stats = df.groupby('attempt').agg(
        total=('value_event', 'count'),
        value_count=('value_event', 'sum')
    ).reset_index()
    
    attempt_stats['value_rate'] = (attempt_stats['value_count'] / attempt_stats['total'] * 100)
    
    fig = px.bar(
        attempt_stats,
        x='attempt',
        y='value_rate',
        title='Value Event Rate by Attempt Number',
        labels={'attempt': 'Attempt Number', 'value_rate': 'Value Event Rate (%)'},
        text='value_rate',
        text_auto='.1f'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        height=400,
        showlegend=False
    )
    return fig


def plot_minutes_to_value_distribution(loan_metrics_df):
    """Interactive histogram: minutes_to_value distribution."""
    if len(loan_metrics_df) == 0 or 'minutes_to_value' not in loan_metrics_df.columns:
        return None
    
    fig = px.histogram(
        loan_metrics_df,
        x='minutes_to_value',
        nbins=30,
        title='Distribution of Minutes to Value (Loan-level)',
        labels={'minutes_to_value': 'Minutes to Value', 'count': 'Frequency'},
        height=400
    )
    fig.update_layout(showlegend=False)
    return fig


def plot_promise_breakdown(df):
    """Interactive pie chart showing promise category breakdown."""
    if len(df) == 0 or 'promise_category' not in df.columns:
        return None
    
    promise_calls = df[df['promise_category'] == True]
    if len(promise_calls) == 0:
        return None
    
    category_counts = promise_calls['category'].value_counts()
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title='Promise Category Breakdown',
        height=400
    )
    return fig


def plot_attempts_to_value_distribution(loan_metrics_df):
    """Interactive histogram: attempts_to_value distribution."""
    if len(loan_metrics_df) == 0 or 'attempts_to_value' not in loan_metrics_df.columns:
        return None
    
    fig = px.histogram(
        loan_metrics_df,
        x='attempts_to_value',
        nbins=20,
        title='Distribution of Attempts to Value (Loan-level)',
        labels={'attempts_to_value': 'Attempts to Value', 'count': 'Frequency'},
        height=400
    )
    fig.update_layout(
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),
        showlegend=False
    )
    return fig


def plot_metrics_over_time(df):
    """Line chart showing promise rate and value event rate over time."""
    if len(df) == 0 or 'started_at' not in df.columns:
        return None
    
    df_time = df[df['started_at'].notna()].copy()
    if len(df_time) == 0:
        return None
    
    df_time['date'] = df_time['started_at'].dt.date
    daily_stats = df_time.groupby('date').agg(
        total=('value_event', 'count'),
        promise_count=('promise_category', 'sum'),
        value_count=('value_event', 'sum')
    ).reset_index()
    
    daily_stats['promise_rate'] = (daily_stats['promise_count'] / daily_stats['total'] * 100)
    daily_stats['value_rate'] = (daily_stats['value_count'] / daily_stats['total'] * 100)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_stats['date'],
        y=daily_stats['promise_rate'],
        mode='lines+markers',
        name='Promise Rate (%)',
        line=dict(width=2)
    ))
    fig.add_trace(go.Scatter(
        x=daily_stats['date'],
        y=daily_stats['value_rate'],
        mode='lines+markers',
        name='Value Event Rate (%)',
        line=dict(width=2)
    ))
    fig.update_layout(
        title='Promise Rate and Value Event Rate Over Time',
        xaxis_title='Date',
        yaxis_title='Rate (%)',
        height=400,
        hovermode='x unified'
    )
    return fig


# Main app
st.title("Domu Bank Call Metrics")

# Load data
if not DATA_FILE.exists():
    st.error(f"Data file not found: {DATA_FILE}")
    st.stop()

try:
    df = load_data(DATA_FILE)
    df = define_events(df)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# No sidebar - use all data
df_filtered = apply_filters(df)

# Check if data is empty
if len(df_filtered) == 0:
    st.warning("No data available.")
    st.stop()

# Compute metrics
call_metrics = compute_call_level_metrics(df_filtered)
loan_metrics_df, loan_stats = compute_loan_level_metrics(df_filtered)

# Metric Definitions Section
with st.expander("📖 Metric Definitions & Calculations", expanded=False):
    st.markdown("""
    ### **Value Event**
    A **Value Event** represents a call that resulted in a meaningful outcome:
    - **Promise Category**: Customer committed to payment (PARTIAL_PAYMENT_ACCEPTED, WILLING_TO_PAY, PROMISE_TO_PAY)
    - **Forward Event**: Call was forwarded to a human agent (assistant-forwarded-call)
    
    *Value events indicate high customer intent and successful engagement.*
    
    ### **Promise Rate**
    **Definition**: Percentage of calls where the customer made a payment promise.
    
    **Calculation**: 
    ```
    Promise Rate = (Number of calls with promise categories) / Total calls × 100%
    ```
    
    **Promise Categories**: 
    - `PARTIAL_PAYMENT_ACCEPTED`: Customer agreed to make a partial payment
    - `WILLING_TO_PAY`: Customer expressed willingness to pay
    - `PROMISE_TO_PAY`: Customer made a promise to pay
    
    **What it signifies**: Higher promise rates indicate better customer engagement and higher likelihood of payment collection.
    
    ### **Qualified Handoff Rate**
    **Definition**: Percentage of calls that were forwarded to a human agent.
    
    **Calculation**:
    ```
    Qualified Handoff Rate = (Number of forwarded calls) / Total calls × 100%
    ```
    
    **Forward Event**: `end_reason == "assistant-forwarded-call"`
    
    **What it signifies**: These calls represent high-intent customers who need human assistance. This is a GOOD outcome, not a failure.
    
    ### **Non-Value Rate**
    **Definition**: Percentage of calls that resulted in no value outcome.
    
    **Calculation**:
    ```
    Non-Value Rate = (Number of non-value events) / Total calls × 100%
    ```
    
    **Non-Value Events Include**:
    - Calls ending with `silence-timed-out` (no response from customer)
    - Calls that are NOT value events (no promise, no forward)
    
    **What it signifies**: Lower non-value rates indicate more efficient use of call resources and better customer engagement.
    
    ### **Cost Saved**
    **Definition**: Percentage of call time that was spent on productive calls (value events).
    
    **Calculation**:
    ```
    Cost Saved % = (Total minutes - Non-Value minutes) / Total minutes × 100%
    Cost Saved (minutes) = Total minutes - Non-Value minutes
    ```
    
    **What it signifies**: Higher cost saved means more time spent on productive calls (value events) rather than non-value calls.
    
    ### **Attempts-to-Value**
    **Definition**: Number of call attempts required before achieving a value event (at the loan level).
    
    **Calculation**:
    - For each loan, find the first call with a value event
    - Count which attempt number that was
    - Report median, mean, and 90th percentile across all loans
    
    **What it signifies**: Lower attempts-to-value means customers are engaging sooner, indicating better targeting and messaging.
    
    ### **Minutes-to-Value**
    **Definition**: Total call duration (in minutes) from the first call attempt until achieving a value event (at the loan level).
    
    **Calculation**:
    - For each loan, sum the duration of all calls from attempt 1 up to and including the first value event
    - Convert seconds to minutes
    - Report median, mean, and 90th percentile across all loans
    
    **What it signifies**: Lower minutes-to-value means faster resolution and lower operational costs per successful outcome.
    """)

# Display all metrics in one view with expandable details
st.header("📊 All Metrics")

# Row 1: First 3 metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Promise Rate", f"{call_metrics['promise_rate']:.2f}%")
    with st.expander("📖 Details & Explanation"):
        st.info("""
        **Definition**: Percentage of calls where the customer made a payment promise.
        
        **Calculation**: Promise Rate = (Calls with promise categories) / Total calls × 100%
        
        **Promise Categories**: 
        - `PARTIAL_PAYMENT_ACCEPTED`: Customer agreed to make a partial payment
        - `WILLING_TO_PAY`: Customer expressed willingness to pay
        - `PROMISE_TO_PAY`: Customer made a promise to pay
        
        **Significance**: Higher rates indicate better customer engagement and higher payment collection likelihood.
        """)
        promise_calls = df_filtered[df_filtered['promise_category'] == True]
        total_calls = len(df_filtered)
        st.write(f"**Promise Calls:** {len(promise_calls):,} / {total_calls:,}")
        if len(promise_calls) > 0:
            st.write("\n**Breakdown by Category:**")
            category_breakdown = promise_calls['category'].value_counts()
            for cat, count in category_breakdown.items():
                pct = (count / len(promise_calls) * 100)
                st.write(f"- {cat}: {count} ({pct:.1f}%)")
            fig_promise = plot_promise_breakdown(df_filtered)
            if fig_promise:
                st.plotly_chart(fig_promise, use_container_width=True)

with col2:
    st.metric("Qualified Handoff Rate", f"{call_metrics['qualified_handoff_rate']:.2f}%")
    with st.expander("📖 Details & Explanation"):
        st.info("""
        **Definition**: Percentage of calls forwarded to a human agent.
        
        **Calculation**: Qualified Handoff Rate = (Forwarded calls) / Total calls × 100%
        
        **Forward Event**: end_reason == "assistant-forwarded-call"
        
        **Significance**: These represent high-intent customers needing human assistance. This is a GOOD outcome, indicating successful qualification.
        """)
        forward_calls = df_filtered[df_filtered['forward_event'] == True]
        total_calls = len(df_filtered)
        st.write(f"**Forwarded Calls:** {len(forward_calls):,} / {total_calls:,}")
        if len(forward_calls) > 0:
            st.write(f"\n**Average Duration:** {forward_calls['duration'].mean() / 60:.2f} minutes")
            st.write(f"**Average Attempt:** {forward_calls['attempt'].mean():.2f}")
            forward_by_attempt = forward_calls.groupby('attempt').size().reset_index(name='count')
            fig = px.bar(
                forward_by_attempt,
                x='attempt',
                y='count',
                title='Forwarded Calls by Attempt Number',
                labels={'attempt': 'Attempt Number', 'count': 'Number of Calls'},
                height=300
            )
            fig.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
            st.plotly_chart(fig, use_container_width=True)

with col3:
    st.metric("Non-Value Rate", f"{call_metrics['waste_rate']:.2f}%")
    with st.expander("📖 Details & Explanation"):
        st.warning("""
        **Definition**: Percentage of calls that resulted in no value outcome.
        
        **Calculation**: Non-Value Rate = (Number of non-value events) / Total calls × 100%
        
        **Non-Value Events Include**:
        - Calls ending with `silence-timed-out` (no customer response)
        - Calls that are NOT value events (no promise made, no forward to agent)
        
        **Significance**: Lower non-value rates indicate more efficient use of call resources and better customer engagement.
        """)
        non_value_calls = df_filtered[df_filtered['waste_event'] == True]
        total_calls = len(df_filtered)
        st.write(f"**Non-Value Calls:** {len(non_value_calls):,} / {total_calls:,}")
        if len(non_value_calls) > 0:
            st.write(f"\n**Total Non-Value Time:** {call_metrics['waste_minutes']:.1f} minutes")
            st.write(f"**Average Non-Value Call Duration:** {non_value_calls['duration'].mean() / 60:.2f} minutes")
            st.write("\n**Top Non-Value Reasons:**")
            non_value_reasons = non_value_calls['end_reason'].value_counts().head(5)
            for reason, count in non_value_reasons.items():
                pct = (count / len(non_value_calls) * 100)
                st.write(f"- {reason}: {count} ({pct:.1f}%)")
            non_value_reasons_chart = non_value_calls['end_reason'].value_counts().head(10)
            fig = px.bar(
                x=non_value_reasons_chart.values,
                y=non_value_reasons_chart.index,
                orientation='h',
                title='Top Non-Value Reasons',
                labels={'x': 'Count', 'y': 'End Reason'},
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

# Row 2: Next 3 metrics
col4, col5, col6 = st.columns(3)

with col4:
    st.metric("Cost Saved", f"{call_metrics['cost_saved_pct']:.2f}%")
    with st.expander("📖 Details & Explanation"):
        st.success("""
        **Definition**: Percentage of call time that was spent on productive calls (value events).
        
        **Calculation**: 
        - Cost Saved % = (Total minutes - Non-Value minutes) / Total minutes × 100%
        - Cost Saved (minutes) = Total minutes - Non-Value minutes
        
        **What it means**: This represents the time spent on productive calls (value events) vs. non-value calls.
        
        **Significance**: Higher cost saved means more time invested in calls that result in promises or qualified handoffs, leading to better ROI.
        """)
        st.write(f"**Cost Saved (Minutes):** {call_metrics['cost_saved_minutes']:.1f}")
        st.write(f"**Total Call Time:** {call_metrics['total_minutes']:.1f} minutes")
        st.write(f"**Non-Value Time:** {call_metrics['waste_minutes']:.1f} minutes")
        st.write(f"**Productive Time:** {call_metrics['cost_saved_minutes']:.1f} minutes")
        if call_metrics['total_minutes'] > 0:
            productive_pct = (call_metrics['cost_saved_minutes'] / call_metrics['total_minutes'] * 100)
            st.write(f"\n**Productive Time %:** {productive_pct:.1f}%")
            time_data = {
                'Category': ['Productive Time', 'Non-Value Time'],
                'Minutes': [call_metrics['cost_saved_minutes'], call_metrics['waste_minutes']]
            }
            time_df = pd.DataFrame(time_data)
            fig = px.pie(
                time_df,
                values='Minutes',
                names='Category',
                title='Time Distribution: Productive vs Non-Value',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

with col5:
    st.metric("Median Attempts-to-Value", loan_stats['median_attempts_to_value'])
    with st.expander("📖 Details & Explanation"):
        st.info("""
        **Definition**: Number of call attempts required before achieving a value event (calculated at the loan level).
        
        **Calculation**:
        1. For each loan, sort calls by attempt number (ascending), then by started_at (ascending)
        2. Find the first call with a value event (promise or forward)
        3. Record the attempt number of that call
        4. Report median, mean, and 90th percentile across all loans
        
        **Significance**: Lower attempts-to-value means customers are engaging sooner, indicating better targeting, messaging, and customer readiness.
        """)
        st.write(f"**Mean:** {loan_stats['mean_attempts_to_value']:.2f}")
        st.write(f"**90th Percentile:** {loan_stats['p90_attempts_to_value']}")
        if len(loan_metrics_df) > 0:
            st.write(f"\n**Loans with Value Events:** {len(loan_metrics_df):,}")
            st.write(f"**Range:** {loan_metrics_df['attempts_to_value'].min()} - {loan_metrics_df['attempts_to_value'].max()}")
            fig_attempts = plot_attempts_to_value_distribution(loan_metrics_df)
            if fig_attempts:
                st.plotly_chart(fig_attempts, use_container_width=True)

with col6:
    st.metric("Median Minutes-to-Value", f"{loan_stats['median_minutes_to_value']:.2f}")
    with st.expander("📖 Details & Explanation"):
        st.info("""
        **Definition**: Total call duration (in minutes) from the first call attempt until achieving a value event (calculated at the loan level).
        
        **Calculation**:
        1. For each loan, sort calls by attempt number (ascending), then by started_at (ascending)
        2. Find the first call with a value event (promise or forward)
        3. Sum the duration (in seconds) of all calls from attempt 1 up to and including the first value event
        4. Convert to minutes: seconds_to_value / 60
        5. Report median, mean, and 90th percentile across all loans
        
        **Significance**: Lower minutes-to-value means faster resolution and lower operational costs per successful outcome. This directly impacts cost efficiency.
        """)
        st.write(f"**Mean:** {loan_stats['mean_minutes_to_value']:.2f} minutes")
        st.write(f"**90th Percentile:** {loan_stats['p90_minutes_to_value']:.2f} minutes")
        if len(loan_metrics_df) > 0:
            total_hours = loan_metrics_df['minutes_to_value'].sum() / 60
            st.write(f"\n**Total Time to Value:** {total_hours:.1f} hours")
            st.write(f"**Range:** {loan_metrics_df['minutes_to_value'].min():.2f} - {loan_metrics_df['minutes_to_value'].max():.2f} minutes")
            fig_minutes = plot_minutes_to_value_distribution(loan_metrics_df)
            if fig_minutes:
                st.plotly_chart(fig_minutes, use_container_width=True)


# Interactive Charts Section
st.header("📈 Interactive Charts")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Value Event Rate by Attempt")
    fig1 = plot_value_event_by_attempt(df_filtered)
    if fig1:
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Metrics Over Time")
    fig_time = plot_metrics_over_time(df_filtered)
    if fig_time:
        st.plotly_chart(fig_time, use_container_width=True)

# Table: Top end_reason by count and % share
st.header("Top End Reasons")
if 'end_reason' in df_filtered.columns:
    end_reason_stats = df_filtered['end_reason'].value_counts().reset_index()
    end_reason_stats.columns = ['End Reason', 'Count']
    end_reason_stats['Share %'] = (end_reason_stats['Count'] / len(df_filtered) * 100).round(2)
    st.dataframe(end_reason_stats, use_container_width=True)

# Data Explorer
st.header("Data Explorer")
st.dataframe(df_filtered, use_container_width=True)

# Download button
csv = df_filtered.to_csv(index=False)
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)

# Filter Information at the bottom
st.divider()
st.header("ℹ️ Data Information & Quality")

with st.expander("Data Overview & Quality Notes", expanded=False):
    st.write(f"**File:** {DATA_FILE.name}")
    st.write(f"**Total Rows Loaded:** {len(df):,}")
    st.write(f"**Rows After Filters:** {len(df_filtered):,}")
    
    st.write("\n**Data Quality Notes:**")
    if 'started_at' in df.columns:
        valid_dates = df['started_at'].notna().sum()
        missing_dates = df['started_at'].isna().sum()
        st.write(f"- **Rows with `started_at` dates:** {valid_dates:,} ({valid_dates/len(df)*100:.1f}%)")
        st.write(f"- **Rows with missing `started_at`:** {missing_dates:,} ({missing_dates/len(df)*100:.1f}%)")
    
    if 'duration' in df.columns:
        missing_duration = df['duration'].isna().sum()
        if missing_duration > 0:
            st.write(f"- **Rows with missing `duration`:** {missing_duration:,} (filled with 0)")
    
    if 'category' in df.columns:
        missing_category = df['category'].isna().sum()
        if missing_category > 0:
            st.write(f"- **Rows with missing `category`:** {missing_category:,}")
    
    st.write("\n**Note:** Currently showing all data. No filters are applied.")
