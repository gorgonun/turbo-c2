import { useQuery } from "react-query"
import { getJobs } from "../../api/turbo-api"
import { Box, Stack } from "@mui/material";

const JobModal = () => {
    const { data, status } = useQuery('jobs', getJobs);

    if (status === 'loading') {
        return <div>Loading...</div>
    }

    if (status === 'error') {
        return <div>Error fetching jobs</div>
    }

    if (status === 'success') {
        return (
            <Stack>
                {data.map(job => (
                    <Box key={job}>job</Box>
                ))}
            </Stack>
        )
    }
}

export default JobModal;
