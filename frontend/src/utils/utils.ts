type Cookies = {
    [key: string]: string;
};

const delay = (ms: number): Promise<void> => {
    return new Promise(resolve => setTimeout(resolve, ms));
};

const grabStoredCookie = (cookieKey: string): string | undefined => {
    const cookies: Cookies = document.cookie
        .split('; ')
        .reduce((prev: Cookies, current) => {
            const [key, ...value] = current.split('=');
            prev[key] = value.join('=');
            return prev;
        }, {});
    const cookieVal = cookieKey in cookies ? cookies[cookieKey] : undefined;
    return cookieVal;
};

export { delay, grabStoredCookie };
