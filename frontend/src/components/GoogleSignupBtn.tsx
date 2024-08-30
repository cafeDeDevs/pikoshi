import { createSignal, Show, type Component } from "solid-js";
import useGoogleLogin from "../hooks/useGoogleLogin";
import { useNavigate } from "@solidjs/router";

import urls from "../config/urls";

const GoogleSignupBtn: Component = () => {
    const [message, setMessage] = createSignal<string>("");
    const navigate = useNavigate();

    const signup = useGoogleLogin({
        onSuccess: async (codeResponse): Promise<void> => {
            try {
                const response = await fetch(urls.BACKEND_SIGNUP_GOOGLE_ROUTE, {
                    method: "POST",
                    headers: {
                        Accept: "application/json",
                        "Content-Type": "application/json",
                    },
                    credentials: "include",
                    body: JSON.stringify({
                        code: codeResponse.code,
                    }),
                });
                const jsonRes = await response.json();
                setMessage(jsonRes.message);
                if (!response.ok)
                    throw new Error("Error While Authenticating.");
                navigate("/gallery");
            } catch (err) {
                const error = err as Error;
                console.error("ERROR :=>", error);
            }
        },
        onError: errorResponse => {
            console.error("Error :=>", errorResponse);
        },
        flow: "auth-code", // change to 'implicit' for access_token
    });

    return (
        <>
            <button onClick={signup}>Google</button>
            <Show when={message().length}>
                <p>{message()}</p>
            </Show>
        </>
    );
};

export default GoogleSignupBtn;
