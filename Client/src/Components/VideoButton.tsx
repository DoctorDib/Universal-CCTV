import { useEffect, useState } from "react";
import './VideoButton.scss';
import classNames from "classnames";
import { IoIosArrowForward , IoIosArrowDown } from 'react-icons/io';

type DateTimeMap = { [key: string]: { formattedDateTime: string[], originalData: string[] } };

interface DataTest {
    data: string[],
    selectedVideo: string,
    setSelectedVideo: (date: string) => void,
}

type DateObject = {
    [date: string]: any;
  };

const VideoButtonComponent = ({ data, selectedVideo, setSelectedVideo, }: DataTest) => {    
    const [element, setElement] = useState<DateTimeMap>({});
    const [collapsedDates, setCollapsedDates] = useState<string[]>([]);

    const generateDateTimeMap = (data: string[]): DateTimeMap => {
        const dateTimeMap: DateTimeMap = {};
    
        data.forEach((item) => {
            // TODO - Find a better way...
            if (item === 'saved') {
                return;
            }

            const [date, time] = item.split('_');
            const formattedDate = date.replace(/-/g, '');
            let formattedTime = time.replace(/-/g, ':').replace('.mp4', '');
            formattedTime = formattedTime.replace(/-/g, ':').replace('.jpeg', '');
    
            if (!dateTimeMap[formattedDate]) {
                dateTimeMap[formattedDate] = { formattedDateTime: [], originalData: [] };
            }
    
            dateTimeMap[formattedDate].formattedDateTime.unshift(formattedTime);
            dateTimeMap[formattedDate].originalData.unshift(item);
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
            {Object.keys(element).reverse().map((date, dateIndex) => (
                <div key={date} className={'date-container'}>
                    <button
                        className={'date-button'}
                        onClick={() => toggleCollapse(date)}
                        aria-expanded={!collapsedDates.includes(date)}
                    >
                        <div className={'info-container'}>
                            <div className={'count'}> 
                                { element[date].formattedDateTime.length } 
                            </div>
                            <div className={'title'}>
                                {formatDateString(date)}
                            </div>
                        </div>

                        <div>
                            {!collapsedDates.includes(date) ? <IoIosArrowForward /> : <IoIosArrowDown/>}
                        </div>
                    </button>
                    <div id={date} className={classNames('time-button-container', !collapsedDates.includes(date) ? 'collapse' : '')}>
                        {element[date].formattedDateTime.map((time, index) => {
                            const originalDate = element[date].originalData[index];
                            return (
                                <div key={data[dateIndex + index]} className={classNames('time-button', selectedVideo === originalDate ? 'selected' : '')} onClick={() => setSelectedVideo(originalDate)}>
                                    {time}
                                </div>
                            )
                        })}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default VideoButtonComponent;
