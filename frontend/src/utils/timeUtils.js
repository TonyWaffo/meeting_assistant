
// Format timer as mm:ss
export const formatTime = (timeInSeconds) => {
    const hours= Math.floor(timeInSeconds / 3600);
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = timeInSeconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
};

