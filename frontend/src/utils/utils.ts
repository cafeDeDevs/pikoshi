import { z } from 'zod';
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
const passwordSchemaRegex = new RegExp(
    [
        /^(?=.*[a-z])/, // At least one lowercase letter
        /(?=.*[A-Z])/, // At least one uppercase letter
        /(?=.*\d)/, // At least one digit
        /(?=.*[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?])/, // At least one special character
        /[A-Za-z\d!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]{10,}$/, // At least 10 characters long
    ]
        .map(r => r.source)
        .join(''),
);

const passwordSchema = z
    .string()
    .regex(
        passwordSchemaRegex,
        'Password must be at least 10 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character.',
    );

const usernameSchema = z
    .string()
    .min(5, 'Username must be at least 5 characters long.');

export { grabStoredCookie, delay, passwordSchema, usernameSchema };
