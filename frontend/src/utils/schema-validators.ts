import { z } from "zod";
import { passwordSchemaRegex, passwordSchemaErrMsg } from "../schemas/password";

const emailSchema = z.string().email();
const passwordSchema = z.string().regex(passwordSchemaRegex, {
    message: passwordSchemaErrMsg,
});

const validateEmailInput = (emailInput: string): void => {
    const zParsedEmail = emailSchema.safeParse(emailInput);
    /* NOTE: using !zparsedEmail.success conditional causes
     * TS error when referencing error */
    if (zParsedEmail.success === false) {
        const { error } = zParsedEmail;
        throw new Error(error.issues[0].message as string);
    }
};

const validatePasswordInput = (passwordInput: string): void => {
    const zParsedPassword = passwordSchema.safeParse(passwordInput);
    if (zParsedPassword.success === false) {
        const { error } = zParsedPassword;
        throw new Error(error.issues[0].message as string);
    }
};

const validateInputs = (emailInput: string, passwordInput: string): void => {
    validateEmailInput(emailInput);
    validatePasswordInput(passwordInput);
};

export { validateEmailInput, validatePasswordInput, validateInputs };
