// import './App.css'
import "reactflow/dist/style.css";
import { CssBaseline, ThemeProvider } from "@mui/material";
import Home from "./components/Home";
import { useThemeContext } from "./theme/use-theme-context";

function App() {
  const { theme } = useThemeContext();

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Home />
    </ThemeProvider>
  );
}

export default App;
