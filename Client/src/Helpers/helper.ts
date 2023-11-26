import dotenv from 'dotenv';
dotenv.config();

export const BuildUrl = (additional: string = "") => {
    const ip = process.env.IP;
    const port = process.env.PORT;
    return `http://${ip}:${port}/${additional}`;
};