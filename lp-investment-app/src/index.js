// index.js
import React from "react";
import { createRoot } from "react-dom/client";
import { ThemeProvider, CssBaseline } from "@mui/material";
import App from "App";
import theme from "./theme";

const root = createRoot(document.getElementById("app"));
// Render the application with theming and routing context
root.render(
  <ThemeProvider theme={theme}>
    <CssBaseline />
      <App />
  </ThemeProvider>
);
