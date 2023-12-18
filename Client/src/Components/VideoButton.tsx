import { useEffect, useState } from "react";
import './VideoButton.scss';
import classNames from "classnames";
import { IoIosArrowForward , IoIosArrowDown } from 'react-icons/io';

type DateTimeMap = { [key: string]: string[] };

interface DataTest { 
    data: string[],
    selectedVideo: string,
    setSelectedVideo: (date: string) => void,
}

const VideoButtonComponent = ({ data, selectedVideo, setSelectedVideo, }: DataTest) => {    
    const [element, setElement] = useState<DateTimeMap>({});
    const [collapsedDates, setCollapsedDates] = useState<string[]>([]);

    const generateDateTimeMap = (data: string[]) => {
        const dateTimeMap: { [key: string]: string[] } = {};
      
        data.forEach((item) => {
            const [date, time] = item.split('_');
            const formattedDate = date.replace(/-/g, '');
            const formattedTime = time.replace(/-/g, ':').replace('.mp4', '');
        
            if (!dateTimeMap[formattedDate]) {
                dateTimeMap[formattedDate] = [];
            }
        
            dateTimeMap[formattedDate].push(formattedTime);
        });
      
        return dateTimeMap;
    };

    useEffect(() => setElement(generateDateTimeMap(data)), [data]);

    const formatDateString = (date: string): string => `${date.slice(6, 8)}-${date.slice(4, 6)}-${date.slice(0, 4)}`;
  
    const toggleCollapse = (date: string) => {
        setCollapsedDates((prevCollapsedDates) =>
            prevCollapsedDates.includes(date)
                ? prevCollapsedDates.filter((collapsedDate) => collapsedDate !== date)
                : [...prevCollapsedDates, date]
        );
    };

    return (
        <div className={'container'}>
            {Object.keys(element).map((date, index) => (
                <div key={date} className={'date-container'}>
                    <button
                        className={'date-button'}
                        onClick={() => toggleCollapse(date)}
                        aria-expanded={!collapsedDates.includes(date)}
                    >
                        {formatDateString(date)}

                        <div>
                            {!collapsedDates.includes(date) ? <IoIosArrowForward /> : <IoIosArrowDown/>}
                        </div>
                    </button>
                    <div id={date} className={classNames('time-button-container', !collapsedDates.includes(date) ? 'collapse' : '')}>
                        {element[date].map((time, index) => (
                            <div key={index} className={classNames('time-button', data[index] == selectedVideo ? 'selected' : '')} onClick={() => setSelectedVideo(data[index])}>
                                {time}
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default VideoButtonComponent;
