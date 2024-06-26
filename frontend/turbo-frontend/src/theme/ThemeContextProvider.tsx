import { Theme, createTheme } from '@mui/material'
import React, { PropsWithChildren } from 'react';
import { useColorTheme } from './use-color-theme';

type ThemeContextType = {
    mode: string;
    toggleMode: () => void;
    theme: Theme;
}

export const ThemeContext = React.createContext<ThemeContextType>({
    mode: 'light',
    toggleMode: () => {},
    theme: createTheme(),
})

export const ThemeContextProvider: React.FC<PropsWithChildren> = ({ children }) => {
    const value = useColorTheme();
    return (
        <ThemeContext.Provider value={value}>
            {children}
        </ThemeContext.Provider>
    )
}
