import { Box, IconButton } from "@mui/material";
import { useThemeContext } from "../theme/use-theme-context";

const ColorModeToggle = () => {
    const { mode, toggleMode } = useThemeContext();

    return (
        <Box>
            <IconButton onClick={toggleMode}>
               {mode === 'light' ? '🌙' : '☀️'} 
            </IconButton>
        </Box>
    );
};

export default ColorModeToggle;
