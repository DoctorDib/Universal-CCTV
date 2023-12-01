import { Config } from "./ConfigContext";

export const FetchData = async (config: Config, url: string) => {
    if (config === null) {
        return {};
    }
    const builtUrl = BuildUrl(config, url);
    return await fetch(builtUrl).then(async (data) => {
        return await data.json();
    });
}

export const BuildUrl = (config: Config, additional: string) => {
    if (config === null) {
        return "";
    }

    console.log(config);

    const ip = config.ip;
    const port = config.port;
    return `http://${ip}:${port}${additional}`;
}