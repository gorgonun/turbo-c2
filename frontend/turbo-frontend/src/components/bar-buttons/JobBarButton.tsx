import { IconButton } from "@mui/material"
import { JobIcon } from "../../theme/icons";

interface JobBarButtonProps {
    onClick: () => void;
}

const JobBarButton = ({ onClick }: JobBarButtonProps) => {
    return (
        <IconButton onClick={onClick}>
            <JobIcon />
        </IconButton>
    )
}

export default JobBarButton;
