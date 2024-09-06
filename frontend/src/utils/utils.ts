import { z } from "zod";
import Compressor from "compressorjs";

type Cookies = {
    [key: string]: string;
};

const delay = (ms: number): Promise<void> => {
    return new Promise(resolve => setTimeout(resolve, ms));
};

const grabStoredCookie = (cookieKey: string): string | undefined => {
    const cookies: Cookies = document.cookie
        .split("; ")
        .reduce((prev: Cookies, current) => {
            const [key, ...value] = current.split("=");
            prev[key] = value.join("=");
            return prev;
        }, {});
    const cookieVal = cookieKey in cookies ? cookies[cookieKey] : undefined;
    return cookieVal;
};

// TODO: Consider creating two or three different size formats here on the client
// for thumbnail/mobile/tablet view (this logic might still need to live on server though...)
const compressImage = (file: File): Promise<File> => {
    return new Promise((resolve, reject) => {
        new Compressor(file, {
            quality: 0.8,
            convertTypes: "image/webp",
            maxWidth: 1200,
            maxHeight: 800,
            minWidth: 300,
            minHeight: 300,
            success(result: Blob) {
                const compressedFile = new File(
                    [result],
                    file.name.replace(/\.[^/.]+$/, "") + ".webp",
                    { type: "image/webp" },
                );
                resolve(compressedFile);
            },
            error(err: Error) {
                reject(err);
            },
        });
    });
};

const compressFiles = async (files: File[]): Promise<FormData | void> => {
    const imageData = new FormData();
    for (const file of files) {
        try {
            const compressedFile = await compressImage(file);
            imageData.append("file", compressedFile, compressedFile.name);
            return imageData;
        } catch (err) {
            const error = err as Error;
            console.error("ERROR :=>", error.message);
        }
    }
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
        .join(""),
);

const passwordSchema = z
    .string()
    .regex(
        passwordSchemaRegex,
        "Password must be at least 10 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character.",
    );

const usernameSchema = z
    .string()
    .min(5, "Username must be at least 5 characters long.");

export {
    delay,
    compressFiles,
    compressImage,
    grabStoredCookie,
    passwordSchema,
    usernameSchema,
};
