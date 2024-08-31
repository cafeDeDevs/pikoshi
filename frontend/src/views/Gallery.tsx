import {
    createSignal,
    createEffect,
    onMount,
    Show,
    type Component,
} from "solid-js";
import { useNavigate } from "@solidjs/router";
import { useAuthContext } from "../hooks/useAuthContext";

import Navbar from "../components/Navbar";

import urls from "../config/urls";
import { delay } from "../utils/utils";

import styles from "../css/Gallery.module.css";

const Gallery: Component = () => {
    const [isAuthenticated, setIsAuthenticated] = createSignal(false);
    const navigate = useNavigate();

    onMount(async () => {
        const authContext = await useAuthContext();
        setIsAuthenticated(authContext);
        if (!isAuthenticated()) {
            await delay(3000);
            navigate("/");
        }
    });

    onMount(async () => {
        try {
            const response = await fetch(urls.BACKEND_GALLERY_INITIAL_ROUTE, {
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
        } catch (err) {
            const error = err as Error;
            console.error("ERROR :=>", error.message);
        }
    });

    return (
        <>
            {/* TODO: Replace Loading... with GalleryLoading component */}
            <Show when={isAuthenticated()} fallback={<p>Loading...</p>}>
                <div class={styles.Gallery}>
                    <Navbar />
                </div>
            </Show>
        </>
    );
};

export default Gallery;
