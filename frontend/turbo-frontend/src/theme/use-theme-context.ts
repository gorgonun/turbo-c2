import React from "react";
import { ThemeContext } from "./ThemeContextProvider";

export const useThemeContext = () => React.useContext(ThemeContext);
