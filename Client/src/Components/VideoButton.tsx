import { useEffect, useState } from "react";
import './VideoButton.scss';
import classNames from "classnames";
import { IoIosArrowForward , IoIosArrowDown } from 'react-icons/io';
import { FileInfo } from "../Resources/interfaces";

type DateTimeMap = { [key: string]: { formattedDateTime: string[][], originalData: FileInfo[] } };

interface DataTest {
    data: Array<FileInfo>,
    selectedVideo: FileInfo,
    setSelectedVideo: (fileInfo: FileInfo) => void,
}

const VideoButtonComponent = ({ data, selectedVideo, setSelectedVideo, }: DataTest) => {    
    const [element, setElement] = useState<DateTimeMap>({});
    const [collapsedDates, setCollapsedDates] = useState<string[]>([]);

    const generateDateTimeMap = (data: Array<FileInfo>): DateTimeMap => {
        const dateTimeMap: DateTimeMap = {};

        data.forEach((item: FileInfo) => {
            const [date, time] = item.file_name.split('_');
            const formattedDate = date.replace(/-/g, '');
            let formattedTime = time.replace(/-/g, ':'); //.replace('.mp4', '');
            formattedTime = formattedTime.replace(/-/g, ':').replace('.jpeg', '');

            if (!dateTimeMap[formattedDate]) {
                dateTimeMap[formattedDate] = { formattedDateTime: [], originalData: [] };
            }
    
            dateTimeMap[formattedDate].formattedDateTime.unshift(item.file_name.split('_'));
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
            {Object.keys(element).reverse().map((date, dateIndex) => {
                return (
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
                            const originalDate = element[date].originalData[index].file_name;

                            return (
                                <div key={element[date].originalData[index]?.uid} className={classNames('time-button', selectedVideo?.file_name === originalDate ? 'selected' : '')} onClick={() => setSelectedVideo(element[date].originalData[index])}>
                                    <div className={'time'}> {time[1].split('-').join(':')} </div>
                                    <div className={'format'}> {element[date].originalData[index].format} </div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )})}
        </div>
    );
};

export default VideoButtonComponent;
