import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Box,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Container
} from '@mui/material';

// Main App Component
export default function App() {
  // State: All LP options from backend
  const [lps, setLps] = useState([]);

  // State: Selected LP by user
  const [selectedLP, setSelectedLP] = useState('');

  // State: Report date (default to today)
  const [reportDate, setReportDate] = useState(new Date().toISOString().split('T')[0]);

  // State: Data returned from API for selected LP
  const [lpData, setLpData] = useState(null);

  // Fetch list of LPs on first render
  useEffect(() => {
    axios.get('http://localhost:5000/api/lps')
      .then(res => setLps(res.data));
  }, []);

  // Fetch LP data whenever selected LP or report date changes
  useEffect(() => {
    if (selectedLP) {
      axios.get(`http://localhost:5000/api/lp/${selectedLP}?report_date=${reportDate}`)
        .then(res => setLpData(res.data))
        .catch(err => console.error(err));
    }
  }, [selectedLP, reportDate]);

  // Helper function: Renders key-value data as an MUI table
  const renderTable = (data) => (
    <Table size="small">
      <TableBody>
        {Object.entries(data).map(([key, value]) => (
          <TableRow key={key}>
            <TableCell sx={{ fontWeight: 600 }}>{key}</TableCell>
            <TableCell>
              {typeof value === "number"
                ? `$${value.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}`
                : value}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 8 }}>
      {/* App Title */}
      <Typography variant="h4" gutterBottom>LP Investment Dashboard</Typography>

      {/* LP and Report Date Selection */}
      <Box display="flex" alignItems="center" gap={3} mb={4}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Select LP</InputLabel>
          <Select
            value={selectedLP}
            label="Select LP"
            onChange={(e) => setSelectedLP(e.target.value)}
          >
            {lps.map((lp) => (
              <MenuItem key={lp} value={lp}>
                {lp}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Report Date Picker */}
        <TextField
          label="Report Date"
          type="date"
          value={reportDate}
          onChange={(e) => setReportDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
          inputProps={{
            max: new Date().toISOString().split('T')[0] // Prevent future dates
          }}
        />
      </Box>

      {/* LP Data Output */}
      {lpData && (
        <>
          {/* LP Profile Info */}
          <Paper sx={{ p: 2, mb: 4 }}>
            <Typography variant="h6">LP Info</Typography>
            {renderTable(lpData.lp_info)}
          </Paper>

          {/* Fund Meta Info */}
          <Paper sx={{ p: 2, mb: 4 }}>
            <Typography variant="h6">Fund Data</Typography>
            {renderTable(lpData.fund_data)}
          </Paper>

          {/* Totals Calculated from Ledger */}
          <Paper sx={{ p: 2, mb: 4 }}>
            <Typography variant="h6">Totals</Typography>
            {renderTable(lpData.totals)}
          </Paper>

          {/* IRR + PCAP Date Display */}
          <Box display="flex" alignItems="center" gap={2} mt={4}>
            <Typography variant="h6">
              IRR:{" "}
              <span style={{ color: "#2e7d32" }}>
                {lpData.irr !== null ? (lpData.irr * 100).toFixed(2) + "%" : "N/A"}
              </span>
            </Typography>

            <Typography variant="body2" color="text.secondary">
              (as of PCAP Date: {lpData.pcap_report_date})
            </Typography>
          </Box>
        </>
      )}
    </Container>
  );
}
