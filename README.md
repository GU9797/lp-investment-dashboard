# lp-investment-dashboard

LP Investment Dashboard
https://github.com/GU9797/lp-investment-dashboard
---

## Notes

- The LP descriptive info was taken from the LPLookup file
- The information about the LP investment in each fund was taken from the LPFund file
- Total calculations were made using the Ledger File, using the Activity/SubActivity fields to group and sum
- IRR was calculated using the PCAP file and pyxirr library: '-Capital_Call_1, Distribution_2 - Capital Call_2, ... Distribution_n - Capital_Call_n + Ending_Balance'
- Assumed that 'as totals across all funds for each LP' means NOT for each fund, but for all funds aggregated for that LP. 
---

## Transparency on Figure and Data

Given that each group of calculations was made discretely on each file, could put a file download button next to each calculation group so that people can see the actual data.
If the size of the file is too large, can filter the file to only contain info for the selected LP and report date. Additionally could have another dashboard tab containing
tabular data that people could view. Could also build collapsible frontend conponents showing the underlying dates/amounts for each calculation. 

---

## Data Storage and Input/Update Mechanisms
So far, this data can be easily managed with a relational database. If additional data needs to be entered, could have an input form in the dashboard for quarterly entries on calls
/distribution etc. Could also display recent rows in a tabular tab that people can edit, paginated in chunks. Also could setup automated ETL jobs that pull from sources to update the database.

---

## Tech Stack
- Backend: Flask
- Frontend: React
