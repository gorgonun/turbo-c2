import humanizeDuration from 'humanize-duration';

const unitMapping = {
    milliseconds: 'ms',
    millisecond: 'ms',
    seconds: 's',
    second: 's',
    minutes: 'm',
    minute: 'm',
    hours: 'h',
    hour: 'h',
    days: 'd',
    day: 'd',
    weeks: 'w',
    week: 'w',
};

export const getHumanReadableTime = (timeMills: number) => {
    const duration = humanizeDuration(timeMills, { round: true, largest: 1});
    const parsedDuration = duration.split(' ')[0];
    const fullUnit = duration.split(' ')[1];
    const unit = unitMapping[fullUnit as keyof typeof unitMapping];

    return {
        "minimized": `${parsedDuration}${unit}`,
        "full": duration,
    }
}
