import {
    createSignal,
    createEffect,
    For,
    Show,
    type Component,
} from "solid-js";

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
    const [error, setError] = createSignal<string>("");
    const [files, setFiles] = createSignal<File[]>([]);
    const [images, setImages] = createSignal<string[]>([]);
    let inputRef: HTMLInputElement | null = null;
    const [galleryUpdated, setGalleryUpdated] = createSignal<boolean>(false);

    const navigate = useNavigate();

    createEffect(async () => {
        const authContext = await useAuthContext();
        setIsAuthenticated(authContext);
        if (!isAuthenticated()) {
            await delay(3000);
            return navigate("/");
        }

        const grabGallery = async (): Promise<void> => {
            try {
                const response = await fetch(
                    urls.BACKEND_GALLERY_INITIAL_ROUTE,
                    {
                        method: "POST",
                        headers: {
                            Accept: "application/json",
                            "Content-Type": "application/json",
                        },
                        credentials: "include",
                    },
                );
                const jsonRes = await response.json();

                if (!response.ok)
                    throw new Error(
                        "An Error Occurred While Trying To Retrieve Your Gallery",
                    );

                const { imagesAsBase64 } = jsonRes;
                setImages(imagesAsBase64);
            } catch (err) {
                const error = err as Error;
                setError(error.message);
                throw new Error(error.message || "Unknown error");
            }
        };
        grabGallery();
    }, [galleryUpdated()]);

    createEffect(() => {
        if (files().length === 0) return;
        const imageData = new FormData();
        files().forEach((file, index) => {
            imageData.append(`file-${index}`, file, file.name);
        });
        const uploadImage = async (): Promise<void> => {
            try {
                const response = await fetch(
                    urls.BACKEND_GALLERY_UPLOAD_IMAGE_ROUTE,
                    {
                        method: "POST",
                        credentials: "include",
                        body: imageData,
                    },
                );
                const jsonRes = await response.json();
                if (!response.ok) {
                    throw new Error(jsonRes.message);
                }
                setGalleryUpdated(prev => !prev);
            } catch (err) {
                const error = err as Error;
                console.error("ERROR :=>", error.message);
                setError(error.message);
            }
        };
        uploadImage();
        setFiles([]);
    }, [files()]);

    const handleUploadClick = (): void => {
        if (inputRef !== null) {
            inputRef.click();
        }
    };

    const handleFileChange = (e: Event): void => {
        const target = e.target as HTMLInputElement;
        if (target.files) {
            setFiles([...files(), target.files[0]]);
        }
    };

    return (
        <>
            {/* TODO: Replace Loading... with GalleryLoading component */}
            <Show when={isAuthenticated()} fallback={<p>Loading...</p>}>
                <Navbar />
                <div class={styles["upload-form"]}>
                    <input
                        class={styles["file-picker"]}
                        type='file'
                        accept='image/*'
                        onChange={handleFileChange}
                        ref={el => (inputRef = el)}
                    />
                    <button class='upload-btn' onClick={handleUploadClick}>
                        Upload Image
                    </button>
                </div>
                <div class={styles.Gallery}>
                    {/* TODO: Replace Loading... with ImageLoading Component */}
                    <Show
                        when={images().length > 0}
                        fallback={<p>Loading...</p>}>
                        <For each={images()}>
                            {(image, index) => (
                                <img
                                    src={`data:image/jpg;base64,${image}`}
                                    alt={`Gallery Image ${index() + 1}`}
                                />
                            )}
                        </For>
                    </Show>
                    <Show when={error().length > 0}>
                        <p style='color: red;'>{error()}</p>
                    </Show>
                </div>
            </Show>
        </>
    );
};

export default Gallery;
