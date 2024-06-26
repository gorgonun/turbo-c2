import { PaletteMode, ThemeOptions } from "@mui/material";

const theme = {
  primary: {
    main: '#00bcd4',
    light: '#03a9f4',
    dark: '#0288d1',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#cddc39',
    light: '#d4e157',
    dark: '#afb42b',
    contrastText: '#000000',
  },
  background: {
    light: '#ffffff',
    dark: '#121212',
  },
  text: {
    primary: '#000000',
    secondary: '#ffffff',
  }
} as ThemeOptions;

export const getDesignTheme = (mode: PaletteMode) =>
  ({
    palette: {
      mode,
      theme,
    },
  } as ThemeOptions);
