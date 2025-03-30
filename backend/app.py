from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from pyxirr import xirr
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# -------------------------------
# Load and clean CSV data
# -------------------------------

# Read CSVs
lp_lookup = pd.read_csv('data/tbLPLookup.csv')
lp_fund = pd.read_csv('data/tbLPFund.csv')
pcap = pd.read_csv('data/tbPCAP.csv')
ledger = pd.read_csv('data/tbLedger.csv')

# Normalize column naming
lp_lookup = lp_lookup.rename(columns={"Active": "Status"})
lp_lookup["Status"] = lp_lookup["Status"].map({1: "Active", 0: "Not Active"})
lp_fund = lp_fund.rename(columns={"Reinvest Start": "Reinvestment Start", "Incentive": "Incentive Fee"})

# Clean numeric + datetime fields
pcap['Amount'] = pcap['Amount'].astype(str).str.replace(',', '').astype(float)
ledger['Amount'] = ledger['Amount'].astype(str).str.replace(',', '').astype(float)
ledger['Activity Date'] = pd.to_datetime(ledger['Activity Date'])
pcap['PCAP Date'] = pd.to_datetime(pcap['PCAP Date'])

# -------------------------------
# API Endpoint: List all LPs
# -------------------------------
@app.route('/api/lps')
def get_lps():
    """Returns a list of all LP short names."""
    return jsonify(lp_lookup['LP Short Name'].dropna().unique().tolist())


# -------------------------------
# API Endpoint: Get details for an individual LP
# -------------------------------
@app.route('/api/lp/<lp_short_name>')
def get_lp_data(lp_short_name):
    """Returns fund info, summary metrics, and IRR for a given LP as of a report date."""

    # Parse report date from query param, default to today
    report_date = request.args.get('report_date', datetime.today().strftime('%Y-%m-%d'))
    report_date = pd.to_datetime(report_date)

    # Find the latest PCAP date <= report date
    pcaps_for_lp = pcap[(pcap['LP Short Name'] == lp_short_name) & (pcap['PCAP Date'] <= report_date)]
    if pcaps_for_lp.empty:
        print("No PCAP data available for this LP before the report date.")
    pcap_report_date = pcaps_for_lp['PCAP Date'].max()

    # -------------------------------
    # LP Profile Info
    # -------------------------------
    lp_info = lp_lookup[lp_lookup['LP Short Name'] == lp_short_name][
        ["Status", "Source", "Effective Date", "Inactive Date"]
    ].fillna("N/A").to_dict(orient='records')[0]

    # -------------------------------
    # Fund Metadata for LP
    # -------------------------------
    fund_data = lp_fund[lp_fund['LP Short Name'] == lp_short_name][
        ["Reinvestment Start", "Harvest Start", "Management Fee", "Incentive Fee"]
    ].fillna("N/A").to_dict(orient='records')[0]

    # -------------------------------
    # Totals from Ledger (as of report date)
    # -------------------------------
    ledger_totals = ledger[
        (ledger['Related Entity'] == lp_short_name) &
        (ledger['Activity Date'] <= report_date)
    ]

    totals = {
        'Total Capital Called': ledger_totals[ledger_totals['Activity'] == 'Capital Call']['Amount'].sum(),
        'Total Capital Distribution': ledger_totals[ledger_totals['Sub Activity'] == 'Capital Distribution']['Amount'].sum(),
        'Total Income Distribution': ledger_totals[ledger_totals['Sub Activity'] == 'Income Distribution']['Amount'].sum(),
        'Total Commitment Amount': ledger_totals[ledger_totals['Activity'] == 'LP Commitment']['Amount'].sum()
    }

    # Add derived values
    totals['Total Distribution'] = totals['Total Capital Distribution'] + totals['Total Income Distribution']
    totals['Remaining Capital Investment'] = totals['Total Capital Called'] - totals['Total Capital Distribution']

    # -------------------------------
    # IRR Calculation using PCAP cashflows
    # -------------------------------
    cashflows = []
    q_dates = sorted(pcaps_for_lp['PCAP Date'].unique())
    ending_balance = 0

    for i, date in enumerate(q_dates):
        pcap_slice = pcaps_for_lp[pcaps_for_lp['PCAP Date'] == date]

        # For the last quarter, store ending balance
        if i == len(q_dates) - 1:
            ending_balance = pcap_slice[pcap_slice['Field'].str.contains('Ending Capital Balance')]['Amount'].sum()

        # First quarter: only capital calls are considered (negative cashflow)
        if i == 0:
            total_inflow = -pcap_slice[pcap_slice['Field'].str.contains('Capital Call')]['Amount'].sum()
        else:
            capital_call = pcap_slice[pcap_slice['Field'].str.contains('Capital Call')]['Amount'].sum()
            dist = pcap_slice[pcap_slice['Field'].str.contains('Distributions')]['Amount'].sum()
            total_inflow = -(capital_call + dist) + ending_balance  # Net cashflow

        cashflows.append(total_inflow)

    # Compute IRR using pyxirr (Excel-style XIRR)
    irr = None
    try:
        irr = xirr(q_dates, cashflows)
    except Exception as e:
        print(e)

    # -------------------------------
    # Return API Response
    # -------------------------------
    return jsonify({
        'lp_info': lp_info,
        'fund_data': fund_data,
        'totals': totals,
        'irr': irr,
        'report_date': report_date.strftime('%Y-%m-%d'),
        'pcap_report_date': pcap_report_date.strftime('%Y-%m-%d')
    })


# -------------------------------
# Run Flask App
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
