import { PaletteMode, createTheme } from "@mui/material";
import React from "react";
import { getDesignTheme } from "./theme";

export const useColorTheme = () => {
  const [mode, setMode] = React.useState<PaletteMode>("light");

  const toggleMode = () => {
    setMode(mode === "light" ? "dark" : "light");
  };

  const modifiedTheme = React.useMemo(
    () => createTheme(getDesignTheme(mode)),
    [mode]
  );

  return { theme: modifiedTheme, mode, toggleMode };
};
