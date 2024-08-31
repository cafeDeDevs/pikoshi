import {
    createSignal,
    createEffect,
    For,
    Show,
    type Component,
} from "solid-js";

import { useNavigate } from "@solidjs/router";
import { useAuthContext } from "../hooks/useAuthContext";
import { useGrabGallery } from "../hooks/useGrabGallery";

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
    const [galleryUpdated, setGalleryUpdated] = createSignal<boolean>(false);

    let inputRef: HTMLInputElement | null = null;

    const navigate = useNavigate();

    createEffect(async () => {
        const authContext = await useAuthContext();
        setIsAuthenticated(authContext);
        if (!isAuthenticated()) {
            await delay(3000);
            return navigate("/");
        }
        const imagesAsBase64 = await useGrabGallery();
        if (imagesAsBase64) {
            setImages(imagesAsBase64);
        } else {
            setError(imagesAsBase64);
        }
    });

    createEffect(async () => {
        if (files().length === 0) return;
        const imageData = new FormData();
        files().forEach(file => {
            imageData.append("file", file, file.name);
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
        await uploadImage();
        setFiles([]);
    });

    createEffect(async () => {
        if (galleryUpdated()) {
            const imagesAsBase64 = await useGrabGallery();
            if (imagesAsBase64) {
                setImages(imagesAsBase64);
            } else {
                setError(imagesAsBase64);
            }
        }
    });

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
