import { createSignal, onMount, Show, type Component } from "solid-js";
import { useLocation, useNavigate } from "@solidjs/router";
import { z } from "zod";

import urls from "../config/urls";
import { delay, usernameSchema } from "../utils/utils";
import { validatePasswordInput } from "../utils/schema-validators";

import styles from "../css/AuthCard.module.css";

const Onboarding: Component = () => {
    const location = useLocation();
    const navigate = useNavigate();

    const [checkHashError, setCheckHashError] = createSignal<string>("");
    const [success, setSuccess] = createSignal<string>("");
    const [error, setError] = createSignal<string>("");
    const [username, setUsername] = createSignal<string>("");
    const [password, setPassword] = createSignal<string>("");
    const [confirmPassword, setConfirmPassword] = createSignal<string>("");

    const queryParams = new URLSearchParams(location.search);
    const token = queryParams.get("token");

    onMount(() => {
        if (!token) navigate("/");
        (async () => {
            try {
                const response = await fetch(urls.BACKEND_CHECK_TOKEN_ROUTE, {
                    method: "POST",
                    headers: {
                        Accept: "application/json",
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ token: token }),
                });
                if (!response.ok) {
                    const jsonRes = await response.json();
                    throw new Error(jsonRes.message);
                }
            } catch (err) {
                const error = err as Error;
                console.error("ERROR :=>", error);
                setCheckHashError(error.message);
                await delay(3000);
                navigate("/");
                throw new Error(error.message);
            }
        })();
    });

    const handleSubmit = async (e: Event) => {
        e.preventDefault();
        setError("");
        setSuccess("");

        // TODO: establish a validateUsernameInput()
        // in utils/schema-validators.ts to replace this
        try {
            usernameSchema.parse(username());
        } catch (err) {
            if (err instanceof z.ZodError) {
                setError(err.errors[0].message);
                throw new Error(err.errors[0].message);
            } else {
                const error = err as Error;
                setError(error.message);
                throw new Error(error.message);
            }
        }

        validatePasswordInput(password());

        if (password() !== confirmPassword()) {
            setError("Passwords do not match");
            throw new Error("Passwords do not match");
        }

        try {
            const res = await fetch(urls.BACKEND_EMAIL_ONBOARDING_ROUTE, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({
                    username: username(),
                    password: password(),
                    token,
                }),
            });
            const jsonRes = await res.json();
            if (!res.ok) throw new Error(jsonRes.message || jsonRes.detail);
            setSuccess(jsonRes.message);
            await delay(3000);
            navigate("/gallery");
        } catch (err) {
            const error = err as Error;
            setError(error.message);
            throw new Error(error.message || "Unknown error");
        }
    };

    return (
        <div class={styles.AuthCard}>
            <Show when={checkHashError().length == 0}>
                <h1>Onboarding</h1>
                <form onSubmit={handleSubmit}>
                    <div>
                        <label>Username:</label>
                        <br />
                        <input
                            type="text"
                            placeholder="John Doe"
                            style="text-align: center;"
                            value={username()}
                            onChange={e => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    <div>
                        <label>Password:</label>
                        <br />
                        <input
                            type="password"
                            value={password()}
                            placeholder="Password1234!"
                            style="text-align: center;"
                            onChange={e => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <div>
                        <label>Confirm Password:</label>
                        <br />
                        <input
                            type="password"
                            placeholder="Password1234!"
                            style="text-align: center;"
                            value={confirmPassword()}
                            onChange={e => setConfirmPassword(e.target.value)}
                            required
                        />
                    </div>
                    <br />
                    <button type="submit">Complete Registration</button>
                </form>
            </Show>
            <Show when={error().length > 0}>
                <p style="color: red;">{error()}</p>
            </Show>
            <Show when={success().length > 0}>
                <p style="color: green;">{success()}</p>
            </Show>
        </div>
    );
};

export default Onboarding;
