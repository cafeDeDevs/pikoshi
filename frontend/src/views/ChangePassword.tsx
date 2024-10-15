import { createSignal, onMount, Show, type Component } from "solid-js";
import { useLocation, useNavigate } from "@solidjs/router";
import { z } from "zod";

import urls from "../config/urls";
import { delay } from "../utils/utils";
import { validatePasswordInput } from "../utils/schema-validators";

import styles from "../css/AuthCard.module.css";

const ChangePassword: Component = () => {
    const location = useLocation();
    const navigate = useNavigate();

    const [checkTokenError, setCheckTokenError] = createSignal<string>("");
    const [success, setSuccess] = createSignal<string>("");
    const [error, setError] = createSignal<string>("");
    const [password, setPassword] = createSignal<string>("");
    const [confirmPassword, setConfirmPassword] = createSignal<string>("");

    const queryParams = new URLSearchParams(location.search);
    const token = queryParams.get("change_password_token");

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
                    body: JSON.stringify({ token }),
                });

                if (!response.ok) {
                    const jsonRes = await response.json();
                    throw new Error(jsonRes.message);
                }
            } catch (err) {
                const error = err as Error;
                console.error("ERROR :=>", error);
                setCheckTokenError(error.message);
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

        try {
            validatePasswordInput(password());
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

        if (password() !== confirmPassword()) {
            setError("Passwords do not match");
            throw new Error("Passwords do not match");
        }

        try {
            const res = await fetch(urls.BACKEND_FORGOT_PASSWORD_ROUTE, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({
                    password: password(),
                    token,
                }),
            });
            const jsonRes = await res.json();
            if (!res.ok) throw new Error(jsonRes.message || jsonRes.detail);
            setSuccess(jsonRes.message);
            await delay(3000);
            navigate("/login");
        } catch (err) {
            const error = err as Error;
            setError(error.message);
            throw new Error(error.message || "Unknown error");
        }
    };

    return (
        <div class={styles.AuthCard}>
            <Show when={checkTokenError().length == 0}>
                <h1>Reset Password</h1>
                <form onSubmit={handleSubmit}>
                    <div>
                        <label>New Password:</label>
                        <br />
                        <input
                            type="password"
                            value={password()}
                            placeholder="Enter new password"
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
                            placeholder="Confirm new password"
                            style="text-align: center;"
                            value={confirmPassword()}
                            onChange={e => setConfirmPassword(e.target.value)}
                            required
                        />
                    </div>
                    <br />
                    <button type="submit">Reset Password</button>
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

export default ChangePassword;
