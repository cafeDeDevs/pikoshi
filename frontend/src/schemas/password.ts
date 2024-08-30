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
const passwordSchemaErrMsg =
    "Password must be at least 10 characters in length and contain at \
                least one lowercase letter, one uppercase letter, one digit, and one \
                special character";

export { passwordSchemaRegex, passwordSchemaErrMsg };
