import { createSignal, Show, type Component } from "solid-js";
import { useNavigate } from "@solidjs/router";

import urls from "../config/urls";
import { delay } from "../utils/utils";

import styles from "../css/ProfileCard.module.css";

const ProfileCard: Component = () => {
    const navigate = useNavigate();
    const [errorMsg, setErrorMsg] = createSignal<string>("");
    const [successMsg, setSuccessMsg] = createSignal<string>("");

    const logout = async () => {
        try {
            const response = await fetch(urls.BACKEND_AUTH_LOGOUT_ROUTE, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
                credentials: "include",
            });
            if (!response.ok) {
                const jsonRes = await response.json();
                throw new Error(jsonRes.message);
            }
            setSuccessMsg(
                "You Have Successfully Logged Out! \nRedirecting you back home!",
            );
            await delay(3000);
            navigate("/");
        } catch (err) {
            const error = err as Error;
            console.error("ERROR :=>", error);
            setErrorMsg(error.message);
        }
    };

    return (
        <>
            <div class={styles.ProfileCard}>
                <button
                    class={styles["logout-btn"]}
                    type='button'
                    onClick={logout}>
                    Logout
                </button>
            </div>
            {/* TODO: Display this in a modal component instead of rendering here */}
            <Show when={successMsg().length > 0}>
                <p>{successMsg()}</p>
            </Show>
            <Show when={errorMsg().length > 0}>
                <p>{errorMsg()}</p>
            </Show>
        </>
    );
};

export default ProfileCard;
