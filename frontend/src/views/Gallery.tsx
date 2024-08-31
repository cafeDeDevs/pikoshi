import { createSignal, For, onMount, Show, type Component } from "solid-js";
import { useNavigate } from "@solidjs/router";
import { useAuthContext } from "../hooks/useAuthContext";

import Navbar from "../components/Navbar";

import urls from "../config/urls";
import { delay } from "../utils/utils";

import styles from "../css/Gallery.module.css";

// TODO: Figure out how to pass optional params (i.e. gallery/default)
// And Then pass this param "default" as an album_name to the backend
const Gallery: Component = () => {
    const [isAuthenticated, setIsAuthenticated] = createSignal<boolean>(false);
    const [images, setImages] = createSignal<string[]>([]);
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
            const jsonRes = await response.json();

            if (!response.ok)
                throw new Error(
                    "An Error Occurred While Trying To Retrieve Your Gallery",
                );

            const { imagesAsBase64 } = jsonRes;
            setImages(imagesAsBase64);
        } catch (err) {
            const error = err as Error;
            console.error("ERROR :=>", error.message);
        }
    });

    return (
        <>
            {/* TODO: Replace Loading... with GalleryLoading component */}
            <Show when={isAuthenticated()} fallback={<p>Loading...</p>}>
                <Navbar />
                <div class={styles.Gallery}>
                    {/* TODO: Replace Loading... with Default Image Component */}
                    <For each={images()} fallback={<p>Loading...</p>}>
                        {image => (
                            <img src={`data:image/jpg;base64,${image}`} />
                        )}
                    </For>
                </div>
            </Show>
        </>
    );
};

export default Gallery;
