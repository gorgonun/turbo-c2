interface Position {
    x: number;
    y: number;
}

export function calculateElementPosition(elements: Position[]): Position {
    let minX = Number.POSITIVE_INFINITY;
    let maxX = Number.NEGATIVE_INFINITY;
    let minY = Number.POSITIVE_INFINITY;
    let maxY = Number.NEGATIVE_INFINITY;

    // Find the minimum and maximum x and y coordinates
    elements.forEach(element => {
        minX = Math.min(minX, element.x);
        maxX = Math.max(maxX, element.x);
        minY = Math.min(minY, element.y);
        maxY = Math.max(maxY, element.y);
    });

    // Calculate the position (x, y) as the midpoint of the bounding box
    const x = (minX + maxX) / 2;
    const y = (minY + maxY) / 2;

    return { x, y };
}
