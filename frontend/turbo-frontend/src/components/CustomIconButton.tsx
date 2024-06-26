import { IconButton } from "@mui/material"
import { ComponentProps } from "react";

type IconButtonProps = ComponentProps<typeof IconButton>;
interface CustomProps {
    icon: React.ReactNode;
}

const CustomIconButton = (props: IconButtonProps & CustomProps) => {
    const icon = props.icon;

    return (
        <IconButton {...props}>
            {icon}
        </IconButton>
    )
}

export default CustomIconButton;
