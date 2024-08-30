import { createSignal, Show, type Component } from "solid-js";
import { useNavigate } from "@solidjs/router";

import urls from "../config/urls";
import {
    validateEmailInput,
    validatePasswordInput,
} from "../utils/schema-validators";
import { delay } from "../utils/utils";

const EmailLogin: Component = () => {
    const [email, setEmail] = createSignal<string>("");
    const [password, setPassword] = createSignal<string>("");
    const [message, setMessage] = createSignal<string>("");

    const navigate = useNavigate();

    const handleSubmit = async (e: Event) => {
        e.preventDefault();
        try {
            validateEmailInput(email());
            validatePasswordInput(password());
            const res = await fetch(urls.BACKEND_EMAIL_LOGIN_ROUTE, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({ email: email(), password: password() }),
            });
            if (!res.ok) {
                const jsonRes = await res.json();
                throw new Error(jsonRes.message);
            } else {
                const jsonRes = await res.json();
                setMessage(jsonRes.message);
                await delay(3000);
                navigate("/gallery");
            }
        } catch (err) {
            const error = err as Error;
            console.error("ERROR :=>", error.message);
            setMessage(error.message);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <div>
                    <label for='email-form'>email:</label>
                    <br />
                    <input
                        type='email'
                        id='email-form'
                        placeholder='johndoe@example.com'
                        style='text-align: center;'
                        value={email()}
                        onChange={e => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>password:</label>
                    <br />
                    <input
                        type='password'
                        value={password()}
                        placeholder='Password1234!'
                        style='text-align: center;'
                        onChange={e => setPassword(e.target.value)}
                        required
                    />
                </div>
                <br />
                <button type='submit'>Continue</button>
            </form>
            <Show when={message().length}>
                <p>{message()}</p>
            </Show>
        </div>
    );
};

export default EmailLogin;
