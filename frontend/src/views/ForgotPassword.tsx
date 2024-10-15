import type { Component } from "solid-js";
import { createSignal } from "solid-js";
import { validateEmailInput } from "../utils/schema-validators";
import urls from "../config/urls";

import styles from "../css/AuthCard.module.css";

const ForgotPassword: Component = () => {
    const [email, setEmail] = createSignal("");

    const handleSubmit = async (e: Event) => {
        e.preventDefault();
        try {
            validateEmailInput(email());
            console.log("Submitting email:", email()); // Log the submitted email

            const res = await fetch(urls.BACKEND_FORGOT_PASSWORD_ROUTE, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email: email() }),
            });

            const jsonRes = await res.json();
            console.log("Backend response:", jsonRes); // Log the backend response

            if (!res.ok) {
                throw new Error(jsonRes.message || jsonRes.detail);
            } else {
                console.log("Email submission successful:", jsonRes.message);
                // setMessage(jsonRes.message);  // Handle success messages
            }
        } catch (err) {
            const error = err as Error;
            console.error("Error during email submission:", error.message);
            // setMessage(error.message);  // Handle error messages
        }
    };

    // const handleSubmit = async (e: Event) => {
    //     e.preventDefault();
    //     try {
    //         validateEmailInput(email());
    //         const res = await fetch(urls.BACKEND_FORGOT_PASSWORD_ROUTE, {
    //             method: "POST",
    //             headers: {
    //                 "Content-Type": "application/json",
    //             },
    //             body: JSON.stringify({ email: email() }),
    //         });
    //         const jsonRes = await res.json();
    //         if (!res.ok) {
    //             throw new Error(jsonRes.message || jsonRes.detail);
    //         } else {
    //             // TODO: SET ACTUAL MESSAGES HERE
    //             console.log(jsonRes.message);

    //             // setMessage(jsonRes.message);
    //         }
    //     } catch (err) {
    //         const error = err as Error;
    //         // console.error("ERROR :=>", error.message);
    //         // setMessage(error.message);
    //     }
    // };

    // const handleSubmit = (e: Event) => {
    //     e.preventDefault();
    //     console.log("Email submitted for password reset:", email());
    // };

    return (
        <div class={styles.AuthCard}>
            <h1>Forgot Password</h1>
            <form onSubmit={handleSubmit}>
                <label for="email">Enter your email:</label>
                <br />
                <input
                    type="email"
                    id="email"
                    value={email()}
                    onInput={e => setEmail(e.currentTarget.value)}
                    required
                />
                <br />
                <button type="submit">Submit</button>
            </form>
            <br />
            <a href="/login">Back to Login</a>
        </div>
    );
};

export default ForgotPassword;
