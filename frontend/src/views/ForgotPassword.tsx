import type { Component } from "solid-js";
import { createSignal } from "solid-js";

import styles from "../css/AuthCard.module.css";

const ForgotPassword: Component = () => {
    const [email, setEmail] = createSignal("");

    const handleSubmit = (e: Event) => {
        e.preventDefault();
        console.log("Email submitted for password reset:", email());
    };

    return (
        <div class={styles.AuthCard}>
            <h1>Forgot Password</h1>
            <form onSubmit={handleSubmit}>
                <label for="email">Enter your email:</label>
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
