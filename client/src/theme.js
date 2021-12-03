import { createTheme, responsiveFontSizes } from "@mui/material/styles";

let theme = createTheme({
  palette: {
    primary: {
      main: "#50bf9f",
    },
    secondary: {
      main: "#163652",
    },
  },
  components: {
    MuiChip: {
      styleOverrides: {
        root: {
          // apply theme's border-radius instead of component's default
          borderRadius: "16px",
        },
      },
    },
  },
});
theme = responsiveFontSizes(theme);
export default theme;
