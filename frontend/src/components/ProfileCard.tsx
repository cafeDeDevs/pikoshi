import { createSignal, Show, type Component } from "solid-js";
import { useNavigate } from "@solidjs/router";

import urls from "../config/urls";
import { delay } from "../utils/utils";
import {
    clearDB as clearDB1,
    deleteDatabase as deleteDatabase1,
} from "../utils/indexdb";
import {
    clearDB as clearDB2,
    deleteDatabase as deleteDatabase2,
} from "../utils/indexdb-views";

import styles from "../css/ProfileCard.module.css";

import { useModalContext } from "../contexts/ModalContext";

const ProfileCard: Component = () => {
    const navigate = useNavigate();

    const { openLogoutModal } = useModalContext();

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
                throw new Error(jsonRes.message || jsonRes.detail);
            }
            await clearDB1();
            await clearDB2();
            await deleteDatabase1();
            await deleteDatabase2();

            openLogoutModal();
            await delay(3000);
            navigate("/");
        } catch (err) {
            const error = err as Error;
            console.error("ERROR :=>", error);
        }
    };

    return (
        <>
            <div class={styles.ProfileCard}>
                <button
                    class={styles["logout-btn"]}
                    type="button"
                    onClick={logout}>
                    Logout
                </button>
            </div>
            {/* TODO: Display this in a modal component instead of rendering here */}
        </>
    );
};

export default ProfileCard;
